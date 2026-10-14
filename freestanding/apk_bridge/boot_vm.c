/* RAFAELIA tiny freestanding synthetic VM; NOT firmware/real ISA emulation. */
typedef unsigned char u8;
typedef unsigned int u32;
_Static_assert(sizeof(u8)==1&&sizeof(u32)==4,"8/32-bit target");
enum {RA_VM_HALT=0,RA_VM_TRUNCATED=1,RA_VM_BAD_OPCODE=2,
      RA_VM_FUEL=3,RA_VM_BAD_INPUT=4};
typedef struct {u32 status,pc,steps,accumulator;} ra_vm_result;
/* 0x00 HALT; 0x10..13 LOAD next byte; 0x20..23 XOR r0;
 * 0x30..33 ADD into r0 (mod 256). No jumps, I/O or syscalls. */
ra_vm_result ra_vm_run(const u8 *b,u32 n,u32 fuel){
 u8 r[4]={0,0,0,0};u32 pc=0,steps=0,st=RA_VM_BAD_INPUT;
 ra_vm_result result;
 if(!b||!n||n>65536u||!fuel||fuel>65536u)
  return (ra_vm_result){RA_VM_BAD_INPUT,0,0,0};
 while(pc<n&&steps<fuel){
  u32 op=b[pc++],idx=op&15u;steps++;
  if(op==0u){st=RA_VM_HALT;break;}
  if(idx>3u){st=RA_VM_BAD_OPCODE;break;}
  if((op&0xf0u)==0x10u){
   if(pc==n){st=RA_VM_TRUNCATED;break;}
   r[idx]=b[pc++];
  }else if((op&0xf0u)==0x20u)r[0]=(u8)(r[0]^r[idx]);
  else if((op&0xf0u)==0x30u)r[0]=(u8)(r[0]+r[idx]);
  else {st=RA_VM_BAD_OPCODE;break;}
 }
 if(st==RA_VM_BAD_INPUT)st=steps==fuel?RA_VM_FUEL:RA_VM_TRUNCATED;
 result=(ra_vm_result){st,pc,steps,r[0]};return result;
}
