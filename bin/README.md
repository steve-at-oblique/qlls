# Ready-built QL files

Copy `ls_rext` in binary mode to `win1_ls_rext`. Transfer `ls` to `win1_ls`
using a tool that interprets its inline QDOS header and preserves the native
executable type and dataspace.

```basic
LRESPR win1_ls_rext
LS_USE "win1_ls"
LS win1_
```

The extension is raw resident code with no executable wrapper or XTcc trailer.
Use the full executable filename with `LS_USE`. Reboot before reloading a
changed extension.

For SNL4, copy both files to the host share and load `LRESPR snl4_ls_rext`.
The extension defaults to launching `snl4_ls`.

See the [main README](../README.md) for transfer details, options and build
instructions.

The ls program is GPL-1.0-or-later; see ../LICENSE.md and ../COPYING. The
separate resident launcher retains its BSD-2-Clause notice; see
../LICENSES/BSD-2-Clause.txt. Distribute these binaries with the source and
license notices from this repository.
