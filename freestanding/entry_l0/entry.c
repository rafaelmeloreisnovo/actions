#include "entry.h"
typedef __UINTPTR_TYPE__ rf_uptr;
#if defined(__ARM_NEON) || defined(__ARM_NEON__)
#include <arm_neon.h>
#define RF_HAS_NEON_KERNEL 1
#else
#define RF_HAS_NEON_KERNEL 0
#endif

rf_u32 rf_execute(const rf_request *request, rf_receipt *receipt) {
    rf_u8 stage[RF_MAX_BYTES];
    rf_u32 i = 0u;
    rf_u32 blocks = 0u;
    rf_u32 need_fallback = 0u;
    rf_u32 backend = RF_BACKEND_SCALAR;
    rf_u32 sum = 0xA17E09C3u;
    rf_u32 len;
    rf_uptr ds, rs, qs, limit;
    if (!request || !receipt) return RF_BAD_REQUEST;
    if (request->abi != RF_ABI_VERSION) return RF_BAD_REQUEST;
    len = request->length;
    if (len > RF_MAX_BYTES) return RF_BOUND_EXCEEDED;
    if (len && (!request->source || !request->destination)) return RF_BAD_REQUEST;
    /* Ensure commit cannot overwrite the request or receipt. Input/output alias is okay. */
    ds = (rf_uptr)request->destination;
    rs = (rf_uptr)receipt;
    qs = (rf_uptr)request;
    limit = ~(rf_uptr)0;
    if (rs > limit - sizeof(*receipt) || qs > limit - sizeof(*request)) return RF_BAD_REQUEST;
    if (len && (ds > limit - len ||
        (ds < rs + sizeof(*receipt) && rs < ds + len) ||
        (ds < qs + sizeof(*request) && qs < ds + len))) return RF_BAD_REQUEST;
    if ((request->policy & ~RF_POLICY_KNOWN) != 0u) return RF_BAD_REQUEST;
    if ((request->verified_capabilities & ~RF_CAP_NEON_VERIFIED) != 0u) return RF_BAD_REQUEST;
    blocks = (len + 15u) / 16u;
    /* Logical watchdog budgets are NOT elapsed-time/energy monitors. */
    if (request->watchdog_work_units < len || request->watchdog_progress_ticks < blocks)
        return RF_WATCHDOG_HOLD;
    if ((request->policy & (RF_REQUEST_GPU | RF_REQUEST_NUMA | RF_REQUEST_ART | RF_REQUEST_DEX)) != 0u)
        need_fallback = 1u;
    if ((request->policy & RF_REQUIRE_NEON) != 0u) {
        if ((request->verified_capabilities & RF_CAP_NEON_VERIFIED) == 0u || !RF_HAS_NEON_KERNEL)
            need_fallback = 1u;
        else if (!need_fallback) backend = RF_BACKEND_NEON;
    }
    if (need_fallback && ((request->policy & RF_ALLOW_FALLBACK) == 0u))
        return RF_BACKEND_UNAVAILABLE;
    if (need_fallback) backend = RF_BACKEND_SCALAR;
#if RF_HAS_NEON_KERNEL
    if (backend == RF_BACKEND_NEON) {
        uint8x16_t key16 = vdupq_n_u8(request->key);
        for (; i + 16u <= len; i += 16u) {
            uint8x16_t a = vld1q_u8((const unsigned char *)(request->source + i));
            vst1q_u8((unsigned char *)(stage + i), veorq_u8(a, key16));
        }
    }
#endif
    for (; i < len; ++i) stage[i] = (rf_u8)(request->source[i] ^ request->key);
    for (i = 0u; i < len; ++i)
        sum = ((sum << 5u) | (sum >> 27u)) ^ (rf_u32)stage[i] ^ (i * 0x9E37u);
    /* Commit only after all error paths. Stage supports source/destination aliasing. */
    for (i = 0u; i < len; ++i) request->destination[i] = stage[i];
    receipt->status = RF_OK;
    receipt->backend = backend;
    receipt->fallback_used = need_fallback;
    receipt->fingerprint = sum;
    receipt->work_units = len;
    receipt->progress_ticks = blocks;
    return RF_OK;
}
