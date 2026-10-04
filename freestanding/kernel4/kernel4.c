/*
 * RAFAELIA Kernel4 freestanding core.
 *
 * Contract:
 *   - one frame = high 4-bit nibble | low 4-bit nibble
 *   - no libc, heap, syscalls, I/O, runtime startup, or external symbols
 *   - glyph semantics beyond the 4|4 framing remain TOKEN_VAZIO
 *   - TOKEN_VAZIO is absence of an authorized payload, never numeric zero
 *
 * This file is an independent local delta; inherited Gradle Actions code is
 * not modified and remains governed by THIRD_PARTY_PROVENANCE.md.
 */

typedef unsigned char k4_u8;

typedef struct {
    k4_u8 value;
    k4_u8 present;
} k4_cell;

enum {
    K4_NIBBLE_MASK = 0x0f,
    K4_NIBBLE_BITS = 4,
    K4_FRAME_BITS = 8,
    K4_ROWS = 8,
    K4_VALUE_ABSENT = 0,
    K4_VALUE_PRESENT = 1
};

#define K4_NIBBLE(x) ((k4_u8)((x) & K4_NIBBLE_MASK))
#define K4_PACK(hi, lo) \
    ((k4_u8)((K4_NIBBLE(hi) << K4_NIBBLE_BITS) | K4_NIBBLE(lo)))
#define K4_HI(frame) K4_NIBBLE((k4_u8)((frame) >> K4_NIBBLE_BITS))
#define K4_LO(frame) K4_NIBBLE(frame)

_Static_assert(K4_PACK(0x0a, 0x05) == 0xa5, "4|4 pack invariant");
_Static_assert(K4_HI(0xa5) == 0x0a, "high nibble invariant");
_Static_assert(K4_LO(0xa5) == 0x05, "low nibble invariant");
_Static_assert(K4_FRAME_BITS == (K4_NIBBLE_BITS + K4_NIBBLE_BITS),
               "frame width invariant");
_Static_assert(K4_VALUE_ABSENT != K4_VALUE_PRESENT,
               "absence and known-value states must be distinct");

/* Two parity bits: one for each nibble. */
static k4_u8 k4_parity4(k4_u8 value)
{
    k4_u8 x = K4_NIBBLE(value);
    x = (k4_u8)(x ^ (k4_u8)(x >> 2));
    x = (k4_u8)(x ^ (k4_u8)(x >> 1));
    return (k4_u8)(x & 1u);
}

static k4_u8 k4_parity2(k4_u8 frame)
{
    return (k4_u8)((k4_parity4(K4_HI(frame)) << 1) |
                   k4_parity4(K4_LO(frame)));
}

/*
 * Structural eight-row web. The 4|4 container is known, but the inner
 * emoji/glyph operators have no authorized numeric payload yet.
 *
 * `present == 0` means the value field is ignored. It is an absence bit,
 * not an encoding of TOKEN_VAZIO as zero. Therefore a future known frame
 * 0x00 remains representable unambiguously as { 0x00, K4_VALUE_PRESENT }.
 */
static const k4_cell k4_web[K4_ROWS] = {
    { 0u, K4_VALUE_ABSENT }, { 0u, K4_VALUE_ABSENT },
    { 0u, K4_VALUE_ABSENT }, { 0u, K4_VALUE_ABSENT },
    { 0u, K4_VALUE_ABSENT }, { 0u, K4_VALUE_ABSENT },
    { 0u, K4_VALUE_ABSENT }, { 0u, K4_VALUE_ABSENT }
};

static k4_u8 k4_value_if_present(k4_cell cell)
{
    k4_u8 mask = (k4_u8)(0u - (k4_u8)(cell.present & 1u));
    return (k4_u8)(cell.value & mask);
}

static volatile k4_u8 k4_receipt_frame;
static volatile k4_u8 k4_receipt_parity;
static volatile k4_u8 k4_receipt_present_rows;

__attribute__((used, section(".text.kernel4_entry"), noreturn))
void kernel4_entry(void)
{
    /* Explicit rows keep the core deterministic and avoid a hosted iterator. */
    k4_u8 folded = (k4_u8)(
        k4_value_if_present(k4_web[0]) ^ k4_value_if_present(k4_web[1]) ^
        k4_value_if_present(k4_web[2]) ^ k4_value_if_present(k4_web[3]) ^
        k4_value_if_present(k4_web[4]) ^ k4_value_if_present(k4_web[5]) ^
        k4_value_if_present(k4_web[6]) ^ k4_value_if_present(k4_web[7]));

    k4_u8 present_rows = (k4_u8)(
        ((k4_web[0].present & 1u) << 0) |
        ((k4_web[1].present & 1u) << 1) |
        ((k4_web[2].present & 1u) << 2) |
        ((k4_web[3].present & 1u) << 3) |
        ((k4_web[4].present & 1u) << 4) |
        ((k4_web[5].present & 1u) << 5) |
        ((k4_web[6].present & 1u) << 6) |
        ((k4_web[7].present & 1u) << 7));

    k4_receipt_frame = folded;
    k4_receipt_parity = k4_parity2(folded);
    k4_receipt_present_rows = present_rows;

    /* A freestanding image has no host to return to. */
    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}
