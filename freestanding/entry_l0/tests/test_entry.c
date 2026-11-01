#include "../entry.h"
#define CHECK(x) do { if (!(x)) return __LINE__; } while (0)
/* Harness only: depends on hosted C entrypoint, core itself does not. */
int main(void) {
    rf_u8 src[RF_MAX_BYTES], dst[RF_MAX_BYTES];
    rf_receipt out;
    rf_request req;
    rf_u32 i, saved;
    req.abi = RF_ABI_VERSION;
    req.source = src;
    req.destination = dst;
    req.length = 32u;
    req.policy = 0u;
    req.verified_capabilities = 0u;
    req.watchdog_work_units = 32u;
    req.watchdog_progress_ticks = 2u;
    req.key = 0x5Au;
    for (i=0u;i<RF_MAX_BYTES;++i) { src[i]=(rf_u8)i; dst[i]=0x7Bu; }
    out.status=0xBADu; out.backend=0xBADu; out.fallback_used=0xBADu;
    out.fingerprint=0xBADu; out.work_units=0xBADu; out.progress_ticks=0xBADu;
    CHECK(rf_execute(&req,&out)==RF_OK);
    CHECK(out.status==RF_OK && out.backend==RF_BACKEND_SCALAR);
    CHECK(out.work_units==32u && out.progress_ticks==2u);
    saved=out.fingerprint;
    for(i=0u;i<32u;++i) CHECK(dst[i]==(rf_u8)(src[i]^0x5Au));
    for(i=32u;i<RF_MAX_BYTES;++i) CHECK(dst[i]==0x7Bu);
    /* Requested unsupported GPU is HOLD unless explicitly permitted fallback. */
    req.policy=RF_REQUEST_GPU;
    CHECK(rf_execute(&req,&out)==RF_BACKEND_UNAVAILABLE);
    CHECK(out.fingerprint==saved && dst[0]==0x5Au);
    req.policy=RF_REQUEST_GPU|RF_ALLOW_FALLBACK;
    CHECK(rf_execute(&req,&out)==RF_OK);
    CHECK(out.fallback_used==1u && out.backend==RF_BACKEND_SCALAR);
    /* Simulated / unverified NEON can never cause silent promotion. */
    req.verified_capabilities=0u; req.policy=RF_REQUIRE_NEON;
    CHECK(rf_execute(&req,&out)==RF_BACKEND_UNAVAILABLE);
    req.policy=RF_REQUIRE_NEON|RF_ALLOW_FALLBACK;
    CHECK(rf_execute(&req,&out)==RF_OK && out.fallback_used==1u);
    /* Dual watchdog blocks and leaves output/receipt untouched. */
    req.policy=0u; req.watchdog_work_units=31u;
    saved=out.fingerprint;
    CHECK(rf_execute(&req,&out)==RF_WATCHDOG_HOLD);
    CHECK(out.fingerprint==saved && dst[1]==(rf_u8)(src[1]^0x5Au));
    req.watchdog_work_units=32u; req.watchdog_progress_ticks=1u;
    CHECK(rf_execute(&req,&out)==RF_WATCHDOG_HOLD);
    req.watchdog_progress_ticks=2u; req.length=RF_MAX_BYTES+1u;
    CHECK(rf_execute(&req,&out)==RF_BOUND_EXCEEDED);
    req.length=32u; req.abi=0u;
    CHECK(rf_execute(&req,&out)==RF_BAD_REQUEST);
    req.abi=RF_ABI_VERSION; req.policy=0x80000000u;
    CHECK(rf_execute(&req,&out)==RF_BAD_REQUEST);
    req.policy=0u; req.verified_capabilities=0x80000000u;
    CHECK(rf_execute(&req,&out)==RF_BAD_REQUEST);
    req.verified_capabilities=0u;
    CHECK(rf_execute((const rf_request *)0,&out)==RF_BAD_REQUEST);
    CHECK(rf_execute(&req,(rf_receipt *)0)==RF_BAD_REQUEST);
    /* Reject destination overlap with control/receipt to keep all-or-nothing commit. */
    req.destination=(rf_u8 *)&out;
    CHECK(rf_execute(&req,&out)==RF_BAD_REQUEST);
    CHECK(out.fingerprint==saved);
    req.destination=(rf_u8 *)&req;
    CHECK(rf_execute(&req,&out)==RF_BAD_REQUEST);
    /* Aliasing is supported by stack stage, not memcpy, malloc or libc. */
    req.destination=src;
    CHECK(rf_execute(&req,&out)==RF_OK);
    for(i=0u;i<32u;++i) CHECK(src[i]==(rf_u8)(i ^ 0x5Au));
    /* Zero length with null buffers is well-defined. */
    req.length=0u; req.source=(const rf_u8 *)0; req.destination=(rf_u8 *)0;
    req.watchdog_work_units=0u; req.watchdog_progress_ticks=0u;
    CHECK(rf_execute(&req,&out)==RF_OK && out.work_units==0u);
    return 0;
}
