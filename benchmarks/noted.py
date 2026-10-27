#!/usr/bin/env python3
"""noted's speed, as noted.computer and the User's Guide state it: the release build in a pseudo-terminal, timed
from a key to the frame noted writes back, with a low-priority busy loop keeping the processor awake (on an idle
Mac, macOS takes about 5 ms longer to start any program).

    python3 bench/noted.py target/release/noted                      # 1,000 and 10,000 notes, and a long note
    python3 bench/noted.py 1.0.0=old/noted next=target/release/noted # builds side by side, by label
    python3 bench/noted.py --notes 1000 --passes 2 --json out.json noted

For each build and folder size: launch to the first full frame (20 launches after a warm-up), memory (physical
footprint, as Activity Monitor shows it), opening the next note (20 keys), a typed key (40), finding (each key of
three queries), and a key typed at the end and the start of a 30,000-line note. Medians. With --passes 2 or more,
the builds take turns going first. Notes are made up, about 1.5 KB each, under a temporary folder; nothing of
yours is read or changed. Standard library only.
"""
import argparse, ctypes, fcntl, json, os, pty, random, select, shutil, statistics, struct, subprocess, sys
import tempfile, termios, time

FRAME = b"\x1b[?2026l"  # the end of each synchronized frame noted writes
WORDS = ("meeting groceries project idea plan budget travel lisbon recipe book notes weekly review design rust "
         "terminal coffee garden music family health run journal todo call email draft launch research kitchen "
         "paper window river stone light market winter letter garden ticket station museum harbor lantern violin "
         "bakery").split()
QUERIES = ["lantern", "harbor lantern", "xylophone"]
LONG = "Some ordinary words.\n" * 30_000


def make_notes(folder, n, seed=7):
    os.makedirs(folder)
    rnd, now = random.Random(seed), time.time()
    for i in range(n):
        title = f"{rnd.choice(WORDS).title()} {rnd.choice(WORDS)} {i}"
        lines = [f"# {title}", ""]
        while sum(len(line) + 1 for line in lines) < 1500:
            kind = rnd.random()
            if kind < 0.15: lines.append(f"## {rnd.choice(WORDS).title()} {rnd.choice(WORDS)}")
            elif kind < 0.35: lines.append(f"- [ ] {rnd.choice(WORDS)} the {rnd.choice(WORDS)}")
            elif kind < 0.5: lines.append(f"- **{rnd.choice(WORDS)}** and *{rnd.choice(WORDS)}*")
            else: lines.append(" ".join(rnd.choice(WORDS) for _ in range(14)) + ".")
        path = os.path.join(folder, title + ".md")
        with open(path, "w") as f: f.write("\n".join(lines) + "\n")
        t = now - 60 * (i + 1)
        os.utime(path, (t, t))


def footprint_mb(pid):
    """Physical footprint (macOS), else resident memory (Linux), in MB."""
    try:
        info = (ctypes.c_uint64 * 64)()
        if ctypes.CDLL("/usr/lib/libproc.dylib").proc_pid_rusage(pid, 2, ctypes.byref(info)) == 0:
            return info[9] / 2**20
    except OSError:
        pass
    try:
        with open(f"/proc/{pid}/status") as f:
            return next(int(l.split()[1]) for l in f if l.startswith("VmRSS:")) / 1024
    except OSError:
        return None


class Noted:
    def __init__(self, binary, folder, home):
        self.fd, tty = pty.openpty()
        fcntl.ioctl(tty, termios.TIOCSWINSZ, struct.pack("HHHH", 40, 120, 0, 0))
        env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, ".config"),
                   XDG_CACHE_HOME=os.path.join(home, ".cache"), TERM="xterm-256color", COLORTERM="truecolor")
        env.pop("NOTED_DIR", None)
        dup = [(os.POSIX_SPAWN_DUP2, tty, 0), (os.POSIX_SPAWN_DUP2, tty, 1), (os.POSIX_SPAWN_DUP2, tty, 2)]
        self.started = time.perf_counter()
        self.pid = os.posix_spawn(binary, [binary, "--dir", folder], env, file_actions=dup, setsid=True)
        os.close(tty)
        self.buf = b""

    def frame(self, timeout=5):
        end = time.monotonic() + timeout
        while FRAME not in self.buf:
            if not select.select([self.fd], [], [], max(0, end - time.monotonic()))[0]:
                raise TimeoutError("noted drew no frame")
            self.buf += os.read(self.fd, 1 << 16)
        at = time.perf_counter()
        self.buf = self.buf[self.buf.index(FRAME) + len(FRAME):]
        return at

    def drain(self, secs):
        end = time.monotonic() + secs
        while (left := end - time.monotonic()) > 0:
            if select.select([self.fd], [], [], left)[0]:
                try: os.read(self.fd, 1 << 16)
                except OSError: break
        self.buf = b""

    def key(self, data):
        """Milliseconds from writing the key to noted's frame."""
        self.drain(0)
        t = time.perf_counter()
        os.write(self.fd, data)
        return (self.frame() - t) * 1000

    def quit(self):
        os.write(self.fd, b"\x11")
        for _ in range(500):
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                break
            self.drain(0.01)
        else:
            os.kill(self.pid, 9)
            os.waitpid(self.pid, 0)
            status = -1
        os.close(self.fd)
        if status:
            raise RuntimeError(f"noted exited with status {status}")


def notes_bench(binary, folder, home):
    out = {}
    launches = []
    for run in range(21):
        n = Noted(binary, folder, home)
        at = n.frame()
        n.drain(0.3)
        n.quit()
        if run:
            launches.append((at - n.started) * 1000)
        time.sleep(0.3)
    out["launch ms"] = launches
    n = Noted(binary, folder, home)
    try:
        n.frame()
        n.drain(2.0)
        out["memory MB"] = [footprint_mb(n.pid)]
        n.key(b"\x1b")
        out["open a note ms"] = [n.key(b"\x1b[B") for _ in range(20)]
        n.key(b"\r")
        n.key(b"\x1b[1;5F")
        typed = []
        for _ in range(40):
            typed.append(n.key(b"k"))
            time.sleep(0.03)
        out["type a key ms"] = typed
        n.drain(1.0)
        found = []
        for q in QUERIES:
            n.key(b"\x06")
            found += [n.key(c.encode()) for c in q]
            n.key(b"\x1b")
            n.drain(0.3)
        out["find, each key ms"] = found
    finally:
        n.quit()
    return out


def long_note_bench(binary, root, trials=4):
    ends, starts = [], []
    for trial in range(trials):
        folder, home = os.path.join(root, f"long-{trial}"), os.path.join(root, f"home-long-{trial}")
        os.makedirs(folder)
        os.makedirs(home)
        with open(os.path.join(folder, "Profile.md"), "w") as f: f.write("Profile\n" + LONG)
        n = Noted(binary, folder, home)
        try:
            n.frame()
            n.drain(0.5)
            for k in (b"\x06", b"Profile", b"\r", b"\x1b[1;5F"):
                n.key(k)
            ends += [n.key(bytes([c])) for c in b"abcdefghij"]
            for k in (b"\x1b[1;5H", b"\x1b[B", b"\x1b[H"):
                n.key(k)
            starts += [n.key(bytes([c])) for c in b"klmnopqrst"]
        finally:
            n.quit()
        with open(os.path.join(folder, "Profile.md")) as f:
            if f.read() != "Profile\nklmnopqrst" + LONG + "abcdefghij":
                raise RuntimeError("the long note didn't end up as typed: the benchmark's keys need a look")
    return {"30,000-line note, type at the end ms": ends, "30,000-line note, type at the start ms": starts}


def busy_loop():
    """One low-priority busy loop, so the processor stays awake as it was when the site was measured."""
    return subprocess.Popen(["nice", "-n", "20", sys.executable, "-c", "while True: pass"])


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("builds", nargs="+", help="path to noted, or label=path")
    p.add_argument("--notes", default="1000,10000", help="folder sizes, comma-separated (default 1000,10000)")
    p.add_argument("--passes", type=int, default=1, help="runs of every build; they take turns going first")
    p.add_argument("--no-long", action="store_true", help="skip the 30,000-line note")
    p.add_argument("--asleep", action="store_true", help="no busy loop keeping the processor awake")
    p.add_argument("--json", help="also write every sample to this file")
    a = p.parse_args()
    builds = [tuple(b.split("=", 1)) if "=" in b else (os.path.basename(os.path.dirname(os.path.abspath(b))) or b, b)
              for b in a.builds]
    for _, path in builds:
        if not os.access(path, os.X_OK): sys.exit(f"bench: {path} isn't an executable noted")
    sizes = [int(s) for s in a.notes.split(",") if s]

    loop = None if a.asleep else busy_loop()
    root = tempfile.mkdtemp(prefix="noted-bench-")
    samples = {}
    try:
        print(f"load averages {' '.join(f'{x:.1f}' for x in os.getloadavg())}", file=sys.stderr)
        for size in sizes:
            made = os.path.join(root, f"notes-{size}")
            make_notes(made, size)
            for p_ in range(a.passes):
                for label, path in (builds if p_ % 2 == 0 else builds[::-1]):
                    print(f"  {label}: {size:,} notes, pass {p_ + 1}", file=sys.stderr)
                    # A copy of its own: typing changes a note.
                    run = os.path.join(root, f"run-{label}-{size}-{p_}")
                    shutil.copytree(made, os.path.join(run, "notes"))
                    os.makedirs(os.path.join(run, "home"))
                    for name, values in notes_bench(path, os.path.join(run, "notes"), os.path.join(run, "home")).items():
                        samples.setdefault(label, {}).setdefault(f"{size:,} notes: {name}", []).extend(values)
        if not a.no_long:
            for p_ in range(a.passes):
                for label, path in (builds if p_ % 2 == 0 else builds[::-1]):
                    print(f"  {label}: a 30,000-line note, pass {p_ + 1}", file=sys.stderr)
                    sub = tempfile.mkdtemp(dir=root)
                    for name, values in long_note_bench(path, sub).items():
                        samples.setdefault(label, {}).setdefault(name, []).extend(values)
        print(f"load averages {' '.join(f'{x:.1f}' for x in os.getloadavg())}", file=sys.stderr)
    finally:
        if loop:
            loop.kill()
            loop.wait()
        shutil.rmtree(root, ignore_errors=True)

    names = list(next(iter(samples.values())))
    labels = [label for label, _ in builds if label in samples]
    width = max(len(n) for n in names)
    print(f"{'median':{width}}  " + "  ".join(f"{label:>12}" for label in labels))
    for name in names:
        cells = []
        for label in labels:
            values = [v for v in samples[label].get(name, []) if v is not None]
            cells.append(f"{statistics.median(values):12.3f}" if values else f"{'n/a':>12}")
        print(f"{name:{width}}  " + "  ".join(cells))
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"load": os.getloadavg(), "samples": samples}, f, indent=1)


if __name__ == "__main__":
    main()
