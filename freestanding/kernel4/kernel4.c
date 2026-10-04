/*
 * RAFAELIA Kernel4 freestanding core.
 *
 * Contract:
 *   - one frame = high 4-bit nibble | low 4-bit nibble
 *   - no libc, heap, syscalls, I/O, runtime startup, or external symbols
 *   - glyph semantics beyond the 4|4 framing remain TOKEN_VAZIO
 *
 * This file is an independent local delta; inherited Gradle Actions code is
 * not modified and remains governed by THIRD_PARTY_PROVENANCE.md.
 */

typedef unsigned char k4_u8;

enum {
    K4_NIBBLE_MASK = 0x0f,
    K4_NIBBLE_BITS = 4,
    K4_FRAME_BITS = 8,
    K4_ROWS = 8
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
 * Structural eight-row web. Only the demonstrated 4|4 frame is encoded.
 * The inner emoji/glyph operators are deliberately not assigned opcodes.
 */
static const k4_u8 k4_web[K4_ROWS] = {
    K4_PACK(0, 0), K4_PACK(0, 0), K4_PACK(0, 0), K4_PACK(0, 0),
    K4_PACK(0, 0), K4_PACK(0, 0), K4_PACK(0, 0), K4_PACK(0, 0)
};

static volatile k4_u8 k4_receipt_frame;
static volatile k4_u8 k4_receipt_parity;

__attribute__((used, section(".text.kernel4_entry"), noreturn))
void kernel4_entry(void)
{
    /* Explicit rows keep the core deterministic and avoid a hosted iterator. */
    k4_u8 folded = (k4_u8)(
        k4_web[0] ^ k4_web[1] ^ k4_web[2] ^ k4_web[3] ^
        k4_web[4] ^ k4_web[5] ^ k4_web[6] ^ k4_web[7]);

    k4_receipt_frame = folded;
    k4_receipt_parity = k4_parity2(folded);

    /* A freestanding image has no host to return to. */
    for (;;) {
        __asm__ volatile("" ::: "memory");
    }
}
