#!/usr/bin/env python3
"""Run the actual ls source with mocked QDOS I/O on the host."""
import os
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory() as tmp:
    exe = str(Path(tmp) / 'ls-test')
    subprocess.run(['cc', '-std=gnu89', '-Wno-deprecated-non-prototype',
                    '-I'+str(root/'tests'), '-x', 'c', str(root/'ls_c'),
                    str(root/'tests/qdos_mock.c'), '-o', exe], check=True)
    def nonblank(output):
        return [row for row in output.splitlines() if row]
    def run(*args, **env):
        return subprocess.run([exe, *args], capture_output=True, text=True,
                              env={**os.environ, **env})
    longname = 'abcdefghijklmnopqrstuvwxyz0123456789'
    expected = [longname, 'alpha', 'Beta', 'zebra']
    assert nonblank(run('-s').stdout) == expected
    assert nonblank(run('-s', '-r').stdout) == expected[::-1]
    assert nonblank(run('-s', '-t').stdout) == ['zebra','Beta','alpha',longname]
    assert nonblank(run('-s', '-S').stdout) == [longname,'alpha','Beta','zebra']
    assert nonblank(run('-s', '-t','-r').stdout) == [longname,'alpha','Beta','zebra']
    assert run('-x').stdout.split() == expected
    assert run(EMPTY='1').stdout == ''
    assert run('-x',EMPTY='1').returncode == 0
    many = nonblank(run('-s', MANY='1').stdout)
    assert many == [f'file{i:03}' for i in range(100)]
    detailed = run('-l')
    assert detailed.returncode == 0
    rows = nonblank(detailed.stdout)
    assert len(rows) == 4
    assert [row.split()[0] for row in rows] == expected
    assert [row.split()[1] for row in rows] == ['400', '300', '200', '100']
    assert all(row.endswith('2026 Nov 16 17:18') for row in rows)
    assert ':12' not in detailed.stdout and '1961' not in detailed.stdout
    assert run('-x', '-l').stdout == detailed.stdout
    assert run('-l', '-x').stdout.split() == expected
    assert run().stdout == detailed.stdout
    assert run('-s', '-l').stdout == detailed.stdout
    assert nonblank(run('-l', '-s').stdout) == expected
    assert run('-l', SHARED='1').stdout == detailed.stdout
    assert all(row.endswith('  -') for row in nonblank(run('-l', NO_DATE='1').stdout))
    assert nonblank(detailed.stdout)[0].startswith(longname+' ')
    directory_rows = nonblank(run('-s', DIRECTORIES='1').stdout)
    assert directory_rows == [longname+' ->', 'alpha', 'Beta ->', 'zebra ->']
    directory_details = nonblank(run(DIRECTORIES='1').stdout)
    assert len(directory_details) == 4
    assert directory_details[0].startswith(longname+' ->  ')
    assert '->' not in directory_details[1]
    assert all(row.index('2026') == directory_details[0].index('2026')
               for row in directory_details)
    assert run('-x', DIRECTORIES='1').stdout.split() == [
        longname, '->', 'alpha', 'Beta', '->', 'zebra', '->']
    # Directory order transcribed from the user's QL screenshot.
    names = ['boot', 'boot2', 'boot3', 'playss', 'rn_bas', 'TK236_bin', 'mouse_bin',
             'proglogic', 'sound_run', 'bench4_bin', 'benchm_bin', 'catwalk_ub',
             'pitman_zip', 'western_ub', 'bintest_bin', 'sertest_bas', 'Min4068_rext',
             'forgotten_ub', 'probe384_bin', 'probe512_bin', 'qimsikbd_bin',
             'snldriver_asm', 'qspread302_zip', 'snl_channels_bas', 'snldriver239_bin',
             'snl_throughput_bas']
    ordered = sorted(names, key=lambda n: (n.lower(), n))
    assert nonblank(run('-s', QL_NAMES='1').stdout) == ordered
    assert nonblank(run('-s', '-r', QL_NAMES='1').stdout) == ordered[::-1]
    assert [row.split()[0] for row in nonblank(run('-l', QL_NAMES='1').stdout)] == ordered
    assert nonblank(run('-s', '-t', QL_NAMES='1').stdout) == names
    assert nonblank(run('-s', '-S', QL_NAMES='1').stdout) == names[::-1]
    assert run().stdout.startswith('\n')
    assert not run().stdout.startswith('\n\n')
    assert run().stdout.endswith('\n')
    assert not run().stdout.endswith('\n\n')
    assert detailed.stdout.startswith('\n')
    assert not detailed.stdout.endswith('\n\n')
    assert nonblank(run('-s', 'snl1_', SNL='1').stdout) == expected
    assert nonblank(run('-s', 'snl1_*', SNL='1').stdout) == expected
    assert run('-l', 'snl1_', SNL='1').stdout == detailed.stdout
    # Use actual SNL server directory records as fixtures, when available.
    if os.environ.get('SNL_SERVER'):
        import importlib.machinery
        import importlib.util
        import struct
        loader = importlib.machinery.SourceFileLoader('snl_ls_directory', os.environ['SNL_SERVER'])
        spec = importlib.util.spec_from_loader(loader.name, loader)
        snl = importlib.util.module_from_spec(spec)
        loader.exec_module(snl)
        drive = Path(tmp) / 'drive'
        drive.mkdir()
        (drive / 'zebra').write_bytes(b'z' * 321)
        (drive / 'alpha').write_bytes(b'a' * 12)
        (drive / 'folder').mkdir()
        session = snl.Session({'1': str(drive)})
        try:
            assert session.open('1', 4, b'*') == 0
            assert session.open('1', 4, b'') == 192
            records = session.read(0, 192)
            fixture = Path(tmp) / 'snl-records.txt'
            lines = []
            for offset in range(0, len(records), 64):
                h = records[offset:offset+64]
                n, = struct.unpack('>H', h[14:16])
                name = h[16:16+n].decode('ascii')
                size, = struct.unpack('>I', h[:4])
                date, = struct.unpack('>I', h[52:56])
                lines.append(f'{name} {size} {date} {h[5]}')
            fixture.write_text('\n'.join(lines)+'\n')
            actual = run('-l','snl1_',SNL='1',SNL_FIXTURE=str(fixture))
            assert actual.returncode == 0
            assert [r.split()[:2] for r in nonblank(actual.stdout)] == [
                ['alpha','12'], ['folder','->'], ['zebra','321']]
            assert 'folder ->' in actual.stdout
        finally:
            session.close()
    assert run('-bad').returncode != 0
    assert run('-T3').returncode != 0
    assert run(OPEN_ERROR='1').returncode != 0
    assert run(READ_ERROR='1').returncode != 0
    help_result = run('-?')
    assert help_result.returncode == 0
    assert '-S largest first' in help_result.stdout
    assert '-s names only' in help_result.stdout
    assert len(help_result.stdout.splitlines()) <= 8
    assert max(map(len, help_result.stdout.splitlines())) <= 64
    shared_help = run('-?', SHARED='1')
    assert shared_help.returncode == 0
    assert shared_help.stdout == help_result.stdout
    assert nonblank(run('-s', SHARED='1').stdout) == expected
print('Passed: name/reverse/date/size sorting, columns, empty and large directories,')
print('long details, 36-character names, help, and open/read/option errors.')
