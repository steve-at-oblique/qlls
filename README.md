# LS for Sinclair QL

LS is a native 68000 directory listing job for QDOS. By default, it
sorts filenames in ascending, case-insensitive order and prints each name with
its original capitalization. The size, date, and filename fields are separated
by one space. Sizes are right-aligned in a field of at least six columns.
Sizes over 999999 bytes are divided by 1024 and rounded down, with the
trailing `K` counted as part of the field. Directories show zero bytes and a trailing ` ->` when the
driver reports a directory entry. A zero timestamp is shown as a centered
`-` in the 16-character date field.

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

The 1416-byte transfer file contains a 30-byte header and the 1386-byte executable.
The header specifies QDOS file type 1 and 512 bytes of data space.

Stock QDOS lists `MDV1_`. With Toolkit II or SMSQ/E, LS reads the current
`DATA_USE` instead. LS writes a newline and then the listing to the main
BASIC job’s channel `#1`, the default output channel for `DIR`.

## Command-line options

With Toolkit II or SMSQ/E, pass a command string to `EW` or `EXEC_W`.

```basic
EW SNL4_ls;"-nr snl1_"
EW SNL4_ls;"-sr"
EW SNL4_ls;"-tr win1_docs_"
```

- `-n` sorts by name, A–Z.
- `-s` sorts by size, smallest first. Directories count as zero bytes.
- `-t` sorts by modification date, newest first. An absent date sorts oldest.
- `-r` reverses the selected field’s default direction.

Combine options or pass them separately. The last field option selects the
sort field. Equal keys preserve directory order. Supply one device or
directory to override the default. Keep the native device and directory
prefix, including its trailing underscore. For a path containing spaces,
enclose the path in double quotes inside a single-quoted BASIC string, as in
`EW SNL4_ls;'-t "WIN1_My Files_"'`.

## Resident BASIC command

Transfer `ls_rext` as a raw binary and transfer `ls` as a QDOS executable.
Load the extension once per boot with Toolkit II or SMSQ/E.

```basic
LRESPR win1_ls_rext
LS_USE "win1_ls"
LS win1
LS win1_,"-s"
LS snl4,"-tr"
```

`LS_USE` sets the full filename of the job. It defaults to `win1_ls`, and
the job can live on a different drive from the extension or the directory
being listed. `LS win1` and `LS win1_` select the same drive. The same syntax
works for other available drives, such as `LS flp1_` and `LS snl4_`.
Quote paths containing spaces. Pass sort options as quoted BASIC arguments,
separated by commas. Combined options such as `"-nr"` work, as do separate
options such as `LS win1_,"-n","-r"`. With no directory argument, `LS` uses
the job's default directory. The command waits for the listing to finish.
The original resident extension passed on QIMSI and on a physical 128K
Sinclair QL.

## Build with Talent/Quanta Assembler Workbench 2.02

Copy `ls_asm` as plain text. In the monitor, enter the following commands. Replace `FLP1_` with the drive holding the assembler and use the appropriate paths for the source and output.

```text
ASM 0 FLP1_
OUT FLP1_ls_bin
INCLUDE FLP1_ls_asm
```

The source ends the assembly. The current build occupies 1386 bytes starting
at address zero. From SuperBASIC, save it with the required 512-byte data space:

```basic
a=RESPR(1386)
LBYTES FLP1_ls_bin,a
SEXEC FLP1_ls,a,1386,512
```

To build the raw resident extension, use `OUT FLP1_ls_rext` and
`INCLUDE FLP1_ls_rext_asm` in the workbench. Load the output with `LRESPR`.

The command-line build was tested in sQLux with the Sinclair JS ROM at
128K, with and without Toolkit II, and with Minerva plus Toolkit II. It
also passed on a physical Sinclair QL and on QIMSI Gold.
