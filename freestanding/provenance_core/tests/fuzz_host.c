/*
 * RAFAELIA: independently written HOST-ONLY bounded C falsifier.
 * Sanitizer runtime is never linked into the freestanding production core.
 * Provenance: local RAFAELIA delta. Claim_allowed=false pending external gates.
 */
#include "../rights_core.h"

int main(void) {
    ra_word origin, claimed, bit, rights, evidence, expected;
    ra_provenance_input in;
    ra_provenance_result out;
    for (origin = RA_ORIGIN_INHERITED; origin <= RA_ORIGIN_LOCAL; ++origin) {
        for (claimed = 0u; claimed <= RA_ALL_PROOFS; ++claimed) {
            in.origin = origin; in.claimed_proofs = claimed;
            ra_provenance_check(&in, &out);
            rights = RA_RIGHTS_PROOFS & ~claimed;
            evidence = RA_EVIDENCE_PROOFS & ~claimed;
            expected = rights ? RA_STATE_RIGHTS_GAP :
                       evidence ? RA_STATE_EVIDENCE_GAP : RA_STATE_STRUCTURAL_CANDIDATE;
            if (out.state != expected || out.missing_rights != rights ||
                out.missing_evidence != evidence || out.release_authorized) return 1;
        }
    }
    in.origin = RA_ORIGIN_LOCAL;
    for (bit = 7u; bit < 32u; ++bit) {
        in.claimed_proofs = RA_ALL_PROOFS | ((ra_word)1u << bit);
        ra_provenance_check(&in, &out);
        if (out.state != RA_STATE_BAD_INPUT || out.release_authorized) return 2;
    }
    /* Reusing aligned storage for request and receipt must preserve meaning. */
    out.state = RA_ORIGIN_LOCAL;
    out.missing_rights = RA_ALL_PROOFS;
    ra_provenance_check((const ra_provenance_input *)(const void *)&out, &out);
    if (out.state != RA_STATE_STRUCTURAL_CANDIDATE || out.release_authorized) return 3;
    in.origin = RA_ORIGIN_MIXED; in.claimed_proofs = RA_ALL_PROOFS;
    ra_provenance_check(&in, &out);
    if (out.state != RA_STATE_UNKNOWN || out.release_authorized) return 4;
    return 0;
}
