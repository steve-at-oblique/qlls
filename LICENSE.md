# Licensing and provenance

## QDOS ls

The original ls program is Copyright (c) 1992 HaPeSu (Hans-Peter Sulzer).
The upstream C source contains that copyright notice but no license grant.
Peter Sulzer's accompanying document, preserved verbatim as
[ls Program for QDOS.pdf](docs/ls%20Program%20for%20QDOS.pdf), states:

> Program is published under the GNU General Public License (GPL) version 1 or newer.

Source: https://sinclairql.net/djw/shells/ls%20Program%20for%20QDOS.pdf
Retrieved November 17, 2026.

Accordingly, `ls_original_c` and the modified `ls_c` are treated as
**GPL-1.0-or-later**. The executable `ls` is built from the modified source.
`COPYING` contains the unmodified GNU GPL version 1 text obtained from
https://www.gnu.org/licenses/old-licenses/gpl-1.0.txt .

The original source is preserved unchanged in `ls_original_c`. The modified
source retains Sulzer's attribution and identifies the 2026 modifications.
README.md describes the changes, build process, tests, and packaging.
When redistributing this modified ls, retain its notices, include the license,
and comply with the applicable GPL source-distribution requirements. Source and
build/packaging scripts are provided in this project; a standalone binary does
not itself contain the corresponding source or these license documents.

## Separately licensed qlvi-derived support files

`ls_rext.s`, `tests/test_ls_rext.py`, and `package.py` were adapted/copied from
Steve Jennen's qlvi additions. Their existing Copyright (c) 2026 Steve Jennen
and BSD-2-Clause notices remain intact. The full text is in
`LICENSES/BSD-2-Clause.txt`. These notices do not relicense Sulzer's ls code.
The resident `ls_rext` binary is built from `ls_rext.s` and launches ls as a
separate QDOS job.

## Original date module

The upstream document mentions a binary-only `cndate_o` module. That module is
not included or used here: this build uses the installed toolchain's cn_date
library function. Toolchain/runtime components retain their own terms.
