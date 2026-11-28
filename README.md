# LS for Sinclair QL

LS is a native 68000 directory listing job for QDOS and SMSQ/E. By default, it
sorts filenames in ascending, case-insensitive order and prints each name with
its original capitalization. The size, date, and filename fields are separated
by one space. Sizes are right-aligned in a field of at least six columns.
Sizes over 999999 bytes are divided by 1024 and rounded down, with the
trailing `K` counted as part of the field. Directories show zero bytes and a trailing ` ->` when the
driver reports a directory entry. Executable programs (QDOS file type 1) show a
trailing `*`. A zero timestamp is shown as a centered `-` in the 16-character
date field.

LS stores directory entries in packed, job-owned heap blocks. If QDOS runs
out of memory while collecting entries, LS closes the directory, releases
the blocks, and returns the QDOS error without printing a partial listing.
Entries already in the selected order append at the tail, so a sorted input
takes one comparison per entry after the first.

## Install and run

Copy `ls` from the project root in binary mode to your SNL drive. For example:

```basic
EXEC_W SNL1_ls
```

The 1890-byte transfer file contains a 30-byte header and the 1860-byte executable.
The header specifies QDOS file type 1 and 512 bytes of data space.
For installation directly on a QL, extract `ls_zip` with QL-aware UnZip
to restore the executable metadata.

Stock QDOS lists `MDV1_`. With Toolkit II or SMSQ/E, LS reads the current
`DATA_USE` instead. By default, LS writes a newline and then the listing to the main
BASIC job’s channel `#1`, the default output channel for `DIR`.
Each listing starts with a left-aligned header showing the search specification
followed by a colon. The header appears in every output mode, even when no
files match. With no search operand, the header shows the default directory.

## Command-line options

With Toolkit II or SMSQ/E, pass a command string to `EW` or `EXEC_W`.
The stock QDOS ROM's `EXEC` and `EXEC_W` do not pass that string to the job.

```basic
EW SNL4_ls;"-nr snl1_"
EW SNL4_ls;"-sr"
EW SNL4_ls;"-tr win1_docs_"
EW SNL4_ls;"-1 win1_"
EW SNL4_ls;"snl1_a"
EW SNL4_ls;"#3,snl1_"
EW SNL4_ls,#3;"-1 snl1_"
```

- `-1` prints bare filenames only, one per line, without sizes, dates, or type indicators.
- `-n` sorts by name, A–Z.
- `-s` sorts by size, smallest first. Directories count as zero bytes.
- `-t` sorts by modification date, newest first. An absent date sorts oldest.
- `-r` reverses the selected field’s default direction.
- `#n` redirects output to an open SuperBASIC channel `#n` (with an optional comma or space before the path). Passing an open channel directly to `EW` or `EXEC_W` (such as `EW SNL4_ls,#3;"snl1_"`) is also supported.

When redirecting to a file, use `EW` or `EXEC_W` so the listing finishes
before you close the output channel.

Combine options or pass them separately. The last field option selects the
sort field. Equal keys preserve directory order. Supply one device or
directory to override the default. Keep the native device and directory
prefix, including its trailing underscore. Append a filename prefix
such as `snl1_a` or `win1_docs_a` to filter that directory case-insensitively,
or supply a bare filename prefix to filter the default directory.
For a path containing spaces, enclose the path in double quotes inside a
single-quoted BASIC string, as in `EW SNL4_ls;'-t "WIN1_My Files_"'`.

## Resident BASIC command

Transfer the 974-byte `ls_rext` as a raw binary and transfer `ls` as a QDOS
executable.
With Toolkit II or SMSQ/E, load the extension once per boot with `LRESPR`.

```basic
LRESPR win1_ls_rext
LS_USE "win1_ls"
LS win1
LS win1_,"-s"
LS snl4,"-tr"
```

On stock QDOS without Toolkit II, load the extension and redirect a
listing with these commands:

```basic
a=RESPR(974)
LBYTES SNL6_ls_rext,a
CALL a
LS_USE "SNL6_ls"
OPEN_NEW #3,SNL5_lsout_txt
LS snl6_q,"#3"
CLOSE #3
```

`LS_USE` sets the full filename of the job. It defaults to `win1_ls`, and
the job can live on a different drive from the extension or the directory
being listed. `LS win1` and `LS win1_` select the same drive. The same syntax
works for other available drives, such as `LS flp1_` and `LS snl4_`.
Quote paths containing spaces. Pass sort options and channel overrides as
quoted BASIC arguments, separated by commas. Combined options such as
`"-nr"` work, as do separate
options such as `LS win1_,"-n","-r"`. With no directory argument, `LS` uses
the job's default directory. The command waits for the listing to finish.
The original resident extension passed on QIMSI and on a physical 128K
Sinclair QL.

## Build with Talent/Quanta Assembler Workbench 2.02

Copy `ls_asm` and `ls_rext_asm` to the QL as plain text. The examples use
`snl6` as the drive holding the assembler and `snl6_` as the filename
prefix. Substitute your own drive and filenames as needed. The prompts
`cmd>` and `asm>` show where to enter each command.

### Assemble the executable

```text
cmd> heap &3000
cmd> asm <start> snl6_
asm> in snl6_ls_asm
cmd> sexec snl6_ls <start> <end> &512
```

Use the address returned by `heap` for `<start>` and the assembled end
address for `<end>`. The source's `END` directive returns you to the
monitor. `sexec` saves a QDOS executable and `&512` sets its data space
to 512 bytes.

### Assemble the resident extension

```text
cmd> heap &3000
cmd> asm <start> snl6_
asm> in snl6_ls_rext_asm
cmd> sbytes snl6_ls_rext <start> <end>
```

Use the heap address and assembly end address from this build. `sbytes`
saves the raw extension for `LRESPR` or `LBYTES`.

After compiling either binary, copy the updated build into this checkout
and run `make ls_zip` before committing. The archive includes both binaries
and the license. Use QL-aware UnZip to restore the executable metadata.
For Mac or Linux transfers via SNL, use the standalone `ls` with its inline
QDOS header.

Version 1.1.1 passed on a physical 128K Sinclair QL running stock QDOS and
on SMSQ/E. It was also tested in sQLux with the Sinclair JS ROM at 128K,
with and without Toolkit II, and with Minerva plus Toolkit II.
