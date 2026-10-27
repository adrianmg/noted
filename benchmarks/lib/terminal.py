"""Programs that run in a terminal, driven the way a terminal drives them: noted, vim, Neovim and Emacs.

Each runs on a pseudo-terminal of 120 x 40 cells, with TERM=xterm-256color, its default settings and a home of its
own (so nobody's configuration counts). Every one is timed the same way: from starting it, or from writing a key, to
the last byte it draws before its screen goes quiet. The queries programs send a terminal at start (its attributes,
the cursor's position, its colors) are answered as a terminal would, so no program waits on a reply.
"""
import ctypes, fcntl, os, pty, random, re, select, shutil, struct, subprocess, tempfile, termios, time

ROWS, COLS = 40, 120
LONG = "Some ordinary words.\n" * 30_000
WORDS = ("meeting groceries project idea plan budget travel lisbon recipe book notes weekly review design rust "
         "terminal coffee garden music family health run journal todo call email draft launch research kitchen "
         "paper window river stone light market winter letter garden ticket station museum harbor lantern violin "
         "bakery").split()

# A terminal's answers to the queries programs send it.
QUERIES = [
    (re.compile(rb"\x1b\[[0]?c"), b"\x1b[?62;22c"),                          # primary device attributes
    (re.compile(rb"\x1b\[>[0]?c"), b"\x1b[>41;390;0c"),                      # secondary: xterm 390
    (re.compile(rb"\x1b\[6n"), b"\x1b[1;1R"),                                # cursor position
    (re.compile(rb"\x1b\[>0?q"), b"\x1bP>|xterm(390)\x1b\\"),                # terminal name and version
    (re.compile(rb"\x1b\]11;\?(\x07|\x1b\\)"), b"\x1b]11;rgb:0000/0000/0000\x1b\\"),  # background color
    (re.compile(rb"\x1b\]10;\?(\x07|\x1b\\)"), b"\x1b]10;rgb:ffff/ffff/ffff\x1b\\"),  # foreground color
    (re.compile(rb"\x1b\[\?(\d+)\$p"), None),                                # a mode: "not recognized"
]

# Emacs wants a controlling terminal, which macOS hands a process only through an ioctl. This helper does that
# and runs the program; its own cost is measured (helper_overhead_ms) and taken off Emacs' launch.
CTTY_C = (b"#include <sys/ioctl.h>\n#include <unistd.h>\n"
          b"int main(int c, char **v) { (void)c; ioctl(0, TIOCSCTTY, 0); execv(v[1], v + 1); return 127; }\n")
CTTY = os.path.join(tempfile.gettempdir(), "noted-bench-ctty")


def ctty():
    if not os.access(CTTY, os.X_OK):
        with open(CTTY + ".c", "wb") as f: f.write(CTTY_C)
        subprocess.run(["cc", "-O2", "-o", CTTY, CTTY + ".c"], check=True)
    return CTTY


def make_notes(folder, n, seed=7):
    """n made-up Markdown notes of about 1.5 KB: headings, tasks, bold and italic. The same seed, the same notes."""
    os.makedirs(folder)
    rnd, now = random.Random(seed), time.time()
    for i in range(n):
        title = f"{rnd.choice(WORDS).title()} {rnd.choice(WORDS)} {i}"
        lines = [f"# {title}", ""]
        while sum(len(line) + 1 for line in lines) < 1500:
            k = rnd.random()
            if k < 0.15: lines.append(f"## {rnd.choice(WORDS).title()} {rnd.choice(WORDS)}")
            elif k < 0.35: lines.append(f"- [ ] {rnd.choice(WORDS)} the {rnd.choice(WORDS)}")
            elif k < 0.5: lines.append(f"- **{rnd.choice(WORDS)}** and *{rnd.choice(WORDS)}*")
            else: lines.append(" ".join(rnd.choice(WORDS) for _ in range(14)) + ".")
        path = os.path.join(folder, title + ".md")
        with open(path, "w") as f: f.write("\n".join(lines) + "\n")
        t = now - 60 * (i + 1)
        os.utime(path, (t, t))


_libproc = ctypes.CDLL("/usr/lib/libproc.dylib")


class _Timebase(ctypes.Structure):
    _fields_ = [("numer", ctypes.c_uint32), ("denom", ctypes.c_uint32)]


_tb = _Timebase()
ctypes.CDLL(None).mach_timebase_info(ctypes.byref(_tb))


def _rusage(pid):
    info = (ctypes.c_uint64 * 64)()  # rusage_info_v2, as 64-bit words
    return info if _libproc.proc_pid_rusage(pid, 2, ctypes.byref(info)) == 0 else None


def footprint_mb(pids):
    """Physical footprint, the number Activity Monitor shows, added up over the processes, in MB (MiB)."""
    return sum(r[9] for r in map(_rusage, pids) if r) / 2**20


def cpu_seconds(pids):
    return sum((r[2] + r[3]) * _tb.numer / _tb.denom / 1e9 for r in map(_rusage, pids) if r)


def settle(pids, since, limit=60):
    """Seconds from `since` until the processes use under 20 ms of CPU a second."""
    while True:
        c = cpu_seconds(pids()); time.sleep(1)
        if (cpu_seconds(pids()) - c) * 1000 < 20 or time.perf_counter() - since > limit:
            return time.perf_counter() - since - 1


def descendants(pid):
    kids = [int(p) for p in subprocess.run(["pgrep", "-P", str(pid)], capture_output=True, text=True).stdout.split()]
    return [pid] + [d for k in kids for d in descendants(k)]


def du_mb(*paths):
    """Disk use of the paths, in MB (MiB): each followed if it's a link itself, but not the links inside it, so an app
    bundle's framework links aren't counted twice."""
    return sum(int(subprocess.run(["du", "-sk", os.path.realpath(p)], capture_output=True, text=True).stdout.split()[0])
               for p in paths) / 1024


class Term:
    def __init__(self, argv, env, controlling=False):
        self.fd, tty = pty.openpty()
        fcntl.ioctl(tty, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        dup = [(os.POSIX_SPAWN_DUP2, tty, 0), (os.POSIX_SPAWN_DUP2, tty, 1), (os.POSIX_SPAWN_DUP2, tty, 2)]
        argv = [ctty()] + argv if controlling else argv
        self.started = time.perf_counter()
        self.pid = os.posix_spawn(argv[0], argv, env, file_actions=dup, setsid=True)
        os.close(tty)
        self.seen = b""
        self.first_frame = None

    def _answer(self, data):
        self.seen = (self.seen + data)[-512:]
        for pattern, reply in QUERIES:
            for m in list(pattern.finditer(self.seen)):
                os.write(self.fd, reply if reply is not None else b"\x1b[?" + m.group(1) + b";0$y")
            self.seen = pattern.sub(b"", self.seen)

    def settle(self, quiet, timeout=10.0):
        """Reads until `quiet` seconds pass without output: the time of the last byte (None if nothing came)."""
        last, end = None, time.monotonic() + timeout
        while time.monotonic() < end:
            if not select.select([self.fd], [], [], quiet)[0]:
                if last is not None: return last
                continue
            try: data = os.read(self.fd, 1 << 16)
            except OSError: return last
            if data:
                last = time.perf_counter()
                if self.first_frame is None and b"\x1b[?2026l" in data: self.first_frame = last
                self._answer(data)
        raise TimeoutError("the screen never went quiet")

    def key(self, data, quiet=0.03):
        """Milliseconds from writing `data` to the last byte drawn in answer."""
        if select.select([self.fd], [], [], 0)[0]: self.settle(0.01)
        t = time.perf_counter()
        os.write(self.fd, data)
        last = self.settle(quiet)
        return None if last is None else (last - t) * 1000

    def send(self, data, quiet=0.05):
        os.write(self.fd, data)
        try: self.settle(quiet, timeout=5)
        except TimeoutError: pass

    def close(self, keys):
        for k in keys:
            os.write(self.fd, k)
            time.sleep(0.15)
        for _ in range(300):
            if os.waitpid(self.pid, os.WNOHANG)[0]: break
            try:
                if select.select([self.fd], [], [], 0.01)[0]: self._answer(os.read(self.fd, 1 << 16))
            except OSError: pass
        else:
            os.kill(self.pid, 9)
            os.waitpid(self.pid, 0)
        os.close(self.fd)


def env_for(home):
    os.makedirs(home, exist_ok=True)
    return {"HOME": home, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin", "TERM": "xterm-256color",
            "COLORTERM": "truecolor", "LANG": "en_US.UTF-8", "TMPDIR": home + "/",
            "XDG_CONFIG_HOME": os.path.join(home, ".config"), "XDG_CACHE_HOME": os.path.join(home, ".cache"),
            "XDG_DATA_HOME": os.path.join(home, ".local/share"), "XDG_STATE_HOME": os.path.join(home, ".local/state")}


def helper_overhead_ms(runs=60):
    """What starting a program through the controlling-terminal helper adds: /usr/bin/true, with and without it."""
    def spawn(argv):
        t0 = time.perf_counter()
        os.waitpid(os.posix_spawn(argv[0], argv, dict(os.environ), setsid=True), 0)
        return (time.perf_counter() - t0) * 1000
    for _ in range(5): spawn(["/usr/bin/true"]); spawn([ctty(), "/usr/bin/true"])
    bare = sorted(spawn(["/usr/bin/true"]) for _ in range(runs))
    helped = sorted(spawn([ctty(), "/usr/bin/true"]) for _ in range(runs))
    return helped[runs // 2] - bare[runs // 2]


# How each editor opens a file, types at its end and at its second line's start, opens another file, saves and quits.
EDITORS = {
    "vim": dict(path="/usr/bin/vim", argv=lambda f: ["/usr/bin/vim", f], end=b"Go", start=b"\x1bggjI",
                quit=[b"\x1b", b":wq\r"], open=lambda name: b":e " + name.encode(), size=["/usr/bin/vim", "/usr/share/vim"]),
    "Neovim": dict(path="/opt/homebrew/bin/nvim", argv=lambda f: ["/opt/homebrew/bin/nvim", f], end=b"Go",
                   start=b"\x1bggjI", quit=[b"\x1b", b":wq\r"], open=lambda name: b":e " + name.encode(), formula="neovim"),
    "Emacs": dict(path="/opt/homebrew/bin/emacs", argv=lambda f: ["/opt/homebrew/bin/emacs", "-nw", f],
                  end=b"\x1b>\r", start=b"\x1b<\x0e\x01", quit=[b"\x18\x13", b"\x18\x03"],
                  open=lambda name: b"\x18\x06" + name.encode(), controlling=True, formula="emacs"),
}


def editor(name, notes, root, launches=20, keys=40, opens=20, trials=4, log=print):
    """Launch, memory, opening a note, typing, and typing in a 30,000-line note, for one of EDITORS."""
    spec, out = EDITORS[name], {}
    controlling = spec.get("controlling", False)
    start = lambda f, work: Term(spec["argv"](f), env_for(os.path.join(work, "home")), controlling)
    note = sorted(os.path.join(notes, f) for f in os.listdir(notes))[0]

    def copy_note():
        work = tempfile.mkdtemp(dir=root)
        shutil.copy(note, os.path.join(work, "note.md"))
        return work, os.path.join(work, "note.md")

    log(f"  {name}: {launches} launches")
    samples = []
    # One home kept from launch to launch, as on anyone's Mac; the first launch, which sets it up, isn't counted.
    kept = tempfile.mkdtemp(dir=root)
    memory = []
    for run in range(launches + 1):
        _, f = copy_note()
        t = start(f, kept)
        last = t.settle(0.3)
        # Memory once it's ready (quiet for 0.3 s), at every launch counted: the median goes in the summary.
        if run:
            memory.append(footprint_mb(descendants(t.pid)))
            out["processes"] = [len(descendants(t.pid))]
        t.close(spec["quit"])
        if run: samples.append((last - t.started) * 1000)
        time.sleep(0.3)
    out["launch ms"] = samples
    out["memory MB"] = memory

    log(f"  {name}: {keys} keys in a short note")
    work, f = copy_note()
    t = start(f, work)
    t.settle(0.3)
    t.send(spec["end"])
    typed = []
    for _ in range(keys):
        typed.append(t.key(b"k"))
        time.sleep(0.03)
    t.close(spec["quit"])
    if "k" * keys not in open(f).read(): raise RuntimeError(f"{name}: the typed keys aren't in the note")
    out["type a key ms"] = typed

    log(f"  {name}: {opens} notes opened")
    work = tempfile.mkdtemp(dir=root)
    for i, src in enumerate(sorted(os.listdir(notes))[:opens + 1]):
        shutil.copy(os.path.join(notes, src), os.path.join(work, f"note-{i:02}.md"))
    here = os.getcwd()
    os.chdir(work)
    try:
        t = start("note-00.md", work)
        t.settle(0.3)
        opened = []
        for i in range(1, opens + 1):
            t.send(spec["open"](f"note-{i:02}.md"))
            opened.append(t.key(b"\r"))
            time.sleep(0.05)
        t.close(spec["quit"])
    finally:
        os.chdir(here)
    out["open a note ms"] = opened

    log(f"  {name}: a 30,000-line note")
    ends, starts = [], []
    for trial in range(trials):
        work = tempfile.mkdtemp(dir=root)
        f = os.path.join(work, "long.md")
        with open(f, "w") as fh: fh.write("Profile\n" + LONG)
        t = start(f, work)
        t.settle(0.5, timeout=30)
        t.send(spec["end"])
        ends += [t.key(bytes([c])) for c in b"abcdefghij"]
        t.send(spec["start"])
        starts += [t.key(bytes([c])) for c in b"klmnopqrst"]
        t.close(spec["quit"])
        text = open(f).read()
        if "abcdefghij" not in text[-40:] or not text.split("\n")[1].startswith("klmnopqrst"):
            raise RuntimeError(f"{name}: the long note didn't end up as typed")
    out["long note, type at the end ms"] = ends
    out["long note, type at the start ms"] = starts
    return out


def noted(binary, notes, root, launches=20, keys=40, opens=20, trials=4, log=print):
    """The same, for noted: it opens on its notes folder, a new note ready."""
    out = {}
    start = lambda folder, work: Term([binary, "--dir", folder], env_for(os.path.join(work, "home")))

    def copy_notes():
        work = tempfile.mkdtemp(dir=root)
        shutil.copytree(notes, os.path.join(work, "notes"))
        return work, os.path.join(work, "notes")

    log(f"  noted: {launches} launches")
    samples, frames = [], []
    # One home kept from launch to launch, as on anyone's Mac; the first launch, which sets it up, isn't counted.
    kept = tempfile.mkdtemp(dir=root)
    memory = []
    for run in range(launches + 1):
        t = start(notes, kept)
        last = t.settle(0.3)
        # Memory once it's ready (quiet for 0.3 s), at every launch counted: the median goes in the summary.
        if run:
            memory.append(footprint_mb([t.pid]))
        t.close([b"\x11"])
        if run:
            samples.append((last - t.started) * 1000)
            frames.append((t.first_frame - t.started) * 1000)
        time.sleep(0.3)
    out["launch ms"] = samples
    out["launch, first full frame ms"] = frames
    out["memory MB"] = memory
    out["processes"] = [1]

    log(f"  noted: {keys} keys in a short note")
    work, folder = copy_notes()
    t = start(folder, work)
    t.settle(0.3)
    for k in (b"\x1b", b"\x1b[B", b"\r", b"\x1b[1;5F"): t.send(k)
    typed = []
    for _ in range(keys):
        typed.append(t.key(b"k"))
        time.sleep(0.03)
    t.close([b"\x11"])
    out["type a key ms"] = typed

    log(f"  noted: {opens} notes opened")
    work, folder = copy_notes()
    t = start(folder, work)
    t.settle(0.3)
    t.send(b"\x1b")
    out["open a note ms"] = [t.key(b"\x1b[B") for _ in range(opens)]
    t.close([b"\x11"])

    log("  noted: a 30,000-line note")
    ends, starts = [], []
    for trial in range(trials):
        work = tempfile.mkdtemp(dir=root)
        folder = os.path.join(work, "notes")
        os.makedirs(folder)
        with open(os.path.join(folder, "Profile.md"), "w") as fh: fh.write("Profile\n" + LONG)
        t = start(folder, work)
        t.settle(0.5, timeout=30)
        for k in (b"\x06", b"Profile", b"\r", b"\x1b[1;5F"): t.send(k)
        ends += [t.key(bytes([c])) for c in b"abcdefghij"]
        for k in (b"\x1b[1;5H", b"\x1b[B", b"\x1b[H"): t.send(k)
        starts += [t.key(bytes([c])) for c in b"klmnopqrst"]
        t.close([b"\x11"])
        if open(os.path.join(folder, "Profile.md")).read() != "Profile\nklmnopqrst" + LONG + "abcdefghij":
            raise RuntimeError("noted: the long note didn't end up as typed")
    out["long note, type at the end ms"] = ends
    out["long note, type at the start ms"] = starts
    return out
