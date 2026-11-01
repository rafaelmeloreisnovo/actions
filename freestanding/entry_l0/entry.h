#ifndef RAFAELIA_ENTRY_L0_H
#define RAFAELIA_ENTRY_L0_H
/* Candidate RAFAELIA implementation: ownership and license grant pending. */
/* Freestanding C ABI; no host, Gradle, JVM, JNI, ART, SDK or memory allocator dependency. */
typedef unsigned char rf_u8;
typedef unsigned int rf_u32;
#define RF_ABI_VERSION 1u
#define RF_MAX_BYTES 256u
#define RF_CAP_NEON_VERIFIED 1u
#define RF_ALLOW_FALLBACK 1u
#define RF_REQUIRE_NEON 2u
#define RF_REQUEST_GPU 4u
#define RF_REQUEST_NUMA 8u
#define RF_REQUEST_ART 16u
#define RF_REQUEST_DEX 32u
#define RF_POLICY_KNOWN 63u
#define RF_OK 0u
#define RF_BAD_REQUEST 1u
#define RF_BOUND_EXCEEDED 2u
#define RF_WATCHDOG_HOLD 3u
#define RF_BACKEND_UNAVAILABLE 4u
#define RF_BACKEND_SCALAR 1u
#define RF_BACKEND_NEON 2u
/* Pointers in this ABI are process-local. No serialized ABI / pointer transport allowed. */
typedef struct {
    rf_u32 abi;
    const rf_u8 *source;
    rf_u8 *destination;
    rf_u32 length;
    rf_u32 policy;
    rf_u32 verified_capabilities; /* Assertion from a trusted adapter, not HW attestation. */
    rf_u32 watchdog_work_units;
    rf_u32 watchdog_progress_ticks;
    rf_u8 key;
} rf_request;
typedef struct {
    rf_u32 status;
    rf_u32 backend;
    rf_u32 fallback_used;
    rf_u32 fingerprint;
    rf_u32 work_units;
    rf_u32 progress_ticks;
} rf_receipt;
/* Returns status; on failure leaves destination and receipt unchanged (rollback by design). */
rf_u32 rf_execute(const rf_request *request, rf_receipt *receipt);
#endif
