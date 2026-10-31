/* RAFAELIA Atlas L0: isolated authorial candidate, license grant pending.
 * No libc, heap, syscalls, networking, Android or Drive access. */
#ifndef RA_ATLAS_L0_H
#define RA_ATLAS_L0_H

typedef unsigned int ra_u32;
_Static_assert(sizeof(ra_u32)==4, "requires 32-bit words");

enum {
 RA_MAGIC=0x52415431u, RA_VERSION=1u, RA_MAX=16u,
 RA_PRESENT_SOURCE=1u, RA_PRESENT_AUTHORITY=2u,
 RA_PRESENT_POLICY=4u, RA_PRESENT_WATCHDOG=8u,
 RA_PRESENT_TTL=16u, RA_PRESENT_ALL=31u,
 RA_ATTEST_SOURCE=1u, RA_ATTEST_PROVENANCE=2u,
 RA_ATTEST_RIGHTS=4u, RA_ATTEST_DESTINATION=8u,
 RA_ATTEST_ALL=15u,
 RA_SCOPE_PUBLIC=1u, RA_SCOPE_PRIVATE=2u,
 RA_KIND_DOCUMENT=1u, RA_KIND_CODE=2u, RA_KIND_BLOB=3u,
 RA_KIND_OBSERVATION=4u,
 RA_REL_DIRECT=1u, RA_REL_INVERSE=2u, RA_REL_DERIVED=3u,
 RA_REL_ANTIDERIVED=4u, RA_REL_RECURSIVE=5u,
 RA_REL_ORTHOGONAL=6u, RA_REL_INTEGRATIVE=7u,
 RA_GAP_NONE=0u, RA_GAP_UNKNOWN=1u, RA_GAP_UNMEASURED=2u,
 RA_GAP_CONTRADICTORY=3u, RA_GAP_WITHHELD=4u,
 RA_GAP_IRRECOVERABLE=5u, RA_GAP_OUT_OF_DOMAIN=6u,
 RA_GAP_UNIDENTIFIABLE=7u,
 RA_BAD_INPUT=1u, RA_MISSING=2u, RA_STALE=3u, RA_WATCHDOG=4u,
 RA_TTL=5u, RA_HOLD=6u, RA_PARTIAL=7u, RA_PLAN_ONLY=8u
};

typedef struct {
 ra_u32 source_key, revision, target_key, kind, relation;
 ra_u32 visibility, gap_type, attestation;
} ra_atlas_record;

typedef struct {
 ra_u32 magic, version, sequence, previous_sequence;
 ra_u32 present, scope, watchdog_a, watchdog_b;
 ra_u32 watchdog_limit, elapsed, ttl, count;
 ra_atlas_record records[RA_MAX];
} ra_atlas_request;

typedef struct {
 ra_u32 status, index_mask, held_mask, duplicates_mask, gap_mask;
 ra_u32 accepted_count, held_count, plan_crc32c;
 ra_u32 drive_writes, publish_authorized, claim_allowed;
} ra_atlas_receipt;

/* Host owns capability attestations, network auth, Drive transactions and readback.
 * One bounded deterministic plan function. Never performs a write. */
void ra_atlas_plan(const ra_atlas_request *req, ra_atlas_receipt *out);
#endif
