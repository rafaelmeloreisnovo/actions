/* Host-only falsifier. Never linked into the freestanding ELF image. */
#include <stdio.h>
#include "../kernel4.c"

static unsigned parity_reference(unsigned nibble)
{
    unsigned count = 0u;
    for (unsigned b = 0u; b < 4u; ++b) {
        count += (nibble >> b) & 1u;
    }
    return count & 1u;
}

int main(void)
{
    unsigned frame;
    for (frame = 0u; frame < 256u; ++frame) {
        unsigned high = (frame >> 4) & 15u;
        unsigned low = frame & 15u;
        unsigned expected = (parity_reference(high) << 1) |
                            parity_reference(low);
        k4_cell absent = { (k4_u8)frame, K4_VALUE_ABSENT };
        k4_cell present = { (k4_u8)frame, K4_VALUE_PRESENT };
        if ((unsigned)K4_PACK(high, low) != frame) return 1;
        if ((unsigned)K4_HI(frame) != high ||
            (unsigned)K4_LO(frame) != low) return 2;
        if ((unsigned)k4_parity2((k4_u8)frame) != expected) return 3;
        if ((unsigned)k4_value_if_present(absent) != 0u) return 4;
        if ((unsigned)k4_value_if_present(present) != frame) return 5;
    }
    for (unsigned row = 0u; row < K4_ROWS; ++row) {
        if (k4_web[row].present != K4_VALUE_ABSENT) return 6;
    }
    /* Valid known zero frame differs from a missing frame by presence. */
    {
        k4_cell missing_zero = {0u, K4_VALUE_ABSENT};
        k4_cell known_zero = {0u, K4_VALUE_PRESENT};
        if (missing_zero.present == known_zero.present) return 7;
        if (k4_value_if_present(missing_zero) != 0u ||
            k4_value_if_present(known_zero) != 0u) return 8;
    }
    puts("KERNEL4_HOST_256_FRAMES_PASS; SCOPE=HOST_ONLY_NO_ELF_BOOT");
    return 0;
}
