# noted benchmark: 2026-10-27, noted 1.1.0

**Machine.** MacBook Pro (Mac16,6), Apple M4 Max (10 performance and 4 efficiency cores), 36 GB, macOS 15.7.3 (24G419). AC Power. Load average 3.5 before, 5.1 after, with one low-priority busy loop keeping the processor awake.

**Apps.** noted 1.1.0, Apple Notes 4.12.7, Obsidian 1.8.10, VS Code Insiders 1.125.0, vim 9.1, Emacs 31.1, default settings.

**Notes.** 1,000 made-up Markdown notes of about 1.5 KB. 

## Medians

| | noted | Apple Notes | Obsidian | VS Code | vim | Emacs |
|---|---|---|---|---|---|---|
| Launch | 2.6 ms | 370 ms | 500 ms | 681 ms | 9.5 ms | 30 ms |
| Memory | 5.1 MB | 73.1 MB | 382 MB | 770 MB | 3.5 MB | 14.8 MB |
| Size on disk | 2.5 MB | 34.5 MB | 441 MB | 767 MB | 26.7 MB | 133 MB |
| Open a note | 0.28 ms | – | 4.3 ms | 27 ms | 0.83 ms | 1.7 ms |
| Type a key | 0.075 ms | – | 1.2 ms | 7.0 ms | 0.16 ms | 0.46 ms |
| Long note, type at the start | 0.10 ms | – | 1.2 ms | 5.5 ms | 0.14 ms | 0.34 ms |
| Long note, type at the end | 0.076 ms | – | 0.90 ms | 5.3 ms | 0.13 ms | 0.34 ms |

Emacs' launch is shown less the 1.32 ms its controlling-terminal helper takes on its own (raw median 30.9 ms).

## Every test

| App | Test | n | Median | p95 | Min | Max |
|---|---|---|---|---|---|---|
| noted | launch | 20 | 2.578 ms | 3.577 | 2.408 | 5.044 |
| noted | launch, first full frame | 20 | 2.578 ms | 3.577 | 2.408 | 5.044 |
| noted | memory | 20 | 5.149 MB | 5.688 | 4.688 | 5.688 |
| noted | processes | 1 | 1.000  | 1.000 | 1.000 | 1.000 |
| noted | type a key | 40 | 0.075 ms | 0.102 | 0.056 | 0.184 |
| noted | open a note | 20 | 0.284 ms | 0.338 | 0.234 | 0.364 |
| noted | long note, type at the end | 40 | 0.076 ms | 0.111 | 0.059 | 0.146 |
| noted | long note, type at the start | 40 | 0.100 ms | 0.156 | 0.075 | 0.213 |
| noted | size | 1 | 2.458 MB | 2.458 | 2.458 | 2.458 |
| Apple Notes | size | 1 | 34.453 MB | 34.453 | 34.453 | 34.453 |
| Apple Notes | launch | 7 | 369.888 ms | 374.533 | 358.759 | 374.533 |
| Apple Notes | busy after its window | 1 | 4.372 s | 4.372 | 4.372 | 4.372 |
| Apple Notes | memory | 1 | 73.126 MB | 73.126 | 73.126 | 73.126 |
| Apple Notes | processes | 1 | 1.000  | 1.000 | 1.000 | 1.000 |
| Obsidian | size | 1 | 440.566 MB | 440.566 | 440.566 | 440.566 |
| Obsidian | launch | 7 | 500.245 ms | 574.882 | 484.040 | 574.882 |
| Obsidian | busy until, from launch | 1 | 3.143 s | 3.143 | 3.143 | 3.143 |
| Obsidian | memory | 1 | 381.942 MB | 381.942 | 381.942 | 381.942 |
| Obsidian | processes | 1 | 4.000  | 4.000 | 4.000 | 4.000 |
| Obsidian | open a note | 20 | 4.300 ms | 5.700 | 3.700 | 17.900 |
| Obsidian | type a key | 40 | 1.200 ms | 1.400 | 0.900 | 4.100 |
| Obsidian | long note, type at the end | 40 | 0.900 ms | 22.400 | 0.800 | 24.700 |
| Obsidian | long note, type at the start | 40 | 1.200 ms | 1.400 | 1.000 | 2.100 |
| VS Code | size | 1 | 767.352 MB | 767.352 | 767.352 | 767.352 |
| VS Code | launch | 7 | 681.382 ms | 698.803 | 659.751 | 698.803 |
| VS Code | busy until, from launch | 1 | 13.204 s | 13.204 | 13.204 | 13.204 |
| VS Code | memory | 1 | 770.041 MB | 770.041 | 770.041 | 770.041 |
| VS Code | processes | 1 | 8.000  | 8.000 | 8.000 | 8.000 |
| VS Code | open a note | 20 | 26.950 ms | 35.000 | 24.300 | 35.700 |
| VS Code | type a key | 40 | 7.000 ms | 8.400 | 3.200 | 8.500 |
| VS Code | long note, type at the end | 40 | 5.300 ms | 8.500 | 1.700 | 8.600 |
| VS Code | long note, type at the start | 40 | 5.550 ms | 8.600 | 1.900 | 12.100 |
| vim | processes | 1 | 1.000  | 1.000 | 1.000 | 1.000 |
| vim | launch | 20 | 9.477 ms | 10.896 | 8.671 | 11.900 |
| vim | memory | 20 | 3.539 MB | 4.125 | 3.391 | 4.282 |
| vim | type a key | 40 | 0.160 ms | 0.186 | 0.116 | 0.199 |
| vim | open a note | 20 | 0.828 ms | 1.045 | 0.658 | 1.047 |
| vim | long note, type at the end | 40 | 0.127 ms | 0.196 | 0.070 | 0.213 |
| vim | long note, type at the start | 40 | 0.137 ms | 0.187 | 0.084 | 0.224 |
| vim | size | 1 | 26.730 MB | 26.730 | 26.730 | 26.730 |
| Emacs | processes | 1 | 1.000  | 1.000 | 1.000 | 1.000 |
| Emacs | launch | 20 | 30.940 ms | 32.593 | 27.807 | 37.896 |
| Emacs | memory | 20 | 14.774 MB | 15.375 | 13.938 | 15.563 |
| Emacs | type a key | 40 | 0.462 ms | 0.513 | 0.415 | 0.555 |
| Emacs | open a note | 20 | 1.748 ms | 5.250 | 1.530 | 6.028 |
| Emacs | long note, type at the end | 40 | 0.338 ms | 0.419 | 0.244 | 0.461 |
| Emacs | long note, type at the start | 40 | 0.339 ms | 0.429 | 0.244 | 0.463 |
| Emacs | size | 1 | 133.141 MB | 133.141 | 133.141 | 133.141 |
| Emacs | launch, less the helper | 20 | 29.621 ms | 31.274 | 26.488 | 36.577 |
