"""
PC-BASIC test.disk
Tests for disk devices

(c) 2019 Rob Hagemans
This file is released under the GNU GPL version 3 or later.
"""

import unittest
import os
import shutil

from pcbasic import Session


HERE = os.path.dirname(os.path.abspath(__file__))


class DiskTest(unittest.TestCase):
    """Disk tests."""

    def setUp(self):
        """Ensure output directory exists."""
        try:
            os.mkdir(os.path.join(HERE, u'output', u'disk'))
        except EnvironmentError:
            pass
        # create directory to mount
        self._test_dir = os.path.join(HERE, u'output', u'disk', u'test_dir')
        try:
            shutil.rmtree(self._test_dir)
        except EnvironmentError:
            pass
        os.mkdir(self._test_dir)

    def _output_path(self, *name):
        """Test output file name."""
        return os.path.join(self._test_dir, *name)

    def test_text(self):
        """Save and load in plaintext to a file."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('10 A%=1234')
            s.execute('save "prog",A')
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('run "prog"')
            assert s.get_variable('A%') == 1234

    def test_binary(self):
        """Save and load in binary format to a file."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('10 A%=1234')
            s.execute('save "prog"')
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('run "prog"')
            assert s.get_variable('A%') == 1234

    def test_protected(self):
        """Save and load in protected format to a file."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('10 A%=1234')
            s.execute('save "prog", P')
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('run "prog"')
            assert s.get_variable('A%') == 1234

    def test_text_letter(self):
        """Save and load in plaintext to a file, explicit drive letter."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('10 A%=1234')
            s.execute('save "A:prog",A')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('run "A:prog"')
            assert s.get_variable('A%') == 1234

    def test_files(self):
        """Test directory listing, current directory and free space report."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('save "A:prog",A')
            s.execute('files "A:"')
            s.execute('print "##"')
            output = [_row.strip() for _row in s.get_text()]
            assert output[:2] == [
                b'A:\\',
                b'.   <DIR>         ..  <DIR> PROG    .BAS'
            ]
            assert output[2].endswith(b' Bytes free')
            # empty line between files and next output
            assert output[3:5] == [b'', b'##']
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('files')
            output = [_row.strip() for _row in s.get_text()]
            assert output[:2] == [
                b'A:\\',
                b'.   <DIR>         ..  <DIR> PROG    .BAS'
            ]

    def test_files_longname(self):
        """Test directory listing with long name."""
        open(self._output_path('very_long_name_and.extension'), 'w')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('files "A:"')
            output = [_row.strip() for _row in s.get_text()]
            assert output[:2] == [
                b'A:\\',
                b'.   <DIR>         ..  <DIR> very_lo+.ex+'
            ]

    def test_files_wildcard(self):
        """Test directory listing with wildcards."""
        open(self._output_path('aaa.txt'), 'w')
        open(self._output_path('aab.txt'), 'w')
        open(self._output_path('abc.txt'), 'w')
        open(self._output_path('aa_long_file_name.txt'), 'w')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('files "A:*.txt"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[1] == b'AAA     .TXT      AAB     .TXT      ABC     .TXT      aa_long+.txt'
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('files "A:aa?.txt"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[1] == b'AAA     .TXT      AAB     .TXT'
        # no match
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('files "A:b*.txt"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[1] == b'File not found\xff'

    def test_internal_disk_files(self):
        """Test directory listing, current directory and free space report on special @: disk."""
        with Session(devices={b'@': self._test_dir}) as s:
            s.execute('save "@:prog",A')
            s.execute('files "@:"')
            output = [_row.strip() for _row in s.get_text()]
            assert output[:2] == [
                b'@:\\',
                b'.   <DIR>         ..  <DIR> PROG    .BAS'
            ]
            assert output[2].endswith(b' Bytes free')

    def test_internal_disk_unbound_files(self):
        """Test directory listing, current directory and free space report on unbound @: disk."""
        with Session(devices={}) as s:
            s.execute('save "@:prog",A')
            s.execute('files "@:"')
            output = [_row.strip() for _row in s.get_text()]
            assert output[:4] == [
                b'Path not found\xff',
                b'@:\\',
                b'.   <DIR>         ..  <DIR>',
                b'0 Bytes free'
            ]

    def test_disk_data(self):
        """Write and read data to a text file."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for output as 1')
            s.execute('print#1, 1234')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for input as 1')
            s.execute('input#1, A%')
            assert s.get_variable('A%') == 1234

    def test_disk_data_utf8(self):
        """Write and read data to a text file, utf-8 encoding."""
        with Session(devices={b'A': self._test_dir}, textfile_encoding='utf-8') as s:
            s.execute('open "a:data" for output as 1')
            # we're embedding codepage in this string, so should be bytes
            s.execute(b'print#1, "\x9C"')
        # utf8-sig, followed by pound sign
        assert open(self._output_path('DATA'), 'rb').read() == b'\xef\xbb\xbf\xc2\xa3\r\n\x1a'
        with Session(devices={b'A': self._test_dir}, textfile_encoding='utf-8') as s:
            s.execute('open "a:data" for append as 1')
            s.execute(b'print#1, "\x9C"')
        assert open(self._output_path('DATA'), 'rb').read() == (
            b'\xef\xbb\xbf\xc2\xa3\r\n\xc2\xa3\r\n\x1a'
        )

    def test_disk_data_lf(self):
        """Write and read data to a text file, soft and hard linefeed."""
        with open(self._output_path('DATA'), 'wb') as f:
            f.write(b'a\nb\r\nc')
        with Session(devices={b'A': self._test_dir}, soft_linefeed=True) as s:
            s.execute('open "a:data" for input as 1')
            s.execute('line input#1, a$')
            s.execute('line input#1, b$')
            s.execute('line input#1, c$')
        assert s.get_variable('A$') == b'a\nb'
        assert s.get_variable('B$') == b'c'
        assert s.get_variable('C$') == b''
        with Session(devices={b'A': self._test_dir}, soft_linefeed=False) as s:
            s.execute('open "a:data" for input as 1')
            s.execute('line input#1, a$')
            s.execute('line input#1, b$')
            s.execute('line input#1, c$')
        assert s.get_variable('A$') == b'a'
        assert s.get_variable('B$') == b'b'
        assert s.get_variable('C$') == b'c'

    def test_disk_data_append(self):
        """Append data to a text file."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for output as 1')
            s.execute('print#1, 1234')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for append as 1')
            s.execute('print#1, "abcde"')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for input as 1')
            s.execute('line input#1, a$')
            s.execute('line input#1, b$')
            assert s.get_variable('A$') == b' 1234 '
            assert s.get_variable('B$') == b'abcde'

    def test_disk_random(self):
        """Write and read data to a random access file."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for random as 1')
            s.execute('field#1, 20 as a$, 20 as b$')
            s.execute('lset b$="abcde"')
            s.execute('print#1, 1234')
            s.execute('put#1, 1')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:data" for random as 1')
            s.execute('field#1, 20 as a$, 20 as b$')
            s.execute('get#1, 1')
            assert s.get_variable('A$') == b' 1234 \r\n'.ljust(20, b'\0')
            assert s.get_variable('B$') == b'abcde'.ljust(20, b' ')

    def test_match_name(self):
        """Test case-insensitive matching of native file name."""
        # this will be case sensitive on some platforms but should be picked up correctly anyway
        open(self._output_path('MixCase.txt'), 'w').close()
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:mixcase.txt" for output as 1')
            s.execute('print#1, 1234')
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "a:MIXCASE.TXT" for input as 1')
            s.execute('input#1, A%')
            assert s.get_variable('A%') == 1234
        # check we've used the pre-existing file
        assert open(self._output_path('MixCase.txt'), 'rb').read() == b' 1234 \r\n\x1a'

    def test_match_name_non_ascii(self):
        """Test non-matching of names that are not ascii."""
        # this will be case sensitive on some platforms but should be picked up correctly anyway
        open(self._output_path(u'MY\xc2\xa30.02'), 'w')
        with Session(devices={b'A': self._test_dir}) as s:
            # non-ascii not allowed - cp437 &h9c is pound sign
            s.execute('open "a:MY"+chr$(&h9c)+"0.02" for output as 1')
            # search for a match in the presence of non-ascii files
            s.execute('open "a:MY0.02" for input as 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[:2] == [b'Bad file name\xff', b'File not found\xff']

    def test_name_illegal_chars(self):
        """Test non-matching of names that are not ascii."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            # control chars not allowed
            s.execute('open chr$(0) for output as 1')
            s.execute('open chr$(1) for output as 1')
            output = [_row.strip() for _row in s.get_text()]
        # NOTE: gw raises bad file number instead
        assert output[:2] == [b'Bad file name\xff', b'Bad file name\xff']

    def test_name_slash(self):
        """Test non-matching of names with forward slash."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            # forward slash not allowed
            s.execute('open "b/c" for output as 1')
            output = [_row.strip() for _row in s.get_text()]
        # NOTE: gw raises bad file number instead
        assert output[0] == b'Path not found\xff'

    def test_unavailable_drive(self):
        """Test attempt to access unavailable drive letter."""
        with Session(devices={b'A': self._test_dir}) as s:
            # drive b: not mounted
            s.execute('open "b:test" for output as 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Path not found\xff'

    def test_path(self):
        """Test accessing file through path."""
        os.mkdir(self._output_path('a'))
        os.mkdir(self._output_path('a', 'B'))
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            # simple relative path
            s.execute('open "a\\b\\rel" for output as 1:close')
            # convoluted path
            s.execute('open "a\\b\\..\\..\\a\\.\\dots" for output as 1:close')
            # set cwd
            s.execute('chdir "a"')
            # absolute path
            s.execute('open "\\a\\b\\abs" for output as 1:close')
            # relative path from cwd
            s.execute('open ".\\this" for output as 1:close')
            s.execute('open "..\\parent" for output as 1:close')
        assert os.path.isfile(self._output_path('a', 'B', 'REL'))
        assert os.path.isfile(self._output_path('a', 'DOTS'))
        assert os.path.isfile(self._output_path('a', 'B', 'ABS'))
        assert os.path.isfile(self._output_path('PARENT'))
        assert os.path.isfile(self._output_path('a', 'THIS'))

    def test_directory_ops(self):
        """Test directory operations."""
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('mkdir "test"')
            s.execute('mkdir "test\\test2"')
            s.execute('chdir "test"')
            s.execute('mkdir "remove"')
            s.execute('rmdir "remove"')
        assert os.path.isdir(self._output_path('TEST'))
        assert os.path.isdir(self._output_path('TEST', 'TEST2'))
        assert not os.path.exists(self._output_path('TEST', 'REMOVE'))

    def test_file_ops(self):
        """Test file operations."""
        open(self._output_path('testfile'), 'w').close()
        open(self._output_path('delete.txt'), 'w').close()
        open(self._output_path('delete1.txt'), 'w').close()
        open(self._output_path('delete2.txt'), 'w').close()
        open(self._output_path('delete3'), 'w').close()
        with Session(
                devices={b'A': self._test_dir, b'B': self._test_dir}, current_device='A:'
            ) as s:
            s.execute('name "testfile" as "newname"')
            # rename across disks
            s.execute('name "newname" as "b:fail"')
            # file already exists
            s.execute('name "newname" as "delete.txt"')
            s.execute('kill "delete.txt"')
            s.execute('kill "delete?.txt"')
            s.execute('kill "delete*"')
            # file not found
            s.execute('kill "notfound"')
            # file not found
            s.execute('kill "not*.*"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[:4] == [
            b'Rename across disks\xff',
            b'File already exists\xff',
            b'File not found\xff',
            b'File not found\xff'
        ]
        assert os.path.isfile(self._output_path('NEWNAME'))
        assert not os.path.exists(self._output_path('testfile'))
        assert not os.path.exists(self._output_path('delete.txt'))
        assert not os.path.exists(self._output_path('delete1.txt'))
        assert not os.path.exists(self._output_path('delete2.txt'))
        assert not os.path.exists(self._output_path('delete3'))

    def test_files_cwd(self):
        """Test directory listing, not on root."""
        os.mkdir(self._output_path('a'))
        with Session(devices={b'A': self._test_dir}, current_device='A:') as s:
            s.execute('chdir "a"')
            s.execute('files')
            s.execute('files ".."')
            s.execute('files "..\\"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[:2] == [b'A:\\A', b'.   <DIR>         ..  <DIR>']
        assert output[4:6] == [b'A:\\A', b'.   <DIR>']
        assert output[8:10] == [b'A:\\A', b'.   <DIR>         ..  <DIR> A           <DIR>']

    def test_files_no_disk(self):
        """Test directory listing, non-existing device."""
        with Session() as s:
            s.execute('files "A:"')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'File not found\xff'

    def test_close_not_open(self):
        """Test closing a file number that is not open."""
        with Session() as s:
            s.execute('close#2')
            output = [_row.strip() for _row in s.get_text()]
        # no error
        assert output[0] == b''

    def test_mount_dict_spec(self):
        """Test mount dict specification."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "A:test" for output as 1: print#1, 42: close 1')
        # lowercase
        with Session(devices={b'a': self._test_dir}) as s:
            s.execute('open "A:test" for input as 1: input#1, A%')
            assert s.get_variable('A%') == 42
        # with :
        with Session(devices={b'A:': self._test_dir}) as s:
            s.execute('open "A:test" for input as 1: input#1, A%')
            assert s.get_variable('A%') == 42
        # unicode
        with Session(devices={u'a:': self._test_dir}) as s:
            s.execute('open "A:test" for input as 1: input#1, A%')
            assert s.get_variable('A%') == 42

    def test_bad_mount(self):
        """Test bad mount dict specification."""
        with Session(devices={b'#': self._test_dir}) as s:
            s.execute('open "A:test" for output as 1: print#1, 42: close 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Path not found\xff'
        with Session(devices={b'\0': self._test_dir}) as s:
            s.execute('open "A:test" for output as 1: print#1, 42: close 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Path not found\xff'
        with Session(devices={u'\xc4': self._test_dir}) as s:
            s.execute('open "A:test" for output as 1: print#1, 42: close 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Path not found\xff'

    def test_bad_current(self):
        """Test bad current device."""
        with Session(devices={'A': self._test_dir, 'Z': None}, current_device='B') as s:
            s.execute('open "test" for output as 1: print#1, 42: close 1')
        assert os.path.isfile(self._output_path('TEST'))
        with Session(devices={'A': self._test_dir, 'Z': None}, current_device='#') as s:
            s.execute('open "test2" for output as 1: print#1, 42: close 1')
        assert os.path.isfile(self._output_path('TEST2'))

    def test_bytes_mount(self):
        """Test specifying mount dir as bytes."""
        with Session(devices={'A': self._test_dir.encode('ascii'), 'Z': None}) as s:
            s.execute('open "test" for output as 1: print#1, 42: close 1')
        assert os.path.isfile(self._output_path('TEST'))
        # must be ascii
        with Session(devices={'A': b'ab\xc2', 'Z': None}) as s:
            s.execute('files')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'@:\\'

    def test_open_bad_device(self):
        """Test open on a bad device name."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "#:test" for output as 1: print#1, 42: close 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Bad file number\xff'

    def test_open_null_device(self):
        """Test the NUL device."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "NUL" for output as 1: print#1, 42: close 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b''

    def test_open_bad_number(self):
        """Test opening to a bad file number."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "TEST" for output as 4')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == b'Bad file number\xff'

    def test_open_reuse_number(self):
        """Test opening to a number taht's already in use."""
        with Session(devices={b'A': self._test_dir}) as s:
            s.execute('open "TEST" for output as 1')
            s.execute('open "TEST2" for output as 1')
            output = [_row.strip() for _row in s.get_text()]
        assert output[0] == 'File already open\xff'


if __name__ == '__main__':
    unittest.main()
