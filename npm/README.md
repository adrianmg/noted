<p align="center">
	<h1 align="center">
		<img src="https://raw.githubusercontent.com/adrianmg/noted/main/docs/logo.png" alt="noted's logo: a floppy disk" width="128">
		<br>
		noted
	</h1>
	<p align="center">Markdown notes in your terminal, as if they ran on MS-DOS.<br>Opens in 2.5 ms, saves as you type, keeps every note as a plain Markdown file.</p>
	<p align="center">
		<a href="https://www.npmjs.com/package/@adrianmg/noted"><img src="https://img.shields.io/npm/v/%40adrianmg%2Fnoted?label=npm&color=0000aa" alt="npm version" height="18"></a>
		<a href="https://github.com/adrianmg/noted/releases"><img src="https://img.shields.io/github/v/release/adrianmg/noted?label=release&color=00aaaa" alt="Latest release" height="18"></a>
		<a href="https://noted.computer"><img src="https://img.shields.io/badge/website-noted.computer-ffff55" alt="Website: noted.computer" height="18"></a>
	</p>
</p>

<p align="center">
	<br>
	<img src="https://raw.githubusercontent.com/adrianmg/noted/main/docs/demo.gif" alt="noted starting from the shell: a new note with a task list, ticking a task, the notes list, finding a note as you type, then the Amber theme" width="720">
	<br>
</p>

## Installation

```sh
# npm: macOS, Linux and Windows (Node 18 or newer)
npm install -g @adrianmg/noted

# Homebrew: macOS and Linux
brew tap adrianmg/noted https://github.com/adrianmg/noted
brew trust adrianmg/noted
brew install noted

# Install script: checks the build against the release's checksums
curl -fsSL https://noted.computer/install | sh      # macOS, Linux
irm https://noted.computer/install.ps1 | iex        # Windows, in PowerShell
```

If npm warns that an install script was blocked, noted is still installed:
run `noted`. The optional script improves startup speed on macOS and Linux.
To allow that optimization, reinstall with an npm version that supports
`--allow-scripts`:

```sh
npm install -g @adrianmg/noted --allow-scripts=@adrianmg/noted
```

## Usage

```sh
noted                     # a new note, cursor ready
noted buy oat milk        # a new note that starts with those words
noted --theme amber       # turbo, amber, phosphor, charcoal, lime, midnight,
                          # c64, catppuccin, gruvbox, kanagawa, solarized,
                          # synthwave
noted --dir ~/Notes       # keep notes in another folder this time
noted --path              # print where your notes are
noted --help              # every option
```

## Import existing notes or change location

Already have notes in Obsidian, iA Writer, or another app that saves
Markdown? Open their folder with `--dir`; quote paths with spaces:

```sh
noted --dir ~/Notes
noted --dir "$HOME/Documents/My Notes"
```

Existing notes open in place, including notes in nested folders, and new
notes are saved there. There is no separate import or conversion step.
`--dir` applies only to this run: it does not change the default or move
notes from your previous folder.

To change the default permanently, use Noted ▸ Notes folder…. The current
location is shown read-only, and "Folder to use" starts with that path.
**Use new folder** becomes available when you choose a valid, different
location. **Bring existing notes from '…'** then lets you move your current
notes along, or leave them where they are by unticking it. Existing notes
in the chosen folder appear either way; Cancel changes nothing.

## What it does

noted opens on a new note in about 2.5 ms, answers each key in under 0.1 ms
(about 0.1 ms in a 30,000-line note), and saves as you type, so there's no
save button and nothing to lose. Each note is a plain Markdown file named
after its first line, in a `Noted` folder in iCloud Drive when it's on, or
else in Documents, where any editor can open it: `noted --path` prints where,
and Noted ▸ Notes folder… chooses where notes open and save. Markdown is lit as you type,
finding searches every note as you type, and it all looks like MS-DOS:
pull-down menus, Norton Commander panes and twelve themes. It runs on macOS,
Linux and Windows, in any terminal.

How it compares with Apple Notes, Obsidian, VS Code, vim and Emacs, measured
on one Mac with every sample published: [benchmarks](https://github.com/adrianmg/noted/tree/main/benchmarks).

## Keys

| Key | |
|---|---|
| `ESC` | Notes list, and back |
| `⌘F` or `^F` | Find a note, or create one |
| `^N` | New note |
| `^T` | Make a task, tick it |
| `^G` | Insert a table |
| `^D` | Delete the note (to the Trash; `^Z` puts it back) |
| `F10` | Menus |
| `F1` | Every key |
| `^Q` | Exit |

On a PC, read `⌘` as `^` and `⌥` as `ALT`.

### Vim keys

Options ▸ Vim keys (`⌥O` then `m`) turns the note modal, as in vim. It's off
until you turn it on. The footer shows the mode, and the cursor is a bar in
Insert mode. A new note starts in Insert mode, an opened one in Normal.

| Key | |
|---|---|
| `i` `a` `I` `A` `o` `O` | Insert mode; `ESC` leaves it |
| `h` `j` `k` `l` `w` `b` `e` `0` `^` `$` `gg` `G` `f` `t` `{` `}` `%` | Move, with counts: `3w` `5j` |
| `d` `c` `y` | With a motion or a text object: `dw` `c$` `yy` `dd` `ciw` `ci"` `da(` |
| `x` `D` `C` `s` `p` `P` `r` `~` `J` `>>` `<<` | As in vim |
| `u` `^R` | Undo, redo; a whole insert is one step |
| `/` | noted's find, across all your notes |

In the notes list, `j` `k` go down and up. It's the core of vim, checked
against vim itself, not all of it: there's no Visual mode (`v`), `.`,
registers, marks, macros or `:` commands, and a key vim has that this
doesn't says so in the footer. `^` keys stay noted's, so `^F` finds and `^D`
deletes a note.

## Updating

```sh
npm install -g @adrianmg/noted     # npm
brew upgrade noted                 # Homebrew
```

With the install scripts, run them again.

## Why?

A thought is gone in seconds, and most notes apps take longer than that to
open. noted is a terminal away, ready before you finish pressing Enter, and
leaves you nothing but plain files in a folder you own.

Do you want to know more? [Visit noted.computer](https://noted.computer),
with a live demo and the User's Guide.

## Questions? Ideas? Bugs?

[Open an issue](https://github.com/adrianmg/noted/issues) or hit me
up on [Twitter](https://twitter.com/adrianmg).

This repository holds noted's releases, its Homebrew formula and this README;
the npm package, [@adrianmg/noted](https://www.npmjs.com/package/@adrianmg/noted),
ships the same builds, and is published from here, with provenance. To report
a vulnerability, see [SECURITY.md](https://github.com/adrianmg/noted/blob/main/SECURITY.md).

## License

Made by [Adrián Mato](https://adrianmato.com). Available under the terms of
the [MIT License](https://github.com/adrianmg/noted/blob/main/LICENSE).
