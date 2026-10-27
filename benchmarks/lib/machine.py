"""What a result depends on, recorded with it: the Mac, its power, how busy it was, and every app's version."""
import datetime, hashlib, json, os, platform, subprocess


def _run(*argv):
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _sysctl(name):
    return _run("sysctl", "-n", name)


def _bundle_version(app):
    return _run("defaults", "read", os.path.join(app, "Contents/Info"), "CFBundleShortVersionString") or None


def info():
    hw = {}
    try:
        hw = json.loads(_run("system_profiler", "SPHardwareDataType", "-json"))["SPHardwareDataType"][0]
    except (ValueError, KeyError, IndexError):
        pass
    power = _run("pmset", "-g", "batt").splitlines()
    low_power = [l.split()[-1] for l in _run("pmset", "-g").splitlines() if "lowpowermode" in l]
    now = datetime.datetime.now().astimezone()
    return {
        "date": now.isoformat(timespec="seconds"),
        "machine": hw.get("machine_name"),
        "model": _sysctl("hw.model"),
        "chip": _sysctl("machdep.cpu.brand_string"),
        "cores": {"total": int(_sysctl("hw.ncpu") or 0), "performance": int(_sysctl("hw.perflevel0.physicalcpu") or 0),
                  "efficiency": int(_sysctl("hw.perflevel1.physicalcpu") or 0)},
        "memory GB": round(int(_sysctl("hw.memsize") or 0) / 2**30),
        "macOS": f"{_run('sw_vers', '-productVersion')} ({_run('sw_vers', '-buildVersion')})",
        "power": power[0].replace("Now drawing from ", "").strip("'") if power else None,
        "low power mode": (low_power[0] == "1") if low_power else None,
        "python": platform.python_version(),
    }


def _vscode_version():
    """"1.125.0", or "1.125.0-insider" for Insiders, which runs where the release isn't installed."""
    from apps import VSCODE_APP
    return _bundle_version(VSCODE_APP) if os.path.exists(VSCODE_APP) else None


def versions(noted_binary):
    first = lambda *argv: (_run(*argv).splitlines() or [""])[0] or None
    with open(noted_binary, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    return {
        "noted": first(noted_binary, "--version"),
        "noted sha256": digest,
        "Apple Notes": _bundle_version("/System/Applications/Notes.app"),
        "Obsidian": _bundle_version("/Applications/Obsidian.app"),
        "VS Code": _vscode_version(),
        "vim": first("/usr/bin/vim", "--version"),
        "Neovim": first("/opt/homebrew/bin/nvim", "--version"),
        "Emacs": first("/opt/homebrew/bin/emacs", "--version"),
    }
