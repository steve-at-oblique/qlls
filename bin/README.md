# Ready-built QL files

Copy `ls` and `ls_rext` to the host share served as SNL drive 4. Keep these names:
the resident LS command launches `snl4_ls`.

Load once per boot, after SNL is ready:

```basic
LRESPR snl4_ls_rext
```

Then run `LS win1_` or `LS snl1_`. The default lists names, byte sizes and
modification dates. Use `LS win1_,"-s"` for names only. Output goes to #1.

`ls` includes the QDOS wrapper understood by SNL. `ls_rext` is resident code
loaded with LRESPR, not an EX executable. Reboot before reloading a changed
resident extension; replacing only ls needs no reboot.

See ../README.md for all options, source, build and testing instructions.
The ls program is GPL-1.0-or-later; see ../LICENSE.md and ../COPYING. The
separate resident launcher retains its BSD-2-Clause notice; see
../LICENSES/BSD-2-Clause.txt. Distribute these binaries with the source and
license notices from this repository.
