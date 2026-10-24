/*
 * RAFAELIA / rights_core.c — independent bounded, deterministic policy core.
 * New local source, 2026-10-24. No Gradle/Node code or runtime dependency.
 * Distinct source/holder/license evidence must be verified OUTSIDE this core.
 * A structural candidate is never an authorization to release or merge.
 */
#include "rights_core.h"

void ra_provenance_check(const ra_provenance_input *input,
                         ra_provenance_result *result)
{
    /* The absent output pointer cannot be written; no side effects exist. */
    if (result == (ra_provenance_result *)0) return;

    /* Deterministically initialize every output before reading untrusted data. */
    result->state = RA_STATE_UNKNOWN;
    result->missing_rights = RA_RIGHTS_PROOFS;
    result->missing_evidence = RA_EVIDENCE_PROOFS;
    result->release_authorized = 0u;

    /* Unknown origin is a genuine unknown, not a class to auto-approve. */
    if (input == (const ra_provenance_input *)0) return;
    if (input->origin == RA_ORIGIN_UNRESOLVED) return;

    /* Combined paths need file-by-file split; one flag set cannot certify both. */
    if (input->origin == RA_ORIGIN_MIXED) return;
    if (input->origin != RA_ORIGIN_INHERITED &&
        input->origin != RA_ORIGIN_LOCAL) {
        result->state = RA_STATE_BAD_INPUT;
        return;
    }
    /* Reject arbitrary/unknown bits rather than discarding input mistakes. */
    if ((input->claimed_proofs & ~((ra_word)RA_ALL_PROOFS)) != 0u) {
        result->state = RA_STATE_BAD_INPUT;
        return;
    }

    /* The same evidence obligation applies to either authorial class. */
    result->missing_rights = RA_RIGHTS_PROOFS & ~input->claimed_proofs;
    result->missing_evidence = RA_EVIDENCE_PROOFS & ~input->claimed_proofs;

    /* Ordering matters: unresolved rights take priority over test status. */
    if (result->missing_rights != 0u) {
        result->state = RA_STATE_RIGHTS_GAP;
    } else if (result->missing_evidence != 0u) {
        result->state = RA_STATE_EVIDENCE_GAP;
    } else {
        result->state = RA_STATE_STRUCTURAL_CANDIDATE;
    }
    /* Unconditionally fail closed: external review/provider authority required. */
}
