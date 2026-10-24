/*
 * RAFAELIA Omega-OS v0.1 / exhaustive bounded HOST falsifier.
 * New local test source; NO inherited Gradle algorithm or runtime copied.
 * This harness links libc for diagnostics. omega_core.c remains freestanding.
 * SOURCE != EXECUTION != EVIDENCE != CLAIM; no firmware or OS boot claim.
 */
#include <stdio.h>
#include <string.h>
#include "../omega_core.h"

_Static_assert(sizeof(o_slot) == 16u, "slot ABI 4 x ou32");
_Static_assert(sizeof(o_context) == 148u, "context ABI 5 x ou32 + 8 slots");
_Static_assert(sizeof(o_event) == 24u, "event ABI 6 x ou32");
_Static_assert(sizeof(o_receipt) == 24u, "receipt ABI 6 x ou32");

static int check_state(const o_context *now) {
    unsigned running_count=0u, i;
    if(now->phase>O_SHUT) return 1;
    for(i=0u;i<O_MAX;++i) {
        const o_slot *s=&now->slots[i];
        if(s->state>O_FAULTED) return 2;
        if(s->state==O_RUNNING) ++running_count;
        if(s->state==O_EMPTY && (s->owner!=0u || s->rights!=0u)) return 3;
    }
    if(running_count>1u) return 4;
    if(now->running==O_NONE) return running_count==0u ? 0 : 5;
    if(now->running>=O_MAX) return 6;
    if(now->slots[now->running].state!=O_RUNNING || running_count!=1u) return 7;
    return 0;
}
static int make_states(o_context seeds[5]) {
    o_event e;
    o_receipt r;
    omega_init(&seeds[0],0x20261024u);
    seeds[1]=seeds[0];
    e=(o_event){1u,O_BOOT,O_ROOT,O_NONE,0u,0u};
    if(omega_step(&seeds[1],&e,&r)!=O_OK) return 1;
    seeds[2]=seeds[1];
    e=(o_event){2u,O_SPAWN,O_ROOT,1u,7u,1u};
    if(omega_step(&seeds[2],&e,&r)!=O_OK) return 2;
    seeds[3]=seeds[2];
    e=(o_event){3u,O_SCHEDULE,O_ROOT,O_NONE,0u,0u};
    if(omega_step(&seeds[3],&e,&r)!=O_OK) return 3;
    seeds[4]=seeds[3];
    e=(o_event){4u,O_YIELD,1u,1u,0u,1u};
    if(omega_step(&seeds[4],&e,&r)!=O_OK) return 4;
    return 0;
}
int main(void) {
    static const ou32 targets[6]={0u,1u,2u,8u,9u,O_NONE};
    static const ou32 rights[4]={0u,1u,7u,8u};
    o_context states[5], a, b;
    o_event event;
    o_receipt one, two;
    unsigned state_id,opcode,actor,target_i,rights_i,epoch_i,sequence_i;
    unsigned long cases=0ul,accepted=0ul,rejected=0ul;
    if(make_states(states)!=0) return 11;
    for(state_id=0;state_id<5u;++state_id) {
        if(check_state(&states[state_id])) return 12;
        for(opcode=0u;opcode<=11u;++opcode) {
            for(actor=0u;actor<=10u;++actor) {
                for(target_i=0u;target_i<6u;++target_i) {
                    for(rights_i=0u;rights_i<4u;++rights_i) {
                        for(epoch_i=0u;epoch_i<4u;++epoch_i) {
                            for(sequence_i=0u;sequence_i<2u;++sequence_i) {
                                ou32 target=targets[target_i],epoch=0u;
                                a=states[state_id]; b=states[state_id];
                                if(epoch_i==1u) epoch=1u;
                                if(epoch_i==2u) epoch=O_NONE;
                                if(epoch_i==3u && target>=1u && target<=O_MAX)
                                    epoch=a.slots[target-1u].epoch+
                                          (opcode==O_SPAWN ? 1u : 0u);
                                event=(o_event){
                                    a.sequence+(sequence_i==0u ? 1u : 0u),
                                    opcode,actor,target,rights[rights_i],epoch
                                };
                                ou32 sa=omega_step(&a,&event,&one);
                                ou32 sb=omega_step(&b,&event,&two);
                                ++cases;
                                if(sa!=sb || sa!=one.status || sa!=two.status)
                                    return 20;
                                if(memcmp(&a,&b,sizeof(a))!=0 ||
                                   memcmp(&one,&two,sizeof(one))!=0)
                                    return 21; /* deterministic replay */
                                if(one.before_digest!=states[state_id].digest)
                                    return 22;
                                if(check_state(&a)) return 23;
                                if(sa!=O_OK) {
                                    ++rejected;
                                    if(memcmp(&a,&states[state_id],sizeof(a))!=0)
                                        return 24; /* atomic rejection */
                                    if(one.after_digest!=one.before_digest ||
                                       one.sequence!=states[state_id].sequence ||
                                       one.phase!=states[state_id].phase)
                                        return 25;
                                } else {
                                    ++accepted;
                                    if(a.sequence!=event.sequence ||
                                       a.sequence!=states[state_id].sequence+1u)
                                        return 26;
                                    if(one.phase!=a.phase || one.sequence!=a.sequence ||
                                       one.after_digest!=a.digest)
                                        return 27;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    if(cases!=126720ul || accepted+rejected!=cases)
        return 28;
    printf("OMEGA_BOUNDED_EXHAUSTIVE_PASS cases=%lu accepted=%lu rejected=%lu replay_runs=%lu\n",
           cases,accepted,rejected,2ul*cases);
    return 0;
}
