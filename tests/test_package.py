#!/usr/bin/env python3
"""Verify the Elvis-compatible wrapper and SNL's actual metadata reader."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import runpy
import struct
import tempfile

root = Path(__file__).resolve().parent.parent
wrap = runpy.run_path(str(root / 'package.py'))['wrap']
raw = (root / 'build/ls').read_bytes()
packaged = (root / 'bin/ls').read_bytes()
assert packaged == wrap(raw)
assert packaged[30:] == raw
assert packaged[21] == 1
assert packaged[22:26] == raw[-4:]
try:
    wrap(packaged)
except ValueError:
    pass
else:
    raise AssertionError('double wrapping must fail')
server = os.environ.get('SNL_SERVER')
if server:
    loader = importlib.machinery.SourceFileLoader('snl_ls_test', server)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    snl = importlib.util.module_from_spec(spec)
    loader.exec_module(snl)
    with tempfile.TemporaryDirectory() as directory:
        (Path(directory) / 'ls').write_bytes(packaged)
        session = snl.Session({'4': directory})
        try:
            assert session.open('4', 1, b'ls') == len(raw)
            header = session.read_header()
            assert header[5] == 1
            assert header[6:10] == raw[-4:]
            assert struct.unpack('>I', header[:4])[0] == len(raw)
            assert session.read(0,64) == raw[:64]
        finally:
            session.close()
    print('Passed: actual SNL reader exposes type 1, correct dataspace and unwrapped code.')
else:
    print('Passed: wrapper preserves code and executable metadata; set SNL_SERVER for integration.')
