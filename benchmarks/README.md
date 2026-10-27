# How noted's speed is measured

[noted.computer](https://noted.computer) compares noted with Apple Notes, Obsidian, VS Code, vim
and Emacs. This folder has everything behind those numbers: the scripts, the Mac they ran on, and
every sample, so anyone can check them or run them again. `compare.py` measures Neovim too when asked
(`--apps`), as earlier sittings did.

- **[results/](results/)**: one folder per sitting.
  - `summary.md`: the medians, then every test with its count, 95th percentile, minimum and maximum.
  - `raw.json`: every sample.
  - `machine.json`: the Mac, whether it was plugged in, how busy it was, and each app's exact version.
  - `noted-builds.txt` and `.json`, where there are: noted's previous release against this one, by
    [noted.py](noted.py), in the same sitting.
- **[compare.py](compare.py)**: the comparison: every app, in one sitting.
- **[noted.py](noted.py)**: noted alone, at 1,000 and 10,000 notes and in a 30,000-line note, to
  compare one build of noted with another.
- **[lib/](lib/)**: how each app is driven. [terminal.py](lib/terminal.py) drives noted, vim,
  Emacs and Neovim, [apps.py](lib/apps.py) Obsidian, VS Code and Apple Notes, and
  [machine.py](lib/machine.py) records the machine.

## The tests

Every app gets the same made-up notes: 1,000 Markdown files of about 1.5 KB each, with headings,
tasks, bold and italic. noted, Obsidian and VS Code open the folder; vim, Emacs and Neovim open one
note of it at a time. Apple Notes runs on the owner's own library: see below.

| Test | What's timed | Samples |
|---|---|---|
| **Launch** | From starting the app until it's ready: noted's first full screen, Apple Notes' window on screen, Obsidian's workspace laid out, VS Code's workbench restored (its own `Restored` mark), and vim's, Emacs' and Neovim's first screen with the note, once they draw nothing more. | 20 launches (Apple Notes, Obsidian and VS Code: 7), after one that isn't counted |
| **Memory** | Physical footprint, the number Activity Monitor shows, added up over every process of the app, once it's ready. | Every launch for noted, vim, Emacs and Neovim; 1 for Apple Notes, Obsidian and VS Code, once they've settled |
| **Size on disk** | The app as installed. noted: its one program, a universal binary for Apple silicon and Intel. Apple Notes: Notes.app and the nine frameworks only it uses (their code, which macOS keeps in its shared cache, and their resources). Obsidian and VS Code: their apps. vim: `/usr/bin/vim` and its runtime files. Emacs and Neovim: as Homebrew installs them, without the libraries they share with other programs. | 1 |
| **Open a note** | noted: `↓` in its notes list, which opens the next note. Obsidian: its quick switcher (`⌘O`), the note's name, then `Enter`. VS Code: Quick Open (`⌘P`), the note's name, then `Enter` (first `↓` to the note, if another ranks above it). vim and Neovim: `:e note.md`. Emacs: `C-x C-f note.md`. Timed from the key that opens it, `↓` or `Enter`. | 20 notes |
| **Type a key** | A letter typed at the end of a 1.5 KB note. | 40 keys |
| **Long note** | A note of 30,000 lines: letters typed at its end, and at the start of its second line. | 40 keys at each place |

Apple Notes has only launch, memory and size. Typing into it would need permissions for the
benchmark (Accessibility), and its notes are its owner's own: they're never read or changed. It's
opened as the Dock opens it, through Launch Services, and if Notes is already open it isn't measured
at all, so nothing of anyone's is closed.

## How it's timed

- **In a terminal.** noted, vim, Emacs and Neovim run on a pseudo-terminal of 120 × 40 cells, with
  `TERM=xterm-256color`. That's real bytes in and the screen they draw out, as in any terminal.
  - A key is timed from writing it to the last byte drawn in answer, before 30 ms without output.
  - A launch is timed from starting the program to the last byte before 300 ms without output.
  - Not timed: a terminal turning those bytes into pixels, which costs the same for every program.
- **Questions a terminal answers.** Programs ask a terminal about itself when they start: its
  attributes, the cursor's position, its colors. Emacs, for one, waits up to 2 seconds for replies.
  The benchmark answers each question as a terminal would, so no program waits.
- **Emacs' controlling terminal.** Emacs wants a controlling terminal, which macOS hands a process
  only through a system call. So it starts through a tiny helper that makes that call and then runs
  Emacs. The helper's own cost (about 1 ms) is measured in the same sitting and taken off Emacs'
  launch. Both numbers are kept.
- **Obsidian** runs as a second copy, in a throwaway profile that opens a vault of the same notes,
  so nobody's own Obsidian is touched. Background throttling is off, as for a window in use.
  - Keys are real: sent through Chrome's DevTools protocol as key events.
  - Each key is timed inside the page, from its `keydown` until the change is in the page, watched
    by a `MutationObserver`.
  - Obsidian's clock has a resolution of 0.1 ms.
- **VS Code** is driven the same way: a second copy, in a throwaway profile with no extensions,
  opening a folder of the same notes. Its profile turns off what would stand between it and the
  notes: the welcome page, the prompt to trust the folder, update and release-notes checks, and
  telemetry. Where the release isn't installed, VS Code Insiders runs, the same editor a few weeks
  ahead; each sitting records which.
  - VS Code puts a typed letter on the page at the next animation frame, so its times include that
    wait, where Obsidian's change is in the page at once, before the frame that shows it.
- **Apple Notes** is timed from `open -a Notes` until its window is on screen. That's a lower bound:
  its list may still be filling.
- **Settings.** Every app has its default settings and a home (or profile) of its own, so nobody's
  configuration counts. No plugins or extensions. Each app keeps that home from one launch to the
  next, caches and all, as on anyone's Mac: the first launch, which sets it up, isn't counted.
- **The processor kept awake.** One low-priority busy loop runs throughout. On an idle Mac, macOS
  takes about 5 ms longer to start any program, every app here included.
- **Medians.** Each multiplier on the site is noted's median against the best median of the other
  apps measured in the same sitting.
- **noted's memory on the site** is the larger of two numbers from the same sitting: noted.py's, 2
  seconds after launch, once noted has read its notes ahead for finding, rather than compare.py's,
  as soon as it's ready.

## What it doesn't say

- **Different jobs.** noted opens a folder of notes; vim, Emacs and Neovim open one file, and VS
  Code is an editor for code. They're compared on what they all do: starting up and showing notes,
  opening another, typing.
- **One Mac.** The numbers are from one Mac, recorded in each results folder; another Mac will give
  other numbers. Results from a busy machine, or one on battery, are slower and noisier, and
  `compare.py` says so when that's the case.
- **Defaults only.** Each app is measured as it comes. Neovim's defaults, for one, include Markdown
  highlighting; a tuned configuration of any of them would give other numbers.

## Run it yourself

On macOS, with Python 3.9 or newer (macOS has it), Xcode's command-line tools (`xcode-select
--install`), Obsidian and VS Code in `/Applications`, and Emacs from Homebrew (`brew install emacs`;
`neovim` too, for `--apps neovim`). Plugged in, with nothing else busy:

```sh
python3 compare.py --noted "$(command -v noted)"          # every app: about 10 minutes
python3 compare.py --noted "$(command -v noted)" --apps noted,vim,neovim,emacs
python3 compare.py --noted "$(command -v noted)" --quick  # a few samples, to try it
python3 noted.py "$(command -v noted)"                    # noted alone
```

The results go to `results/<date>-<noted version>/`. Only Python's standard library is used.
