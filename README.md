# QLLS: sorted directory listings for the Sinclair QL

A qdos-gcc port of Hans-Peter Sulzer's 1992 QDOS ls, with sorting, compact file
sizes/dates, QL directory markers, and a resident SuperBASIC `LS` command.
The supplied original printed directory entries in storage order; this version
sorts the displayed listing without rearranging the directory on disk.

## Install

Ready-built files are in **bin/**:

- **bin/ls**: the executable, packaged with the QDOS header wrapper understood
  by SNL, like qlvi's Elvis executable.
- **bin/ls_rext**: the resident SuperBASIC command extension.

Copy both files into the host share served as SNL drive 4, keeping their names.
Load the command once per boot:

```basic
LRESPR snl4_ls_rext
```

You can put that line in your `win1_` BOOT sequence **after SNL is ready**.
The SNL daemon must be running when the files are loaded. The resident command
launches `snl4_ls`; if you move the executable elsewhere, change the embedded
name and its length at the end of `ls_rext.s` and rebuild.

```basic
LS win1_
LS snl1_
LS win1_,"-s"
LS win1_,"-t"
LS win1_,"-S"
LS win1_,"-s","-x"
LS "-?"
```

Paths need no quotes unless they contain spaces. Pass options as separate quoted,
comma-separated arguments. String variables work: `d$="win1_": LS d$,"-s"`.
Output uses existing SuperBASIC window #1 and waits until finished. The extension
leaves #1 open and does not create a new window. `LS` alone lists the current
DATA_USE directory, so `DATA_USE snl4_` followed by `LS` lists SNL4.

Load the extension only once per boot. Reboot before loading a replacement
`ls_rext`; replacing just `ls` needs no reboot or extension reload.

## Output and options

The default is a compact alphabetical listing, ignoring ASCII letter case:

```text
boot          177  2026 Nov 16 17:18
docs ->      1024  2026 Nov 15 20:55
```

A directory has ` ->` after its name in every output format. One blank line
precedes a nonempty listing; there is no extra blank line afterward. Sizes are
bytes excluding the 64-byte QDOS file header. Modification dates omit seconds;
a missing date is shown as `-`.

| Option | Meaning |
| --- | --- |
| `-s` | Short: names only, one per line |
| `-l` | Explicitly select the default name/size/date format |
| `-x` | Names only, in columns across the screen |
| `-r` | Reverse the selected sort order |
| `-t` | Newest modification date first |
| `-S` | Largest file first |
| `-T0` | All files (default) |
| `-T1` | Data files |
| `-T2` | Programs |
| `-T4` | Directories |
| `-?` | Help |

The last of `-s`, `-l`, and `-x` selects the format. The last of `-t` and `-S`
selects the sort; alphabetical order breaks ties. Names with numbers use ordinary
alphabetical ordering, not natural numeric ordering. Accented characters use
byte ordering, not locale collation. Sorting uses the filename without its marker.

Supply one device, directory, filename or wildcard expression. `-e-name` retains
the original syntax for an operand beginning with a hyphen. The resident launcher
accepts up to 16 arguments and a total quoted command length of 255 bytes; quotes
and control characters inside arguments are rejected.

Without the resident extension, use Toolkit II/SMSQ/E:

```basic
EW snl4_ls,#1,#1,#1;"win1_"
EW snl4_ls,#1,#1,#1;"-s -r win1_"
```

Use a semicolon before the quoted parameter string. Starting `ls` without inherited
channels opens its own console, which waits for SPACE or ENTER before closing.
The root source file `ls_c` retains QDOS-style naming; `ls_original_c` is the
unmodified upstream source.

## Build and test

The qdos-gcc toolchain must be on PATH. Python 3 is used for packaging and tests.

```sh
make
make test
```

Or specify a compiler path:

```sh
make QDOS_CC=/path/to/qdos/bin/qdos-gcc
```

`make` builds the ready-to-copy files in `bin/`. Intermediate objects and the
raw, unwrapped executable are in ignored `build/`. The build uses qdos-gcc 2.95.3
with `-O2 -Wall` and its default QL 68000 target. The linked library supplies
`cn_date`; the original binary-only `cndate_o` module is neither included nor used.

Optional integration checks:

```sh
SNL_SERVER=/path/to/snldriver/snl_serial make test
python3 -m pip install unicorn
make test-launcher
```

Host tests compile the application with mocked QDOS I/O. They check name,
reverse/date/size sorting, filenames from an actual WIN1 listing, empty and large
directories, 36-character names, compact details, short/column output, directory
markers, help, spacing and errors. The optional SNL test reads real server
directory records and verifies executable metadata and visible code bytes.

Launcher tests execute the assembled 68000 code with Unicorn and mocked ROM/QDOS
calls. They check registration, arguments and string expressions, SuperBASIC
relocation, inherited #1 channels, waiting, stack limits and failure cleanup.
They do not emulate the complete QDOS ROM, driver or scheduler.

## Implementation and verification notes

- Sorted listings retain complete 64-byte directory headers in memory; capacity
  grows geometrically. Very large directories require additional free RAM.
- A local Shell sort avoids a callback into GCC code from the C68 assembler
  library. ASCII case folding avoids the shared temporary in C68's tolower macro.
- SNL directory opens omit wildcard characters; the C68 reader applies the
  original pattern afterward. Opening SNL's literal `*` prefix yields no entries.
- File metadata comes from directory records. Standard directory type 255 and
  length-validated legacy CST/Thor directory types are recognized.
- This is a small QDOS utility: no recursion, multiple directory operands,
  natural numeric sorting, hidden host-file enumeration or pagination.
- The user has verified WIN and SNL listings and use of the resident command on
  a QL. Later changes also have host tests; the full hardware/ROM matrix has not
  been tested. No physical QL is connected to the development environment.

## License and attribution

Original program: Copyright (c) 1992 HaPeSu (Hans-Peter Sulzer).
The author's accompanying PDF releases it under **GNU GPL version 1 or newer**
(SPDX: GPL-1.0-or-later), although the original C header has no license grant.
See [LICENSE.md](LICENSE.md), [COPYING](COPYING), and the preserved upstream
[documentation](docs/ls%20Program%20for%20QDOS.pdf).

The 2026 port adds sorting, output formats, directory markers and SNL support;
it also updates C68 declarations/startup variables, fixes unsafe padding and
formatting, and adds build scripts and tests. The original attribution is kept.

The separate resident launcher, launcher tests and packaging script derive from
Steve Jennen's qlvi additions and retain their BSD-2-Clause notices. See
[LICENSES/BSD-2-Clause.txt](LICENSES/BSD-2-Clause.txt). Those notices do not
relicense Sulzer's ls. Redistribute the binaries with the corresponding source,
build scripts, attribution and license notices from this repository.
