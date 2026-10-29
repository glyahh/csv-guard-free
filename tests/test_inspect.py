import csv, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inspect_csv import inspect, MAX_BYTES
SCRIPT=Path(__file__).resolve().parents[1]/'inspect_csv.py'
class Tests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.p=Path(self.temp.name)/'x.csv'
    def tearDown(self): self.temp.cleanup()
    def write(self,s): self.p.write_text(s,encoding='utf-8')
    def test_counts(self):
        self.write('id,note\n0001, A \n0001, A \n0002,=1+1\n'); r=inspect(self.p)
        self.assertEqual((r['rows'],r['exact_duplicate_rows'],r['formula_prefix_rows']),(3,1,1))
        self.assertEqual(r['column_checks'][0]['leading_zero_digit_cells'],3)
    def test_values_not_reported(self):
        self.write('secret_header\nsecret_value\n'); s=json.dumps(inspect(self.p))
        self.assertNotIn('secret_header',s); self.assertNotIn('secret_value',s)
    def test_original_unchanged(self):
        self.write('id,note\n0001,NA\n0002,\n'); b=self.p.read_bytes(); r=inspect(self.p)
        self.assertEqual(b,self.p.read_bytes()); self.assertEqual(r['column_checks'][1]['literal_NA_cells'],1)
    def test_no_output_files(self):
        self.write('id\n001\n'); files=list(self.p.parent.iterdir()); inspect(self.p)
        self.assertEqual(files,list(self.p.parent.iterdir()))
    def test_cli_bad_input(self):
        self.write('id,note\n01\n'); p=subprocess.run([sys.executable,str(SCRIPT),str(self.p)],capture_output=True)
        self.assertEqual(p.returncode,2); self.assertEqual(p.stdout,b'')
    def test_duplicate_header(self):
        self.write('id,id\n01,02\n')
        with self.assertRaises(ValueError): inspect(self.p)
    def test_bad_encoding(self):
        self.p.write_bytes(b'\xff')
        with self.assertRaises(UnicodeError): inspect(self.p)
    def test_bad_quotes(self):
        self.write('id\n"broken\n')
        with self.assertRaises(csv.Error): inspect(self.p)
    def test_header_only(self):
        self.write('id\n'); self.assertEqual(inspect(self.p)['rows'],0)
    def test_gb18030(self):
        self.p.write_bytes('编号\n001\n'.encode('gb18030')); self.assertEqual(inspect(self.p,'gb18030')['rows'],1)
    def test_over_limit(self):
        with self.p.open('wb') as f:f.truncate(MAX_BYTES+1)
        with self.assertRaises(ValueError): inspect(self.p)
    def test_symlink(self):
        self.write('id\n001\n'); link=self.p.with_name('link'); link.symlink_to(self.p)
        with self.assertRaises(ValueError): inspect(link)
    @unittest.skipUnless(hasattr(os,'mkfifo'),'POSIX only')
    def test_fifo(self):
        os.mkfifo(self.p)
        with self.assertRaises(ValueError): inspect(self.p)
    def test_multiline(self):
        self.write('id,note\n001,"two\nlines"\n'); self.assertEqual(inspect(self.p)['rows'],1)
if __name__=='__main__':unittest.main(verbosity=2)
