/* RAFAELIA: proposed independent L0 dispatch contract. Authorship/license review pending.
 * See LICENSES/README.md. No Gradle Actions implementation is reused. */
#ifndef RAFAELIA_DISPATCH_L0_H
#define RAFAELIA_DISPATCH_L0_H

typedef unsigned int rd_u32;
_Static_assert(sizeof(rd_u32) == 4, "32-bit words required");

enum {
  RD_TAG = 0x52444c30u, /* RDL0 */
  RD_SCALAR = 1u, RD_NEON = 2u, RD_SIMD = 4u, RD_GPU = 8u,
  RD_ALL_CAPS = 15u, RD_CPU_CAPS = 7u,
  RD_PRESENT_CAPS = 1u, RD_PRESENT_POLICY = 2u,
  RD_PRESENT_WATCHDOG_A = 4u, RD_PRESENT_WATCHDOG_B = 8u,
  RD_PRESENT_SOURCE = 16u, RD_ALL_PRESENT = 31u,
  RD_UNKNOWN = 0u, RD_BAD_INPUT = 1u, RD_STALE = 2u,
  RD_WATCHDOG = 3u, RD_NO_ROUTE = 4u, RD_GPU_BOUNDARY = 5u,
  RD_PLAN_ONLY = 6u
};

typedef struct {
  rd_u32 tag, sequence, previous_sequence;
  rd_u32 present_mask, observed_caps, permitted_caps;
  rd_u32 preferred, watchdog_a, watchdog_b, watchdog_limit;
} rd_request;

typedef struct {
  rd_u32 status, route, fallback, rollback_required;
  rd_u32 hardware_activated, merge_authorized;
} rd_receipt;

/* Caller supplies attested inputs and owns dispatch/rollback; this routine NEVER dispatches. */
void rd_plan(const rd_request *request, rd_receipt *receipt);
#endif
