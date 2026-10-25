<p align="center">
	<h1 align="center">
		<img src="https://raw.githubusercontent.com/adrianmg/noted/main/docs/logo.png" alt="noted's logo: a floppy disk" width="128">
		<br>
		noted
	</h1>
	<p align="center">Markdown notes in your terminal, as if they ran on MS-DOS.<br>Opens instantly, saves as you type, keeps every note as a plain Markdown file.</p>
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

## Installation and Usage

With Homebrew, on macOS and Linux (the tap is this repository):

```sh
brew tap adrianmg/noted https://github.com/adrianmg/noted
brew install noted
```

With npm, on macOS, Linux and Windows (Node 18 or newer):

```sh
npm install -g @adrianmg/noted
```

Or with neither: these download the build for your system, check it against
the release's checksums and put `noted` on your PATH.

```sh
curl -fsSL https://noted.computer/install | sh     # macOS, Linux
irm https://noted.computer/install.ps1 | iex       # Windows, in PowerShell
```

To start writing, run:

```sh
noted
```

More ways to start it:

```sh
noted                     # a new note, cursor ready
noted buy oat milk        # a new note that starts with those words
noted --theme amber       # turbo, amber, phosphor, charcoal, lime, midnight,
                          # catppuccin, dracula, gruvbox, rosepine, synthwave
noted --dir ~/Notes       # keep notes in another folder this time
noted --path              # print where your notes are
noted --help              # every option
```

## What it does

- **Instant.** The whole screen is drawn about 2.5 ms after you press Enter,
  even with ten thousand notes. Among a thousand, keys, opening a note and
  finding as you type each answer in under a millisecond.
- **Saved as you type.** There is no save button. Close the window whenever:
  what you typed is there.
- **Plain files you own.** One Markdown file per note, named after its first
  line (`Grocery list.md`), in a `Noted` folder in iCloud Drive, or in
  Documents. They open in Obsidian, iA Writer, the Files app or any editor.
- **Markdown, lit as you type.** Headings, bold, italics, code, links,
  quotes, task lists and tables take the theme's colors; the marks stay on
  the page, dimmed, so nothing jumps around.
- **Find as you type.** Titles that match come first, then notes that
  contain what you typed. If nothing matches, `ENTER` makes a new note.
- **Lists, tasks and tables.** `ENTER` continues a list, `^T` makes and ticks
  tasks, `^G` puts in a table that keeps its columns lined up as you type.
- **Folders.** Start a title with `work/` and the note is filed in a `work`
  folder.
- **The MS-DOS look.** Pull-down menus, Norton Commander panes, Turbo Vision
  dialogs and eleven themes, from Turbo blue and amber phosphor to Dracula
  and SynthWave '84, with optional CRT scanlines.
- **Everywhere.** macOS, Linux and Windows; Terminal, iTerm2, Ghostty, kitty,
  WezTerm, Alacritty, Windows Terminal, over SSH and in tmux. The mouse
  works too.

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

## Where your notes live

A `Noted` folder in iCloud Drive when it's on, or else in Documents:

| | With iCloud Drive | Without it |
|---|---|---|
| macOS | `iCloud Drive/Noted` | `~/Documents/Noted` |
| Windows | `iCloudDrive\Noted`, with iCloud for Windows | `Documents\Noted` |
| Linux | | `~/Documents/Noted` |

`noted --path` prints it. To keep notes somewhere else, use Noted ▸ Notes
folder…, which can move them there too. Settings are in
`~/.config/noted/settings` (`%APPDATA%\noted\settings` on Windows).

## Updating

```sh
brew upgrade noted                 # Homebrew
npm install -g @adrianmg/noted     # npm
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
ships the same builds.

## License

Made by [Adrián Mato](https://adrianmato.com). Available under the terms of
the [MIT License](https://github.com/adrianmg/noted/blob/main/LICENSE).
