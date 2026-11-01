/* Independent RAFAELIA lab adapter. No libc, heap, IO, OS or physical claims.
 * Origin: locally supplied RAFAELIA_OMEGA_freestanding_lab.zip. */
#include "omega_core.h"
int omega_bridge_residual_q16(const int32_t *observed, const int32_t *predicted,
                              const uint32_t *weight, size_t count, uint64_t *out) {
    return omega_residual_q16(observed, predicted, weight, count, out);
}
