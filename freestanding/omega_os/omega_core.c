/* Independent RAFAELIA Omega-OS transition kernel.
 * No allocation, libc, syscalls, ambient I/O, hardware access.
 * Receipt digest FNV32 is non-cryptographic and NOT a trusted signature.
 */
#include "omega_core.h"
static ou32 mix(ou32 h,ou32 w) {
 ou32 i;
 for(i=0;i<4u;i++)h=(h^((w>>(8u*i))&255u))*16777619u;
 return h;
}
void omega_init(o_context *c,ou32 seed) {
 ou32 i;if(!c)return;
 c->phase=O_COLD;c->sequence=0;c->digest=mix(2166136261u,seed);
 c->last_selected=O_MAX-1u;c->running=O_NONE;
 for(i=0;i<O_MAX;i++) {
  c->slots[i].state=O_EMPTY;c->slots[i].owner=0;c->slots[i].rights=0;c->slots[i].epoch=0;
 }
}
static int valid_target(ou32 t) {return t>=1u&&t<=O_MAX;}
static int privileged(const o_event *e) {return e->actor==O_ROOT;}
static int allowed(const o_event *e,const o_slot *s,ou32 required) {
 return privileged(e)||(e->actor==s->owner&&
    (s->rights&required)==required);
}
ou32 omega_step(o_context *c,const o_event *e,o_receipt *r) {
 ou32 error=O_OK,idx=O_NONE,chosen=O_NONE,i,next;
 o_slot *slot=0;
 if(!c||!e||!r)return O_E_POINTER;
 r->status=O_E_ARGUMENT;r->sequence=c->sequence;
 r->chosen=O_NONE;r->before_digest=c->digest;
 r->after_digest=c->digest;r->phase=c->phase;
 if(c->sequence==O_NONE)error=O_E_OVERFLOW;
 else if(e->sequence!=c->sequence+1u)error=O_E_SEQUENCE;
 else if(e->opcode<O_BOOT||e->opcode>O_SHUTDOWN)error=O_E_ARGUMENT;
 else if((e->opcode==O_BOOT||e->opcode==O_SCHEDULE||
          e->opcode==O_SHUTDOWN)&&e->target!=O_NONE)
  error=O_E_TARGET;
 else if(e->opcode!=O_BOOT&&e->opcode!=O_SCHEDULE&&
         e->opcode!=O_SHUTDOWN&&!valid_target(e->target))
  error=O_E_TARGET;
 else if(e->opcode!=O_SPAWN&&e->rights!=0u)error=O_E_ARGUMENT;
 else if((e->opcode==O_BOOT||e->opcode==O_SCHEDULE||
          e->opcode==O_SHUTDOWN)&&e->epoch!=0u)error=O_E_EPOCH;
 else if(e->opcode==O_BOOT) {
  if(c->phase!=O_COLD)error=O_E_PHASE;
  else if(!privileged(e))error=O_E_ACTOR;
 } else if(c->phase!=O_LIVE)error=O_E_PHASE;
 else {
  if(valid_target(e->target)){idx=e->target-1u;slot=&c->slots[idx];}
  if(e->opcode!=O_SPAWN && valid_target(e->target) &&
     e->epoch!=slot->epoch)error=O_E_EPOCH;
  if(error==O_OK)switch(e->opcode){
  case O_SPAWN:
   if(!privileged(e))error=O_E_ACTOR;
   else if((e->rights&~7u)!=0u||e->rights==0u)error=O_E_RIGHTS;
   else if(slot->epoch==O_NONE)error=O_E_OVERFLOW;
   else if(e->epoch!=slot->epoch+1u)error=O_E_EPOCH;
   else if(slot->state!=O_EMPTY)error=O_E_TRANSITION;
   break;
  case O_SCHEDULE:
   if(!privileged(e))error=O_E_ACTOR;
   else if(c->running!=O_NONE)error=O_E_BUSY;
   else {
    for(i=1u;i<=O_MAX;i++){
     next=(c->last_selected+i)%O_MAX;
     if(c->slots[next].state==O_READY &&
        (c->slots[next].rights&O_R_RUN)!=0u){chosen=next;break;}
    }
    if(chosen==O_NONE)error=O_E_TRANSITION;
   }break;
  case O_YIELD:
  case O_WAIT:
   if(slot->state!=O_RUNNING||c->running!=idx)error=O_E_TRANSITION;
   else if(!allowed(e,slot,O_R_CONTROL))error=O_E_RIGHTS;
   break;
  case O_WAKE:
   if(!privileged(e))error=O_E_ACTOR;
   else if(slot->state!=O_WAITING)error=O_E_TRANSITION;
   break;
  case O_EXIT:
   if(slot->state==O_EMPTY||slot->state==O_STOPPED||
      slot->state==O_FAULTED)error=O_E_TRANSITION;
   else if(!allowed(e,slot,O_R_EXIT))error=O_E_RIGHTS;
   break;
  case O_FAULT:
   if(!privileged(e))error=O_E_ACTOR;
   else if(slot->state==O_EMPTY||slot->state==O_STOPPED||
           slot->state==O_FAULTED)error=O_E_TRANSITION;
   break;
  case O_REAP:
   if(!privileged(e))error=O_E_ACTOR;
   else if(slot->state!=O_STOPPED&&slot->state!=O_FAULTED)
    error=O_E_TRANSITION;
   break;
  case O_SHUTDOWN:
   if(!privileged(e))error=O_E_ACTOR;
   else if(c->running!=O_NONE)error=O_E_BUSY;
   else for(i=0;i<O_MAX;i++)
    if(c->slots[i].state==O_READY||c->slots[i].state==O_RUNNING||
       c->slots[i].state==O_WAITING){error=O_E_BUSY;break;}
   break;
  default:error=O_E_ARGUMENT;break;
  }
 }
 if(error!=O_OK){r->status=error;return error;}
 switch(e->opcode){
 case O_BOOT:c->phase=O_LIVE;break;
 case O_SPAWN:
  slot->state=O_READY;slot->owner=e->target;
  slot->rights=e->rights;slot->epoch=e->epoch;break;
 case O_SCHEDULE:
  c->slots[chosen].state=O_RUNNING;c->running=chosen;
  c->last_selected=chosen;break;
 case O_YIELD:slot->state=O_READY;c->running=O_NONE;break;
 case O_WAIT:slot->state=O_WAITING;c->running=O_NONE;break;
 case O_WAKE:slot->state=O_READY;break;
 case O_EXIT:
  slot->state=O_STOPPED;
  if(c->running==idx)c->running=O_NONE;
  break;
 case O_FAULT:
  slot->state=O_FAULTED;
  if(c->running==idx)c->running=O_NONE;
  break;
 case O_REAP:slot->state=O_EMPTY;slot->owner=0;slot->rights=0;break;
 case O_SHUTDOWN:c->phase=O_SHUT;break;
 default:break;
 }
 c->sequence=e->sequence;
 c->digest=mix(c->digest,e->sequence);
 c->digest=mix(c->digest,e->opcode);
 c->digest=mix(c->digest,e->actor);
 c->digest=mix(c->digest,e->target);
 c->digest=mix(c->digest,e->rights);
 c->digest=mix(c->digest,e->epoch);
 c->digest=mix(c->digest,chosen);
 c->digest=mix(c->digest,c->phase);
 r->status=O_OK;r->sequence=c->sequence;
 r->chosen=chosen==O_NONE?O_NONE:chosen+1u;
 r->after_digest=c->digest;r->phase=c->phase;
 return O_OK;
}
