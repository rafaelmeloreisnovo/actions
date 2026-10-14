/* Omega-OS v0.1: finite state kernel; single writer; no libc/OS/heap/I-O */
#ifndef OMEGA_CORE_H
#define OMEGA_CORE_H
typedef unsigned int ou32;
_Static_assert(sizeof(ou32)==4,"Requires 32-bit unsigned");
enum {
 O_MAX=8, O_ROOT=0, O_NONE=0xffffffffu,
 O_COLD=0, O_LIVE=1, O_SHUT=2,
 O_EMPTY=0, O_READY=1, O_RUNNING=2, O_WAITING=3, O_STOPPED=4, O_FAULTED=5,
 O_BOOT=1, O_SPAWN=2, O_SCHEDULE=3, O_YIELD=4, O_WAIT=5,
 O_WAKE=6, O_EXIT=7, O_FAULT=8, O_REAP=9, O_SHUTDOWN=10,
 O_R_RUN=1, O_R_CONTROL=2, O_R_EXIT=4,
 O_OK=0, O_E_PHASE=1, O_E_SEQUENCE=2, O_E_ACTOR=3,
 O_E_TARGET=4, O_E_TRANSITION=5, O_E_RIGHTS=6,
 O_E_BUSY=7, O_E_ARGUMENT=8, O_E_OVERFLOW=9, O_E_POINTER=10, O_E_EPOCH=11
};
typedef struct {ou32 state, owner, rights, epoch;} o_slot;
typedef struct {
 ou32 phase, sequence, digest, last_selected, running;
 o_slot slots[O_MAX];
} o_context;
typedef struct {ou32 sequence, opcode, actor, target, rights, epoch;} o_event;
typedef struct {ou32 status, sequence, chosen, before_digest, after_digest, phase;} o_receipt;
void omega_init(o_context *context,ou32 seed);
ou32 omega_step(o_context *context,const o_event *event,o_receipt *receipt);
#endif
