"""The apps with windows: Obsidian, driven over Chrome's DevTools protocol, and Apple Notes.

Obsidian runs as a second copy, in a profile of its own that opens a vault of the made-up notes, so nobody's own
Obsidian, vault or settings are touched. Keys are real: sent through DevTools as key events, and timed inside the page
from the key's arrival until the page shows what it did.

Apple Notes keeps its notes in the user's own library, and can only be typed into with permissions this doesn't ask
for, so it gets launch, memory and size. It's opened as the Dock opens it, through Launch Services (started directly,
it shows no window), and timed until its window is on screen. Nothing in the library is read or changed, and if Notes
is already open it's left alone and not measured.
"""
import base64, ctypes, json, os, signal, socket, struct, subprocess, time, urllib.parse, urllib.request

from terminal import descendants, du_mb, footprint_mb, settle

OBSIDIAN_APP = "/Applications/Obsidian.app"
OBSIDIAN = OBSIDIAN_APP + "/Contents/MacOS/Obsidian"
NOTES_APP = "/System/Applications/Notes.app"


class WebSocket:
    """Just enough of a WebSocket client for DevTools: text frames, masked as a client's must be."""
    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((u.hostname, u.port))
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            head += self.sock.recv(4096)
        head, self.buf = head.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise ConnectionError(head.decode(errors="replace"))

    def _frame(self, op, data):
        mask, n = os.urandom(4), len(data)
        size = bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 \
            else bytes([0x80 | 127]) + struct.pack(">Q", n)
        self.sock.sendall(bytes([0x80 | op]) + size + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def send(self, text):
        self._frame(1, text.encode())

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 16)
            if not chunk: raise ConnectionError("DevTools closed the connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        message = b""
        while True:
            b0, b1 = self._read(2)
            n = b1 & 0x7F
            if n == 126: n = struct.unpack(">H", self._read(2))[0]
            elif n == 127: n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            payload = self._read(n)
            if mask: payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            op = b0 & 0x0F
            if op == 9: self._frame(10, payload); continue
            if op == 8: raise ConnectionError("DevTools closed the connection")
            message += payload
            if b0 & 0x80: return message.decode()

    def close(self):
        try: self.sock.close()
        except OSError: pass


def obsidian_profile(root, vault, name="profile"):
    """A throwaway Obsidian profile that opens `vault` and nothing else."""
    data = os.path.join(root, f"obsidian-{name}")
    os.makedirs(data)
    with open(os.path.join(data, "obsidian.json"), "w") as f:
        json.dump({"vaults": {"0123456789abcdef": {"path": vault, "ts": int(time.time() * 1000), "open": True}}}, f)
    return data


class Obsidian:
    """A second Obsidian, in its own profile, driven over DevTools."""
    def __init__(self, data, port=9333):
        self.data, self.port, self.n, self.ws = data, port, 0, None
        null = os.open(os.devnull, os.O_RDWR)
        # As a window in use runs: Chromium slows the timers of windows it takes to be in the background.
        argv = [OBSIDIAN, f"--user-data-dir={data}", f"--remote-debugging-port={port}",
                "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows"]
        self.t0 = time.perf_counter()
        self.pid = os.posix_spawn(OBSIDIAN, argv, os.environ,
                                  file_actions=[(os.POSIX_SPAWN_DUP2, null, 1), (os.POSIX_SPAWN_DUP2, null, 2)], setsid=True)
        os.close(null)

    def connect(self, timeout=30):
        end = time.time() + timeout
        while time.time() < end:
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=0.5))
                pages = [t for t in targets if t.get("type") == "page" and "webSocketDebuggerUrl" in t]
                if pages:
                    self.ws = WebSocket(pages[0]["webSocketDebuggerUrl"])
                    return
            except (OSError, ValueError):
                pass
            time.sleep(0.005)
        raise TimeoutError("Obsidian offered no DevTools page")

    def call(self, method, **params):
        self.n += 1
        me = self.n
        self.ws.send(json.dumps({"id": me, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == me:
                if "error" in msg: raise RuntimeError(msg["error"])
                return msg.get("result", {})

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r: raise RuntimeError(r["exceptionDetails"])
        return r["result"].get("value")

    def wait(self, expr, timeout=60, every=0.005):
        """Seconds from launch until `expr` is true in the page."""
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.js(expr): return time.perf_counter() - self.t0
            except (RuntimeError, ConnectionError):
                pass
            time.sleep(every)
        raise TimeoutError(expr)

    def key(self, key, code, vk, text=None, modifiers=0):
        down = dict(type="keyDown", key=key, code=code, windowsVirtualKeyCode=vk, modifiers=modifiers)
        if text: down.update(text=text, unmodifiedText=text)
        self.call("Input.dispatchKeyEvent", **down)
        self.call("Input.dispatchKeyEvent", type="keyUp", key=key, code=code, windowsVirtualKeyCode=vk, modifiers=modifiers)

    def pids(self):
        """This Obsidian's processes: the app and its helpers (the GPU, network and page processes)."""
        out = subprocess.run(["ps", "-axww", "-o", "pid=,command="], capture_output=True, text=True).stdout
        mine = f"--user-data-dir={self.data}"
        found = {int(line.split(None, 1)[0]) for line in out.splitlines() if mine in line}
        return sorted(found | set(descendants(self.pid)))

    def quit(self):
        if self.ws: self.ws.close()
        try: os.killpg(self.pid, signal.SIGTERM)
        except ProcessLookupError: pass
        end = time.time() + 10
        while not os.waitpid(self.pid, os.WNOHANG)[0]:
            if time.time() > end:
                os.killpg(self.pid, signal.SIGKILL)
                os.waitpid(self.pid, 0)
                break
            time.sleep(0.02)
        for pid in self.pids():
            try: os.kill(pid, signal.SIGKILL)
            except ProcessLookupError: pass


# Times a real key inside the page: from its keydown until `until()` holds after a change under `target`.
ARM = """(() => {
    window.__t = null; window.__done = null;
    addEventListener('keydown', () => { if (window.__t === null) window.__t = performance.now(); }, {capture: true, once: true});
    const target = %s; const until = %s;
    const mo = new MutationObserver(() => {
        if (window.__t === null || window.__done !== null) return;
        if (until()) { window.__done = performance.now(); mo.disconnect(); }
    });
    mo.observe(target, {subtree: true, childList: true, characterData: true});
    return true;
})()"""
READY = "typeof app !== 'undefined' && app.workspace.layoutReady === true"
EDITOR = "document.querySelector('.workspace-leaf.mod-active .cm-content')"


def _timed_key(o, target, until, key, code, vk, text=None, modifiers=0):
    o.js(ARM % (target, until))
    o.key(key, code, vk, text, modifiers)
    o.wait("window.__done !== null", timeout=10, every=0.001)
    return o.js("window.__done - window.__t")


def obsidian(notes, root, launches=7, keys=40, opens=20, log=print):
    """Launch, memory, size, opening a note, typing, and typing in a 30,000-line note."""
    from terminal import LONG
    import shutil
    out = {"size MB": [du_mb(OBSIDIAN_APP)]}
    vault = os.path.join(root, "obsidian-vault")
    shutil.copytree(notes, vault)
    data = obsidian_profile(root, vault)

    log(f"  Obsidian: {launches} launches")
    samples = []
    for run in range(launches + 1):
        o = Obsidian(data)
        o.connect()
        t = o.wait(READY)
        o.quit()
        if run: samples.append(t * 1000)
        time.sleep(1.5)
    out["launch ms"] = samples

    o = Obsidian(data)
    try:
        o.connect()
        o.wait(READY)
        out["busy until, from launch s"] = [settle(o.pids, o.t0)]
        out["memory MB"] = [footprint_mb(o.pids())]
        out["processes"] = [len(o.pids())]

        log(f"  Obsidian: {opens} notes opened (quick switcher, then Enter)")
        names = sorted((f[:-3] for f in os.listdir(vault) if f.endswith(".md")),
                       key=lambda f: -os.path.getmtime(os.path.join(vault, f + ".md")))
        opened = []
        for name in names[40:40 + opens]:
            o.key("o", "KeyO", 79, modifiers=4)
            o.wait("!!document.querySelector('.prompt-input')", timeout=5)
            o.call("Input.insertText", text=name)
            o.wait("[...document.querySelectorAll('.suggestion-item')].some(r => r.textContent.includes(%s))" % json.dumps(name), timeout=5)
            time.sleep(0.15)
            want = json.dumps(name)
            until = (f"() => app.workspace.getActiveFile()?.basename === {want} && "
                     f"({EDITOR}?.textContent || '').includes({want})")
            opened.append(_timed_key(o, "document.querySelector('.workspace')", until, "Enter", "Enter", 13, "\r"))
            time.sleep(0.3)
        out["open a note ms"] = opened

        log(f"  Obsidian: {keys} keys in a short note")
        o.js("(() => { const e = app.workspace.activeEditor.editor; e.setCursor(e.lastLine(), e.getLine(e.lastLine()).length); e.focus(); })()")
        time.sleep(0.3)
        typed = []
        for _ in range(keys):
            typed.append(_timed_key(o, EDITOR, "() => true", "k", "KeyK", 75, "k"))
            time.sleep(0.03)
        out["type a key ms"] = typed
    finally:
        o.quit()

    log("  Obsidian: a 30,000-line note")
    long_vault = os.path.join(root, "obsidian-long-vault")
    os.makedirs(long_vault)
    with open(os.path.join(long_vault, "Profile.md"), "w") as f: f.write("Profile\n" + LONG)
    o = Obsidian(obsidian_profile(root, long_vault, "long"))
    try:
        o.connect()
        o.wait(READY)
        o.js("app.workspace.getLeaf(false).openFile(app.vault.getAbstractFileByPath('Profile.md'))")
        o.wait(f"({EDITOR}?.textContent || '').includes('Some ordinary words')", timeout=30)
        time.sleep(1.0)
        o.js("(() => { const e = app.workspace.activeEditor.editor; e.setCursor(e.lastLine(), e.getLine(e.lastLine()).length); e.focus(); })()")
        time.sleep(0.3)
        ends = []
        for c in "abcdefghij" * (keys // 10):
            ends.append(_timed_key(o, EDITOR, "() => true", c, f"Key{c.upper()}", ord(c.upper()), c))
            time.sleep(0.03)
        o.js("(() => { const e = app.workspace.activeEditor.editor; e.setCursor(1, 0); e.focus(); })()")
        time.sleep(0.3)
        starts = []
        for c in "klmnopqrst" * (keys // 10):
            starts.append(_timed_key(o, EDITOR, "() => true", c, f"Key{c.upper()}", ord(c.upper()), c))
            time.sleep(0.03)
        out["long note, type at the end ms"] = ends
        out["long note, type at the start ms"] = starts
        typed_end, typed_start = o.js("(() => { const e = app.workspace.activeEditor.editor; return [e.getLine(e.lastLine()), e.getLine(1)]; })()")
        if not typed_end.endswith("abcdefghij") or not typed_start.startswith("klmnopqrst"):
            raise RuntimeError("Obsidian: the long note didn't end up as typed")
    finally:
        o.quit()
    return out


# VS Code: the release if it's installed, else Insiders, the same editor a few weeks ahead.
VSCODE_APP = next((a for a in ("/Applications/Visual Studio Code.app", "/Applications/Visual Studio Code - Insiders.app")
                   if os.path.exists(a)), "/Applications/Visual Studio Code.app")
VSCODE_SETTINGS = {
    # Nothing in the way of the notes: no welcome page, no prompt to trust the folder, no update or release-notes
    # checks. Everything else as it comes, with no extensions.
    "workbench.startupEditor": "none",
    "security.workspace.trust.enabled": False,
    "update.mode": "none",
    "update.showReleaseNotes": False,
    "telemetry.telemetryLevel": "off",
    "extensions.autoCheckUpdates": False,
    "extensions.autoUpdate": False,
}
VSCODE_READY = "performance.getEntriesByName('code/LifecyclePhase/Restored').length > 0"
VSCODE_LINES = "[...document.querySelectorAll('.part.editor .monaco-editor .view-line')].map(l => l.textContent.replace(/\\u00a0/g, ' '))"
VSCODE_EDITOR = "document.querySelector('.part.editor .monaco-editor.focused .view-lines') || document.querySelector('.part.editor .monaco-editor .view-lines')"


def vscode_profile(root, name="profile"):
    """A throwaway VS Code profile, and a folder for its (no) extensions."""
    data = os.path.join(root, f"vscode-{name}")
    os.makedirs(os.path.join(data, "User"))
    os.makedirs(os.path.join(root, "vscode-extensions"), exist_ok=True)
    with open(os.path.join(data, "User", "settings.json"), "w") as f: json.dump(VSCODE_SETTINGS, f)
    return data


class VSCode(Obsidian):
    """A second VS Code, in its own profile, opening `folder`, driven over DevTools as Obsidian is."""
    def __init__(self, data, folder, port=9334):
        self.data, self.port, self.n, self.ws = data, port, 0, None
        binary = os.path.join(VSCODE_APP, "Contents/MacOS", _bundle_info(VSCODE_APP, "CFBundleExecutable"))
        argv = [binary, f"--user-data-dir={data}", f"--extensions-dir={os.path.join(os.path.dirname(data), 'vscode-extensions')}",
                f"--remote-debugging-port={port}", "--skip-release-notes", "--skip-welcome", "--disable-updates",
                "--disable-telemetry", "--disable-workspace-trust", "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows", "--new-window", folder]
        env = dict(os.environ)
        for name in ("ELECTRON_RUN_AS_NODE", "VSCODE_IPC_HOOK_CLI", "VSCODE_PID", "VSCODE_CWD"): env.pop(name, None)
        null = os.open(os.devnull, os.O_RDWR)
        self.t0 = time.perf_counter()
        self.pid = os.posix_spawn(binary, argv, env,
                                  file_actions=[(os.POSIX_SPAWN_DUP2, null, 1), (os.POSIX_SPAWN_DUP2, null, 2)], setsid=True)
        os.close(null)

    def connect(self, timeout=60):
        end = time.time() + timeout
        while time.time() < end:
            try:
                targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=0.5))
                pages = [t for t in targets if t.get("type") == "page" and "workbench" in t.get("url", "")
                         and "webSocketDebuggerUrl" in t]
                if pages:
                    self.ws = WebSocket(pages[0]["webSocketDebuggerUrl"])
                    return
            except (OSError, ValueError):
                pass
            time.sleep(0.005)
        raise TimeoutError("VS Code offered no workbench page")


def _bundle_info(app, key):
    return subprocess.run(["defaults", "read", os.path.join(app, "Contents/Info"), key],
                          capture_output=True, text=True).stdout.strip()


def _vscode_open(v, name, shows=None):
    """Opens note `name` with Quick Open (⌘P), as you would: its name, down to it if another ranks first, then
    Enter. Milliseconds from Enter until the editor shows the note."""
    v.key("p", "KeyP", 80, modifiers=4)
    v.wait("(() => { const w = document.querySelector('.quick-input-widget'); return !!w && getComputedStyle(w).display !== 'none'; })()", timeout=5)
    v.call("Input.insertText", text=name)
    exact = json.dumps(name + ".md")
    v.wait("[...document.querySelectorAll('.quick-input-list .monaco-list-row')].some(r => r.textContent.replace(/\\u00a0/g, ' ').startsWith(%s))" % exact, timeout=10)
    time.sleep(0.15)
    focused = "(() => { const r = document.querySelector('.quick-input-list .monaco-list-row.focused'); return !!r && r.textContent.replace(/\\u00a0/g, ' ').startsWith(%s); })()" % exact
    for _ in range(10):
        if v.js(focused): break
        v.key("ArrowDown", "ArrowDown", 40)
        time.sleep(0.05)
    else:
        raise RuntimeError(f"VS Code: Quick Open never selected {name}.md")
    want = json.dumps(shows or "# " + name)
    return _timed_key(v, "document.querySelector('.part.editor')", f"() => {VSCODE_LINES}.some(l => l.includes({want}))",
                      "Enter", "Enter", 13, "\r")


def _vscode_type(v, chars):
    typed = []
    for c in chars:
        typed.append(_timed_key(v, VSCODE_EDITOR, "() => true", c, f"Key{c.upper()}", ord(c.upper()), c))
        time.sleep(0.03)
    return typed


def vscode(notes, root, launches=7, keys=40, opens=20, log=print):
    """Launch, memory, size, opening a note, typing, and typing in a 30,000-line note, as for Obsidian."""
    from terminal import LONG
    import shutil
    out = {"size MB": [du_mb(VSCODE_APP)]}
    folder = os.path.join(root, "vscode-notes")
    shutil.copytree(notes, folder)
    data = vscode_profile(root)

    log(f"  VS Code: {launches} launches")
    samples = []
    for run in range(launches + 1):
        v = VSCode(data, folder)
        v.connect()
        t = v.wait(VSCODE_READY)
        v.quit()
        if run: samples.append(t * 1000)
        time.sleep(1.5)
    out["launch ms"] = samples

    v = VSCode(data, folder)
    try:
        v.connect()
        v.wait(VSCODE_READY)
        out["busy until, from launch s"] = [settle(v.pids, v.t0)]
        out["memory MB"] = [footprint_mb(v.pids())]
        out["processes"] = [len(v.pids())]

        log(f"  VS Code: {opens} notes opened (Quick Open, then Enter)")
        names = sorted((f[:-3] for f in os.listdir(folder) if f.endswith(".md")),
                       key=lambda f: -os.path.getmtime(os.path.join(folder, f + ".md")))
        _vscode_open(v, names[39])
        time.sleep(0.5)
        opened = []
        for name in names[40:40 + opens]:
            opened.append(_vscode_open(v, name))
            time.sleep(0.3)
        out["open a note ms"] = opened

        log(f"  VS Code: {keys} keys in a short note")
        v.key("ArrowDown", "ArrowDown", 40, modifiers=4)
        time.sleep(0.3)
        out["type a key ms"] = _vscode_type(v, "k" * keys)
    finally:
        v.quit()

    log("  VS Code: a 30,000-line note")
    long_folder = os.path.join(root, "vscode-long")
    os.makedirs(long_folder)
    with open(os.path.join(long_folder, "Profile.md"), "w") as f: f.write("Profile\n" + LONG)
    v = VSCode(vscode_profile(root, "long"), long_folder)
    try:
        v.connect()
        v.wait(VSCODE_READY)
        # Once it has settled, as for the short notes: right after launch Quick Open hasn't listed the folder yet.
        settle(v.pids, v.t0)
        _vscode_open(v, "Profile", shows="Some ordinary words")
        time.sleep(1.0)
        v.key("ArrowDown", "ArrowDown", 40, modifiers=4)
        time.sleep(0.5)
        ends = _vscode_type(v, "abcdefghij" * (keys // 10))
        end_ok = v.js(f"{VSCODE_LINES}.some(l => l.endsWith('abcdefghij'))")
        v.key("ArrowUp", "ArrowUp", 38, modifiers=4)
        time.sleep(0.5)
        v.key("ArrowDown", "ArrowDown", 40)
        time.sleep(0.3)
        starts = _vscode_type(v, "klmnopqrst" * (keys // 10))
        start_ok = v.js(f"{VSCODE_LINES}.some(l => l.startsWith('klmnopqrst') && l.endsWith('Some ordinary words.'))")
        if not (end_ok and start_ok):
            raise RuntimeError("VS Code: the long note didn't end up as typed")
        out["long note, type at the end ms"] = ends
        out["long note, type at the start ms"] = starts
    finally:
        v.quit()
    return out


# Apple Notes: its window, found through CoreGraphics' window list.
_cg = ctypes.CDLL("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics")
_cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
_cg.CGWindowListCopyWindowInfo.restype, _cg.CGWindowListCopyWindowInfo.argtypes = ctypes.c_void_p, [ctypes.c_uint32, ctypes.c_uint32]
_cf.CFArrayGetCount.restype, _cf.CFArrayGetCount.argtypes = ctypes.c_long, [ctypes.c_void_p]
_cf.CFArrayGetValueAtIndex.restype, _cf.CFArrayGetValueAtIndex.argtypes = ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_long]
_cf.CFDictionaryGetValue.restype, _cf.CFDictionaryGetValue.argtypes = ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_void_p]
_cf.CFStringCreateWithCString.restype, _cf.CFStringCreateWithCString.argtypes = ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
_cf.CFNumberGetValue.restype, _cf.CFNumberGetValue.argtypes = ctypes.c_bool, [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
_cf.CFRelease.argtypes = [ctypes.c_void_p]
_KEYS = {k: _cf.CFStringCreateWithCString(None, k.encode(), 0x08000100)
         for k in ("kCGWindowOwnerPID", "kCGWindowLayer", "kCGWindowBounds", "Width", "Height")}


def _number(dictionary, key, double=False):
    ref = _cf.CFDictionaryGetValue(dictionary, _KEYS[key])
    if not ref: return None
    value = ctypes.c_double() if double else ctypes.c_int64()
    _cf.CFNumberGetValue(ref, 13 if double else 4, ctypes.byref(value))
    return value.value


def window_on_screen(pid):
    windows = _cg.CGWindowListCopyWindowInfo(1 | 16, 0)  # on screen only, without desktop elements
    try:
        for i in range(_cf.CFArrayGetCount(windows)):
            w = _cf.CFArrayGetValueAtIndex(windows, i)
            if _number(w, "kCGWindowOwnerPID") != pid or _number(w, "kCGWindowLayer") != 0: continue
            bounds = _cf.CFDictionaryGetValue(w, _KEYS["kCGWindowBounds"])
            if bounds and (_number(bounds, "Width", True) or 0) > 300 and (_number(bounds, "Height", True) or 0) > 200:
                return True
        return False
    finally:
        _cf.CFRelease(windows)


def notes_pids():
    out = subprocess.run(["ps", "-axww", "-o", "pid=,command="], capture_output=True, text=True).stdout
    return [int(l.split(None, 1)[0]) for l in out.splitlines() if l.split(None, 1)[1].startswith(NOTES_APP)]


def notes_quit():
    for p in notes_pids():
        try: os.kill(p, signal.SIGTERM)
        except ProcessLookupError: pass
    end = time.time() + 10
    while notes_pids() and time.time() < end: time.sleep(0.05)


def notes_size_mb():
    """Notes.app and the frameworks only Notes uses (NotesShared, NotesUI and the rest): their code, which macOS
    keeps in its shared cache rather than in the frameworks' folders, and their resources. Frameworks every app
    shares, AppKit or WebKit, aren't counted, as for the other apps."""
    import glob, re
    folders = glob.glob("/System/Library/PrivateFrameworks/Notes*.framework")
    code = 0.0
    for folder in folders:
        name = os.path.basename(folder)[:-len(".framework")]
        segments = subprocess.run(["dyld_info", "-segments", os.path.join(folder, "Versions/A", name)],
                                  capture_output=True, text=True).stdout
        # dyld_info lists each segment twice: counted once, by its address.
        unique = {(addr, seg): int(kb) for addr, seg, kb in re.findall(r"^\s+(0x[0-9A-F]+)\s+(__\w+)\s+(\d+)KB\s", segments, re.M)}
        code += sum(kb for (_, seg), kb in unique.items() if seg != "__LINKEDIT") / 1024
    return du_mb(NOTES_APP) + code + (du_mb(*folders) if folders else 0)


def apple_notes(launches=7, log=print):
    """Launch to its window on screen, then memory and size. None if Notes is already open."""
    if notes_pids():
        log("  Apple Notes is open: skipped, so nothing of yours is closed")
        return None
    out = {"size MB": [notes_size_mb()]}
    log(f"  Apple Notes: {launches} launches")
    samples = []
    for run in range(launches + 1):
        t0 = time.perf_counter()
        subprocess.Popen(["open", "-a", NOTES_APP])
        pid = None
        while not (pid and window_on_screen(pid)):
            if time.perf_counter() - t0 > 30: raise TimeoutError("Apple Notes showed no window")
            pids = notes_pids()
            pid = pids[0] if pids else None
            time.sleep(0.003)
        if run: samples.append((time.perf_counter() - t0) * 1000)
        if run < launches:
            time.sleep(1.0)
            notes_quit()
            time.sleep(1.5)
    out["launch ms"] = samples
    t0 = time.perf_counter()
    out["busy after its window s"] = [settle(notes_pids, t0)]
    out["memory MB"] = [footprint_mb(notes_pids())]
    out["processes"] = [len(notes_pids())]
    notes_quit()
    return out
