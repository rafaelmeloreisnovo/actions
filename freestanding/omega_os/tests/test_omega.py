"""Synthetic host falsifiers; no physical, protection or boot claims."""
import ctypes,os,random,unittest
from pathlib import Path
lib=ctypes.CDLL(os.environ.get("OMEGA_TEST_LIB",str(Path(__file__).resolve().parents[1]/"libomega.so")))
U=ctypes.c_uint;N=0xffffffff
class Slot(ctypes.Structure):_fields_=[(k,U) for k in ("state","owner","rights","epoch")]
class Context(ctypes.Structure):
 _fields_=[(k,U) for k in ("phase","sequence","digest","last_selected","running")]+[("slots",Slot*8)]
class Event(ctypes.Structure):_fields_=[(k,U) for k in ("sequence","opcode","actor","target","rights","epoch")]
class Receipt(ctypes.Structure):
 _fields_=[(k,U) for k in ("status","sequence","chosen","before_digest","after_digest","phase")]
lib.omega_init.argtypes=[ctypes.POINTER(Context),U]
lib.omega_step.argtypes=[ctypes.POINTER(Context),ctypes.POINTER(Event),ctypes.POINTER(Receipt)]
lib.omega_step.restype=U
def raw(c):return bytes(ctypes.string_at(ctypes.byref(c),ctypes.sizeof(c)))
def init(seed=19):
 c=Context();lib.omega_init(ctypes.byref(c),seed);return c
def step(c,op,actor=0,target=N,rights=0,seq=None,epoch=None):
 if epoch is None:
  epoch=(c.slots[target-1].epoch + (1 if op==2 else 0)) if 1<=target<=8 else 0
 e=Event(c.sequence+1 if seq is None else seq,op,actor,target,rights,epoch)
 r=Receipt();before=raw(c)
 st=lib.omega_step(ctypes.byref(c),ctypes.byref(e),ctypes.byref(r))
 assert st==r.status
 if st:assert raw(c)==before,"Rejected event mutated state"
 else:assert c.sequence==e.sequence
 assert sum(s.state==2 for s in c.slots)<=1
 if c.running!=N:assert c.slots[c.running].state==2
 return st,r
def live():
 c=init();assert step(c,1)[0]==0;return c
class TestOmega(unittest.TestCase):
 def test_ctypes_matches_documented_c_abi(self):
  # The C header has 4 ou32 fields per slot (epoch is the 4th).
  # A stale three-field mirror corrupts offsets and invalidates all replay tests.
  self.assertEqual(ctypes.sizeof(U),4)
  self.assertEqual(ctypes.sizeof(Slot),16)
  self.assertEqual(ctypes.sizeof(Context),148)
  self.assertEqual(Context.slots.offset,20)
  self.assertEqual(Slot.epoch.offset,12)
 def test_initial(self):
  c=init();self.assertEqual((c.phase,c.sequence,c.running),(0,0,N))
 def test_boot_authority(self):
  c=init();self.assertEqual(step(c,1,actor=2)[0],3)
  self.assertEqual(step(c,1)[0],0);self.assertEqual(step(c,1)[0],1)
 def test_spawn_actor(self):self.assertEqual(step(live(),2,actor=1,target=1,rights=7)[0],3)
 def test_rights(self):
  c=live();self.assertEqual(step(c,2,target=1,rights=0)[0],6)
  self.assertEqual(step(c,2,target=1,rights=8)[0],6)
 def test_duplicate(self):
  c=live();step(c,2,target=1,rights=7)
  self.assertEqual(step(c,2,target=1,rights=7)[0],5)
 def test_round_robin(self):
  c=live();step(c,2,target=1,rights=7);step(c,2,target=2,rights=7)
  self.assertEqual(step(c,3)[1].chosen,1)
  self.assertEqual(step(c,3)[0],7)
  self.assertEqual(step(c,4,actor=1,target=1)[0],0)
  self.assertEqual(step(c,3)[1].chosen,2)
  step(c,4,actor=2,target=2)
  self.assertEqual(step(c,3)[1].chosen,1)
 def test_wait_wake(self):
  c=live();step(c,2,target=1,rights=7);step(c,3)
  self.assertEqual(step(c,5,actor=1,target=1)[0],0)
  self.assertEqual(step(c,3)[0],5)
  step(c,6,target=1);self.assertEqual(step(c,3)[1].chosen,1)
 def test_foreign_yield(self):
  c=live();step(c,2,target=1,rights=7);step(c,3)
  self.assertEqual(step(c,4,actor=2,target=1)[0],6)
 def test_no_control(self):
  c=live();step(c,2,target=1,rights=1);step(c,3)
  self.assertEqual(step(c,4,actor=1,target=1)[0],6)
  self.assertEqual(step(c,4,target=1)[0],0)
 def test_exit_right(self):
  c=live();step(c,2,target=1,rights=3)
  self.assertEqual(step(c,7,actor=1,target=1)[0],6)
  self.assertEqual(step(c,7,target=1)[0],0)
 def test_reap_clears_capabilities(self):
  c=live();step(c,2,target=1,rights=7);step(c,7,target=1)
  step(c,9,target=1)
  self.assertEqual((c.slots[0].state,c.slots[0].owner,c.slots[0].rights),(0,0,0))
 def test_fault_root_only(self):
  c=live();step(c,2,target=1,rights=7)
  self.assertEqual(step(c,8,actor=1,target=1)[0],3)
  self.assertEqual(step(c,8,target=1)[0],0)
 def test_replay(self):
  c=live();self.assertEqual(step(c,2,target=1,rights=7,seq=1)[0],2)
  self.assertEqual(step(c,2,target=1,rights=7,seq=4)[0],2)
 def test_bad_target_opcode(self):
  c=live();self.assertEqual(step(c,2,target=0,rights=7)[0],4)
  self.assertEqual(step(c,99)[0],8)
 def test_shutdown_authority(self):self.assertEqual(step(live(),10,actor=1)[0],3)
 def test_shutdown_wait(self):
  c=live();step(c,2,target=1,rights=7)
  self.assertEqual(step(c,10)[0],7)
  step(c,7,target=1);self.assertEqual(step(c,10)[0],0)
  self.assertEqual(step(c,2,target=2,rights=7)[0],1)
 def test_empty_not_zero(self):
  self.assertEqual(live().running,N)
 def test_overflow(self):
  c=init();c.sequence=N;self.assertEqual(step(c,1,seq=0)[0],9)
 def test_replay_deterministic(self):
  def trace():
   c=init(42);events=[(1,0,N,0),(2,0,1,7),(2,0,2,7),(3,0,N,0),
                       (4,1,1,0),(3,0,N,0),(7,2,2,0),(3,0,N,0)]
   receipts=[(step(c,*args)[0],c.digest) for args in events]
   return raw(c),receipts
  self.assertEqual(trace(),trace())
 def test_adversarial(self):
  rng=random.Random(20261013);c=live()
  for _ in range(2500):
   status,_=step(c,rng.randrange(1,13),rng.randrange(0,11),
                 rng.choice([N]+list(range(11))),rng.randrange(0,17))
   self.assertTrue(0<=status<=11)
 def test_generation_replay_across_reused_task(self):
  c=live();step(c,2,target=1,rights=7)
  old=c.slots[0].epoch
  step(c,7,target=1);step(c,9,target=1)
  self.assertEqual(c.slots[0].epoch,old)
  step(c,2,target=1,rights=7)
  self.assertEqual(c.slots[0].epoch,old+1)
  self.assertEqual(step(c,7,actor=1,target=1,epoch=old)[0],11)
  self.assertEqual(step(c,7,actor=1,target=1,epoch=old+1)[0],0)
 def test_boot_argument(self):
  c=init();self.assertEqual(step(c,1,target=1)[0],4)
  self.assertEqual(step(c,1,rights=7)[0],8)
if __name__=="__main__":unittest.main()
