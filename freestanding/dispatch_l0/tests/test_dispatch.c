/* Hosted-only deterministic falsifier. Not part of the freestanding L0 runtime. */
#include "../dispatch.h"
#define CHECK(x) do { if (!(x)) return __LINE__; } while (0)
int main(void)
{
  rd_request q = { RD_TAG, 9u, 8u, RD_ALL_PRESENT,
                   RD_SCALAR | RD_NEON, RD_SCALAR | RD_NEON,
                   RD_NEON, 4u, 3u, 4u };
  rd_receipt r;
  rd_u32 cap, policy;
  union { rd_request request; rd_receipt receipt; } shared;
  rd_plan(&q, &r);
  CHECK(r.status == RD_PLAN_ONLY && r.route == RD_NEON && r.fallback == 0u);
  CHECK(r.rollback_required == 0u && r.merge_authorized == 0u && r.hardware_activated == 0u);
  q.permitted_caps = RD_SCALAR;
  rd_plan(&q, &r); CHECK(r.status == RD_PLAN_ONLY && r.route == RD_SCALAR && r.fallback == 1u);
  q.preferred = RD_GPU;
  rd_plan(&q, &r); CHECK(r.status == RD_GPU_BOUNDARY && r.route == 0u && r.rollback_required == 1u);
  q.preferred = RD_NEON;
  q.present_mask = RD_ALL_PRESENT ^ RD_PRESENT_WATCHDOG_B;
  rd_plan(&q, &r); CHECK(r.status == RD_UNKNOWN && r.route == 0u);
  q.present_mask = RD_ALL_PRESENT;
  q.watchdog_b = 0u;
  rd_plan(&q, &r); CHECK(r.status == RD_WATCHDOG && r.route == 0u);
  q.watchdog_b = 3u;
  q.sequence = q.previous_sequence;
  rd_plan(&q, &r); CHECK(r.status == RD_STALE);
  q.previous_sequence = 0xffffffffu; q.sequence = 0u;
  rd_plan(&q, &r); CHECK(r.status == RD_STALE);
  q.previous_sequence = 8u; q.sequence = 9u;
  q.permitted_caps = RD_GPU;
  rd_plan(&q, &r); CHECK(r.status == RD_NO_ROUTE && r.route == 0u);
  q.permitted_caps = RD_ALL_CAPS;
  q.observed_caps = RD_GPU;
  rd_plan(&q, &r); CHECK(r.status == RD_NO_ROUTE);
  q.observed_caps = RD_SCALAR | RD_NEON;
  q.permitted_caps = RD_SCALAR | RD_NEON;
  q.present_mask = RD_ALL_PRESENT | 32u;
  rd_plan(&q, &r); CHECK(r.status == RD_BAD_INPUT);
  q.present_mask = RD_ALL_PRESENT;
  q.observed_caps = 0x80000000u;
  rd_plan(&q, &r); CHECK(r.status == RD_BAD_INPUT);
  q.observed_caps = RD_SCALAR | RD_NEON;
  q.tag = 0u;
  rd_plan(&q, &r); CHECK(r.status == RD_BAD_INPUT);
  q.tag = RD_TAG;
  q.preferred = 3u;
  rd_plan(&q, &r); CHECK(r.status == RD_BAD_INPUT);
  q.preferred = RD_NEON;
  q.watchdog_limit = 2u;
  rd_plan(&q, &r); CHECK(r.status == RD_WATCHDOG);
  q.watchdog_limit = 4u;
  rd_plan((const rd_request *)0, &r);
  CHECK(r.status == RD_UNKNOWN && r.rollback_required == 1u);
  rd_plan((const rd_request *)1, (rd_receipt *)0); /* output-null guards deref */
  /* Intentional input/output storage overlap, safe due to upfront snapshot. */
  shared.request = q;
  rd_plan(&shared.request, &shared.receipt);
  CHECK(shared.receipt.status == RD_PLAN_ONLY && shared.receipt.route == RD_NEON);
  /* 16x16 finite truth grid: candidate choice must be permitted and observed. */
  for (cap=0u;cap<16u;cap++) for(policy=0u;policy<16u;policy++) {
    q.observed_caps=cap; q.permitted_caps=policy; q.preferred=0u;
    rd_plan(&q,&r);
    CHECK(r.hardware_activated == 0u && r.merge_authorized == 0u);
    CHECK(r.route == 0u || (r.route & (cap & policy & RD_CPU_CAPS)) == r.route);
    CHECK((r.status == RD_PLAN_ONLY) == (r.route != 0u));
  }
  return 0;
}
