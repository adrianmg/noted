#!/usr/bin/env python3
"""noted against Apple Notes, Obsidian, VS Code, vim and Emacs, in one sitting on one Mac: the comparison on
noted.computer (Neovim too, with --apps). Writes a results folder with the machine it ran on, every sample, and a
summary.

    python3 bench/compare.py --noted target/release/noted
    python3 bench/compare.py --noted target/release/noted --apps noted,vim,emacs --quick

Run it plugged in, with nothing else busy (a load average under about 5): it says so if not. Needs macOS, Python 3.9
or newer (as macOS has it), Xcode's command-line tools (cc, dyld_info), Obsidian and VS Code (or VS Code Insiders) in
/Applications, and vim and Emacs (/usr/bin/vim; Emacs, and Neovim if asked for, from Homebrew). Apple Notes is
opened and closed on your own library: nothing in it is read or changed, and it's left out if Notes is already open.
See README.md for how each test works.
"""
import argparse, datetime, json, os, shutil, statistics, subprocess, sys, tempfile, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
import apps, machine, terminal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["noted", "Apple Notes", "Obsidian", "VS Code", "vim", "Neovim", "Emacs"]
KEYS = {"noted": "noted", "notes": "Apple Notes", "obsidian": "Obsidian", "vscode": "VS Code", "vim": "vim", "neovim": "Neovim",
        "emacs": "Emacs"}
ROWS = [("Launch", "launch ms", "ms"), ("Memory", "memory MB", "MB"), ("Size on disk", "size MB", "MB"),
        ("Open a note", "open a note ms", "ms"), ("Type a key", "type a key ms", "ms"),
        ("Long note, type at the start", "long note, type at the start ms", "ms"),
        ("Long note, type at the end", "long note, type at the end ms", "ms")]


def stats(values):
    v = sorted(x for x in values if x is not None)
    if not v: return None
    return {"n": len(v), "median": statistics.median(v), "p95": v[min(len(v) - 1, round(0.95 * (len(v) - 1)))],
            "min": v[0], "max": v[-1]}


def fmt(x, unit):
    if x is None: return "–"
    if x >= 100: return f"{x:,.0f} {unit}"
    if x >= 10: return f"{x:.0f} {unit}" if unit == "ms" else f"{x:.1f} {unit}"
    if x >= 1: return f"{x:.1f} {unit}"
    if x >= 0.1: return f"{x:.2f} {unit}"
    return f"{x:.3f} {unit}"


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--noted", required=True, help="the noted to measure (a release build)")
    p.add_argument("--apps", default="noted,notes,obsidian,vscode,vim,emacs",
                   help="which, comma-separated (also: neovim)")
    p.add_argument("--notes", type=int, default=1000, help="how many made-up notes (default 1,000)")
    p.add_argument("--out", help="results folder (default bench/results/<date>-<noted version>)")
    p.add_argument("--built-from", help="where the noted build came from, recorded with the results (a release, a commit)")
    p.add_argument("--quick", action="store_true", help="a few samples each, to try it: not for publishing")
    p.add_argument("--asleep", action="store_true", help="no busy loop keeping the processor awake")
    a = p.parse_args()
    if sys.platform != "darwin": sys.exit("compare: macOS only")
    noted_bin = os.path.abspath(a.noted)
    chosen = [KEYS[k.strip().lower()] for k in a.apps.split(",") if k.strip()]
    n_launch, n_gui, n_keys, n_opens, trials = (3, 2, 10, 5, 1) if a.quick else (20, 7, 40, 20, 4)

    meta = {"machine": machine.info(), "versions": machine.versions(noted_bin),
            "settings": {"notes": a.notes, "terminal": f"{terminal.COLS} x {terminal.ROWS}, xterm-256color",
                         "launches": {"terminal apps": n_launch, "Apple Notes, Obsidian and VS Code": n_gui},
                         "keys": n_keys, "notes opened": n_opens, "long note": "30,000 lines",
                         "long note trials": trials, "busy loop": not a.asleep, "quick": a.quick},
            "load before": list(os.getloadavg())}
    if a.built_from: meta["versions"]["noted built from"] = a.built_from
    m = meta["machine"]
    print(f"{m['machine']} ({m['model']}), {m['chip']}, {m['memory GB']} GB, macOS {m['macOS']}; {m['power']}; "
          f"load {meta['load before'][0]:.1f}", file=sys.stderr)
    if m["power"] and "AC" not in m["power"]:
        print("  not plugged in: macOS may slow the processor on battery", file=sys.stderr)
    if meta["load before"][0] > 5:
        print("  the Mac is busy (load above 5): timings will be noisy", file=sys.stderr)

    root = tempfile.mkdtemp(prefix="noted-compare-")
    notes = os.path.join(root, "notes")
    terminal.make_notes(notes, a.notes)
    loop = None if a.asleep else subprocess.Popen(["nice", "-n", "20", sys.executable, "-c", "while True: pass"])
    raw, log = {}, lambda s: print(s, file=sys.stderr, flush=True)
    try:
        if "Emacs" in chosen:
            meta["helper overhead ms"] = terminal.helper_overhead_ms()
        for app in [x for x in ORDER if x in chosen]:
            log(f"== {app}")
            if app == "noted":
                raw[app] = terminal.noted(noted_bin, notes, root, n_launch, n_keys, n_opens, trials, log)
                raw[app]["size MB"] = [os.path.getsize(noted_bin) / 2**20]
            elif app == "Apple Notes":
                result = apps.apple_notes(n_gui, log)
                if result: raw[app] = result
            elif app == "Obsidian":
                raw[app] = apps.obsidian(notes, root, n_gui, n_keys, n_opens, log)
            elif app == "VS Code":
                raw[app] = apps.vscode(notes, root, n_gui, n_keys, n_opens, log)
            else:
                spec = terminal.EDITORS[app]
                raw[app] = terminal.editor(app, notes, root, n_launch, n_keys, n_opens, trials, log)
                paths = spec.get("size") or [subprocess.run(["brew", "--prefix", spec["formula"]], capture_output=True,
                                                            text=True).stdout.strip()]
                raw[app]["size MB"] = [terminal.du_mb(*paths)]
    finally:
        if loop:
            loop.kill()
            loop.wait()
        shutil.rmtree(root, ignore_errors=True)
    meta["load after"] = list(os.getloadavg())

    # Emacs starts through the controlling-terminal helper: its launch, less the helper's own cost.
    if "Emacs" in raw and "helper overhead ms" in meta:
        raw["Emacs"]["launch, less the helper ms"] = [x - meta["helper overhead ms"] for x in raw["Emacs"]["launch ms"]]

    version = (meta["versions"]["noted"] or "noted").split()[-1]
    out = a.out
    if not out:
        # <date>-<version>, or -2, -3 for another sitting the same day.
        base = os.path.join(HERE, "results", f"{datetime.date.today().isoformat()}-{version}{'-quick' if a.quick else ''}")
        out, n = base, 1
        while os.path.exists(out):
            n += 1
            out = f"{base}-{n}"
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "machine.json"), "w") as f: json.dump(meta, f, indent=1)
    with open(os.path.join(out, "raw.json"), "w") as f: json.dump(raw, f, indent=1)
    summary = write_summary(out, meta, raw)
    print(summary)
    print(f"written to {out}", file=sys.stderr)


def short_version(app, full):
    """"noted 1.1.0", "Neovim 0.12.6", "vim 9.1": the app and its version, from what it reports."""
    import re
    found = re.search(r"\d+(\.\d+)+", full or "")
    if app == "VS Code" and "insider" in (full or ""): app = "VS Code Insiders"
    return f"{app} {found.group(0)}" if found else app


def write_summary(out, meta, raw):
    m, v = meta["machine"], meta["versions"]
    present = [x for x in ORDER if x in raw]
    med = lambda app, key: (stats(raw[app].get(key, [])) or {}).get("median")
    lines = [f"# noted benchmark: {m['date'][:10]}, {v['noted']}", "",
             f"**Machine.** {m['machine']} ({m['model']}), {m['chip']} ({m['cores']['performance']} performance and "
             f"{m['cores']['efficiency']} efficiency cores), {m['memory GB']} GB, macOS {m['macOS']}. {m['power']}"
             f"{', Low Power Mode on' if m['low power mode'] else ''}. Load average {meta['load before'][0]:.1f} before, "
             f"{meta['load after'][0]:.1f} after"
             f"{', with one low-priority busy loop keeping the processor awake' if meta['settings']['busy loop'] else ''}.", "",
             "**Apps.** " + ", ".join(short_version(app, v.get(app)) for app in present) + ", default settings.", "",
             f"**Notes.** {meta['settings']['notes']:,} made-up Markdown notes of about 1.5 KB. "
             + ("A quick run, for trying the scripts: too few samples to publish." if meta["settings"]["quick"] else ""), "",
             "## Medians", "",
             "| | " + " | ".join(present) + " |", "|---|" + "---|" * len(present)]
    for label, key, unit in ROWS:
        cells = []
        for app in present:
            k = "launch, less the helper ms" if (app == "Emacs" and key == "launch ms" and "launch, less the helper ms" in raw[app]) else key
            cells.append(fmt(med(app, k), unit))
        if any(c != "–" for c in cells):
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
    if "Emacs" in raw and "helper overhead ms" in meta:
        lines += ["", f"Emacs' launch is shown less the {meta['helper overhead ms']:.2f} ms its controlling-terminal "
                      f"helper takes on its own (raw median {med('Emacs', 'launch ms'):.1f} ms)."]
    lines += ["", "## Every test", "", "| App | Test | n | Median | p95 | Min | Max |", "|---|---|---|---|---|---|---|"]
    for app in present:
        for key, values in raw[app].items():
            s = stats(values)
            if not s: continue
            unit = key.rsplit(" ", 1)[-1]
            name = key.rsplit(" ", 1)[0] if unit in ("ms", "MB", "s") else key
            u = unit if unit in ("ms", "MB", "s") else ""
            lines.append(f"| {app} | {name} | {s['n']} | {s['median']:.3f} {u} | {s['p95']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
    summary = "\n".join(lines) + "\n"
    with open(os.path.join(out, "summary.md"), "w") as f: f.write(summary)
    return summary


if __name__ == "__main__":
    main()
