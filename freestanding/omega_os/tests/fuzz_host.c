/* HOSTED SANITIZER HARNESS. Kernel under test stays freestanding.
 * Validates rejection atomicity and one-running-task invariant.
 */
#include <stdio.h>
#include <string.h>
#include "../omega_core.h"
static unsigned rnd(unsigned *x){*x=*x*1664525u+1013904223u;return *x;}
int main(void){
 o_context c,prev; o_receipt r; o_event e;
 unsigned seed=0x20261013u,i,j,active,st;
 omega_init(&c,1234u);
 e=(o_event){1u,O_BOOT,O_ROOT,O_NONE,0u};
 if(omega_step(&c,&e,&r)!=O_OK)return 1;
 for(i=0;i<30000u;i++){
  prev=c;
  e.sequence=(rnd(&seed)&15u)==0u?c.sequence:c.sequence+1u;
  e.opcode=(rnd(&seed)%13u);
  e.actor=(rnd(&seed)%11u);
  e.target=(rnd(&seed)&1u)?O_NONE:rnd(&seed)%11u;
  e.rights=rnd(&seed)%17u;
  st=omega_step(&c,&e,&r);
  if(st!=r.status)return 2;
  if(st!=O_OK&&memcmp(&c,&prev,sizeof(c))!=0)return 3;
  active=0;
  for(j=0;j<O_MAX;j++){
   if(c.slots[j].state>O_FAULTED)return 4;
   if(c.slots[j].state==O_RUNNING)active++;
   if(c.slots[j].state==O_EMPTY &&
      (c.slots[j].rights!=0u||c.slots[j].owner!=0u))return 5;
  }
  if(active>1u)return 6;
  if(c.running==O_NONE&&active!=0u)return 7;
  if(c.running!=O_NONE&&
     (c.running>=O_MAX||c.slots[c.running].state!=O_RUNNING))return 8;
  if(st==O_OK&&c.sequence!=prev.sequence+1u)return 9;
 }
 puts("OMEGA_SANITIZER_FALSIFIER_PASS_30000");
 return 0;
}
