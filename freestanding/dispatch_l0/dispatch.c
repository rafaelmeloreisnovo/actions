/* RAFAELIA L0 isolated deterministic decision: no I/O, heap, syscalls, libc.
 * New proposed authored delta, not Gradle/Node source or a device driver.
 * External caller identity, true capability and watchdog freshness are NOT verified here. */
#include "dispatch.h"

void rd_plan(const rd_request *request, rd_receipt *receipt)
{
  rd_u32 tag = 0u, sequence = 0u, previous = 0u, present = 0u;
  rd_u32 observed = 0u, permitted = 0u, preferred = 0u;
  rd_u32 wda = 0u, wdb = 0u, limit = 0u;
  rd_u32 eligible = 0u, chosen = 0u, state = RD_UNKNOWN;

  if (receipt == (rd_receipt *)0) return;
  /* Read all words before writing receipt: supports overlapping caller buffers. */
  if (request != (const rd_request *)0) {
    tag = request->tag;
    sequence = request->sequence;
    previous = request->previous_sequence;
    present = request->present_mask;
    observed = request->observed_caps;
    permitted = request->permitted_caps;
    preferred = request->preferred;
    wda = request->watchdog_a;
    wdb = request->watchdog_b;
    limit = request->watchdog_limit;
  }
  /* Default is denial; zero here is known denied state, not TOKEN_VAZIO. */
  receipt->status = RD_UNKNOWN;
  receipt->route = 0u;
  receipt->fallback = 0u;
  receipt->rollback_required = 1u;
  receipt->hardware_activated = 0u;
  receipt->merge_authorized = 0u;

  if (request == (const rd_request *)0) return;
  if (tag != RD_TAG || (present & ~RD_ALL_PRESENT) != 0u ||
      (observed & ~RD_ALL_CAPS) != 0u ||
      (permitted & ~RD_ALL_CAPS) != 0u ||
      (preferred != 0u && preferred != RD_SCALAR &&
       preferred != RD_NEON && preferred != RD_SIMD && preferred != RD_GPU)) {
    receipt->status = RD_BAD_INPUT;
    return;
  }
  if (present != RD_ALL_PRESENT) return; /* missing != zero */
  if (previous == 0xffffffffu || sequence != previous + 1u) {
    receipt->status = RD_STALE;
    return;
  }
  if (limit == 0u || wda == 0u || wdb == 0u || wda > limit || wdb > limit) {
    receipt->status = RD_WATCHDOG;
    return;
  }
  if (preferred == RD_GPU) {
    receipt->status = RD_GPU_BOUNDARY;
    return;
  }
  eligible = (observed & permitted) & RD_CPU_CAPS;
  if (preferred == RD_NEON && (eligible & RD_NEON)) chosen = RD_NEON;
  else if (preferred == RD_SIMD && (eligible & RD_SIMD)) chosen = RD_SIMD;
  else if (preferred == RD_SCALAR && (eligible & RD_SCALAR)) chosen = RD_SCALAR;
  else if (preferred == 0u && (eligible & RD_NEON)) chosen = RD_NEON;
  else if (preferred == 0u && (eligible & RD_SIMD)) chosen = RD_SIMD;
  else if (eligible & RD_SCALAR) chosen = RD_SCALAR;

  state = chosen != 0u ? RD_PLAN_ONLY : RD_NO_ROUTE;
  receipt->status = state;
  receipt->route = chosen;
  receipt->fallback = (rd_u32)(chosen != 0u && preferred != 0u && chosen != preferred);
  receipt->rollback_required = (rd_u32)(chosen == 0u);
  /* A PLAN cannot activate GPU/NEON/CPU hardware, approve PR or authorize release. */
}
