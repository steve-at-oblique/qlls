# QLLS: sorted directory listings for the Sinclair QL

A qdos-gcc port of Hans-Peter Sulzer's 1992 QDOS ls, with sorting, compact file
sizes/dates, QL directory markers, and a resident SuperBASIC `LS` command.
The supplied original printed directory entries in storage order; this version
sorts the displayed listing without rearranging the directory on disk.

## Install

Download the two ready-built files from [bin/](bin/). You can install them on
WIN1 with Toolkit II's `LRESPR`, or the equivalent command in SMSQ/E.

1. Copy [ls_rext](bin/ls_rext) in binary mode to `win1_ls_rext`. It is raw
   resident code with no executable wrapper or XTcc trailer.
2. Transfer [ls](bin/ls) to `win1_ls` as a QDOS executable. The download has
   an inline QDOS header. Use a transfer tool that interprets the wrapper and
   sets the native executable type and dataspace on WIN1.
3. Load the extension, set the executable path, and try a listing.

```basic
LRESPR win1_ls_rext
LS_USE "win1_ls"
LS win1_
```

This setup was tested on a physical QL with both files on WIN1 and the SNL
daemon stopped.

`LS_USE` takes the full filename of the executable. For example, use
`LS_USE "win2_tools_ls"` if you installed it there. Put `LRESPR` followed by
`LS_USE` in your BOOT file to configure it each boot.

If `LRESPR` succeeds but `LS` fails, try
`EW win1_ls,#1,#1,#1;"win1_"` to check whether QDOS can run the executable
directly. If that fails too, check the file's executable metadata and transfer
method. See [QDOS file header formats](https://www.kilgus.net/2021/11/13/a-short-history-of-qdos-file-headers/).

For an SNL installation, copy both files to the SNL4 host share and run
`LRESPR snl4_ls_rext` once SNL is ready. The built-in executable path is
`snl4_ls`, so that setup can omit `LS_USE`.

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
