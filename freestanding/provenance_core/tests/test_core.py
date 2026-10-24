"""Hosted falsifiers for original freestanding core; NOT legal or physical proof."""
import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest

CORE = Path(__file__).resolve().parents[1]

class Request(ctypes.Structure):
    _fields_ = [("origin", ctypes.c_uint), ("claimed_proofs", ctypes.c_uint)]

class Decision(ctypes.Structure):
    _fields_ = [("state", ctypes.c_uint), ("missing_rights", ctypes.c_uint),
                ("missing_evidence", ctypes.c_uint), ("release_authorized", ctypes.c_uint)]


class ProvenanceCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ra-rights-")
        cls.lib_path = Path(cls.temp.name) / "rights.so"
        subprocess.run(["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-ffreestanding", "-fno-builtin", "-shared", "-fPIC",
                        str(CORE / "rights_core.c"), "-o", str(cls.lib_path)], check=True)
        cls.api = ctypes.CDLL(str(cls.lib_path)).ra_provenance_check
        cls.api.argtypes = [ctypes.POINTER(Request), ctypes.POINTER(Decision)]
        cls.api.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def evaluate(self, origin, proofs):
        output = Decision(99, 99, 99, 99)
        self.api(ctypes.byref(Request(origin, proofs)), ctypes.byref(output))
        return output

    def test_unknown_and_mixed_never_pass(self):
        for origin in (0, 3):
            out = self.evaluate(origin, 127)
            self.assertEqual((out.state, out.release_authorized), (0, 0))

    def test_invalid_origin_and_extra_proofs_rejected(self):
        self.assertEqual(self.evaluate(77, 127).state, 1)
        self.assertEqual(self.evaluate(1, 128).state, 1)

    def test_zero_proofs_is_a_gap_not_approval(self):
        out = self.evaluate(2, 0)
        self.assertEqual((out.state, out.missing_rights, out.missing_evidence), (2, 31, 96))

    def test_credit_missing_even_with_tests(self):
        out = self.evaluate(1, 127 ^ 16)
        self.assertEqual((out.state, out.missing_rights), (2, 16))

    def test_rights_present_without_head_receipt(self):
        out = self.evaluate(2, 31)
        self.assertEqual((out.state, out.missing_evidence), (3, 96))

    def test_structurally_complete_never_authorizes_release(self):
        for origin in (1, 2):
            out = self.evaluate(origin, 127)
            self.assertEqual((out.state, out.missing_rights,
                              out.missing_evidence, out.release_authorized), (4, 0, 0, 0))

    def test_null_input_fails_closed(self):
        output = Decision(99, 99, 99, 99)
        self.api(None, ctypes.byref(output))
        self.assertEqual((output.state, output.release_authorized), (0, 0))

    def test_cross_target_objects_no_undefined_symbols(self):
        targets = ("x86_64-unknown-none-elf", "armv7-none-eabi", "aarch64-none-elf")
        for target in targets:
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as output:
                    obj = Path(output) / "rights.o"
                    subprocess.run(["clang", "--target=" + target, "-std=c11", "-O2",
                                    "-ffreestanding", "-fno-builtin", "-fno-stack-protector",
                                    "-nostdlib", "-c", str(CORE / "rights_core.c"),
                                    "-o", str(obj)], check=True)
                    names = subprocess.run(["nm", "-u", str(obj)], check=True,
                                           text=True, capture_output=True).stdout
                    self.assertEqual(names.strip(), "")

if __name__ == "__main__":
    unittest.main()
