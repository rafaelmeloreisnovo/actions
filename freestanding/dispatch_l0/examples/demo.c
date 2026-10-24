/* Hosted-only demo; stdio is NOT part of dispatch.c freestanding runtime. */
#include <stdio.h>
#include "../dispatch.h"
int main(void)
{
    rd_request q={RD_TAG,9u,8u,RD_ALL_PRESENT,
      RD_SCALAR|RD_NEON,RD_SCALAR|RD_NEON,RD_NEON,4u,3u,4u};
    rd_receipt r;
    unsigned int errors=0u;
    rd_plan(&q,&r);
    printf("N1 NEON: status=%u route=%u fallback=%u rollback=%u activated=%u merge=%u\n",
      r.status,r.route,r.fallback,r.rollback_required,r.hardware_activated,r.merge_authorized);
    errors+=(unsigned int)!(r.status==RD_PLAN_ONLY&&r.route==RD_NEON&&r.fallback==0u&&r.rollback_required==0u&&r.hardware_activated==0u&&r.merge_authorized==0u);
    q.permitted_caps=RD_SCALAR;
    rd_plan(&q,&r);
    printf("N2 scalar: status=%u route=%u fallback=%u rollback=%u activated=%u merge=%u\n",
      r.status,r.route,r.fallback,r.rollback_required,r.hardware_activated,r.merge_authorized);
    errors+=(unsigned int)!(r.status==RD_PLAN_ONLY&&r.route==RD_SCALAR&&r.fallback==1u&&r.rollback_required==0u&&r.hardware_activated==0u&&r.merge_authorized==0u);
    q.preferred=RD_GPU;
    rd_plan(&q,&r);
    printf("N3 GPU deny: status=%u route=%u fallback=%u rollback=%u activated=%u merge=%u\n",
      r.status,r.route,r.fallback,r.rollback_required,r.hardware_activated,r.merge_authorized);
    errors+=(unsigned int)!(r.status==RD_GPU_BOUNDARY&&r.route==0u&&r.fallback==0u&&r.rollback_required==1u&&r.hardware_activated==0u&&r.merge_authorized==0u);
    q.preferred=RD_NEON;q.present_mask^=RD_PRESENT_WATCHDOG_B;
    rd_plan(&q,&r);
    printf("N4 unknown: status=%u route=%u fallback=%u rollback=%u activated=%u merge=%u\n",
      r.status,r.route,r.fallback,r.rollback_required,r.hardware_activated,r.merge_authorized);
    errors+=(unsigned int)!(r.status==RD_UNKNOWN&&r.route==0u&&r.fallback==0u&&r.rollback_required==1u&&r.hardware_activated==0u&&r.merge_authorized==0u);
    puts(errors?"DEMO_FAIL":"DEMO_PASS_SCOPED: hosted; no hardware activation or merge");
    return errors?1:0;
}
