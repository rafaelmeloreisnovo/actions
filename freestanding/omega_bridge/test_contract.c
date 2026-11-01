/* Host-only falsifiers for the freestanding numeric primitive. */
#include "omega_core.h"
#include <stdint.h>
int main(void) {
    uint64_t out = UINT64_C(999);
    int32_t a[3] = { 0, INT32_MIN, 3<<16 };
    int32_t b[3] = { 0, INT32_MIN, 1<<16 };
    uint32_t w[3] = { 1<<16, 1<<16, 1<<16 };
    if (omega_residual_q16(a,b,w,3,&out) != OMEGA_OK || out != UINT64_C(17179869184)) return 1;
    if (omega_residual_q16(b,a,w,3,&out) != OMEGA_OK || out != UINT64_C(17179869184)) return 2;
    w[2] = 0;
    if (omega_residual_q16(a,b,w,3,&out) != OMEGA_OK || out != 0) return 3;
    if (omega_residual_q16(a,b,w,0,&out) != OMEGA_EMPTY || out != 0) return 4;
    if (omega_residual_q16(a,b,w,3,0) != OMEGA_RANGE) return 5;
    if (omega_residual_q16(a,0,w,3,&out) != OMEGA_RANGE) return 6;
    a[0] = INT32_MAX; b[0] = INT32_MIN; w[0] = UINT32_MAX;
    if (omega_residual_q16(a,b,w,3,&out) != OMEGA_OVERFLOW) return 7;
    return 0;
}
