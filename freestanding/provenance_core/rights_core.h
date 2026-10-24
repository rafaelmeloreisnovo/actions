/*
 * RAFAELIA / rights_core.h — independent file-level provenance gate, v1.
 * New local implementation created 2026-10-24 for rafaelmeloreisnovo/actions.
 * Inherited Gradle Actions is NOT used as an implementation template.
 * Rights: separately applicable grant/holder remains subject to review.
 * See AUTHORSHIP_AND_CREDITS.md and the unchanged upstream MIT notice.
 * No claim of independent legal clearance or release authorization.
 */
#ifndef RAFAELIA_RIGHTS_CORE_H
#define RAFAELIA_RIGHTS_CORE_H

typedef unsigned int ra_word;
_Static_assert(sizeof(ra_word) == 4, "requires 32-bit unsigned int");

enum {
    RA_ORIGIN_UNRESOLVED = 0u,
    RA_ORIGIN_INHERITED = 1u,
    RA_ORIGIN_LOCAL = 2u,
    RA_ORIGIN_MIXED = 3u,
    RA_PROOF_SOURCE_REF = 1u << 0,
    RA_PROOF_EXACT_FILE_HASH = 1u << 1,
    RA_PROOF_RIGHTS_HOLDER = 1u << 2,
    RA_PROOF_LICENSE_SCOPE = 1u << 3,
    RA_PROOF_ATTRIBUTION = 1u << 4,
    RA_PROOF_EXACT_HEAD_TEST = 1u << 5,
    RA_PROOF_INDEPENDENT_REVIEW = 1u << 6,
    RA_ALL_PROOFS = (1u << 7) - 1u,
    RA_RIGHTS_PROOFS = (1u << 5) - 1u,
    RA_EVIDENCE_PROOFS = (3u << 5),
    RA_STATE_UNKNOWN = 0u,
    RA_STATE_BAD_INPUT = 1u,
    RA_STATE_RIGHTS_GAP = 2u,
    RA_STATE_EVIDENCE_GAP = 3u,
    RA_STATE_STRUCTURAL_CANDIDATE = 4u
};

typedef struct {
    ra_word origin;
    ra_word claimed_proofs;
} ra_provenance_input;

typedef struct {
    ra_word state;
    ra_word missing_rights;
    ra_word missing_evidence;
    ra_word release_authorized;
} ra_provenance_result;

/* Output is always fail-closed. All input bits are ASSERTIONS, not proofs. */
void ra_provenance_check(const ra_provenance_input *input,
                         ra_provenance_result *result);
#endif
