import ctypes,io,os,struct,unittest,zipfile
from pathlib import Path
p=Path(__file__).resolve().parents[1]
lib=ctypes.CDLL(os.environ.get("RA_BRIDGE_TEST_LIB",str(p/"libra_bridge.so")))
class Apk(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint) for n in ("status","entries","manifest_present","dex_present")]
class Vm(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint) for n in ("status","pc","steps","accumulator")]
lib.ra_apk_probe.argtypes=[ctypes.c_void_p,ctypes.c_uint]
lib.ra_apk_probe.restype=Apk
lib.ra_vm_run.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
lib.ra_vm_run.restype=Vm
def probe(b): return lib.ra_apk_probe(ctypes.create_string_buffer(b),len(b))
def vm(b,fuel=32):return lib.ra_vm_run(ctypes.create_string_buffer(b),len(b),fuel)
def z(names=("AndroidManifest.xml","classes.dex")):
    io_=io.BytesIO()
    with zipfile.ZipFile(io_,"w",compression=zipfile.ZIP_DEFLATED) as file:
        for name in names:file.writestr(name,b"synthetic-content")
    return io_.getvalue()
class Structural(unittest.TestCase):
    def test_valid(self):self.assertEqual((probe(z()).status,probe(z()).dex_present),(0,1))
    def test_native_only(self):self.assertEqual(probe(z(("AndroidManifest.xml",))).status,0)
    def test_no_manifest(self):self.assertEqual(probe(z(("classes.dex",))).status,6)
    def test_truncated(self):self.assertNotEqual(probe(z()[:-1]).status,0)
    def test_nonzip(self):self.assertEqual(probe(b"some random bytes not zip").status,2)
    def test_path(self):self.assertEqual(probe(z(("AndroidManifest.xml","../bad"))).status,7)
    def test_local_sig(self):
        a=bytearray(z());a[0]=0;self.assertEqual(probe(bytes(a)).status,5)
    def test_offset(self):
        a=bytearray(z());i=a.rfind(b"PK\x05\x06");struct.pack_into("<I",a,i+16,0xfffffff0)
        self.assertEqual(probe(bytes(a)).status,4)
    def test_zip64(self):
        a=bytearray(z());i=a.rfind(b"PK\x05\x06");struct.pack_into("<H",a,i+10,0xffff)
        self.assertEqual(probe(bytes(a)).status,3)
    def test_encrypted(self):
        a=bytearray(z());i=a.find(b"PK\x01\x02");struct.pack_into("<H",a,i+8,1)
        self.assertEqual(probe(bytes(a)).status,3)
    def test_local_name_mismatch(self):
        a=bytearray(z());i=a.find(b"PK\x01\x02");a[i+46]=ord("Z")
        self.assertEqual(probe(bytes(a)).status,5)
    def test_overlay(self):self.assertNotEqual(probe(z()+b"tail").status,0)
    def test_absence(self):self.assertEqual(probe(b"").status,1)
class ToyBoot(unittest.TestCase):
    def test_bytecode(self):
        r=vm(bytes([0x10,7,0x11,5,0x31,0]))
        self.assertEqual((r.status,r.accumulator,r.steps),(0,12,4))
    def test_imm(self):self.assertEqual(vm(b"\x10").status,1)
    def test_opcode(self):self.assertEqual(vm(b"\xff\x00").status,2)
    def test_budget(self):self.assertEqual(vm(b"\x10\x07\x00",fuel=1).status,3)
    def test_no_halt(self):self.assertEqual(vm(b"\x11\x05").status,1)
    def test_zero_not_absent(self):
        self.assertEqual(vm(b"\x10\x00\x00").status,0)
        self.assertEqual(vm(b"").status,4)
if __name__=="__main__":unittest.main()
