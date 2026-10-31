/* JNI primitive ABI only: no libc, heap or external imported symbols. */
#include "atlas.h"
typedef signed int jint;
__attribute__((visibility("default")))
jint Java_org_rafaelia_atlas_AtlasWizard_nativePlan(void *env, void *object,
    jint key, jint revision, jint scope, jint gap, jint attestation){
 ra_atlas_request q;ra_atlas_receipt r;
 volatile ra_u32 *words=(volatile ra_u32 *)&q;ra_u32 i;
 for(i=0u;i<(ra_u32)(sizeof(q)/sizeof(ra_u32));i++)words[i]=0u;
 (void)env;(void)object;
 q.magic=RA_MAGIC;q.version=RA_VERSION;q.sequence=2u;q.previous_sequence=1u;
 q.present=RA_PRESENT_ALL;q.scope=(ra_u32)scope;
 q.watchdog_a=1u;q.watchdog_b=1u;q.watchdog_limit=2u;
 q.elapsed=0u;q.ttl=1u;q.count=1u;
 q.records[0].source_key=(ra_u32)key;
 q.records[0].revision=(ra_u32)revision;
 q.records[0].target_key=1u;q.records[0].kind=RA_KIND_DOCUMENT;
 q.records[0].relation=RA_REL_DIRECT;q.records[0].visibility=RA_SCOPE_PRIVATE;
 q.records[0].gap_type=(ra_u32)gap;q.records[0].attestation=(ra_u32)attestation;
 ra_atlas_plan(&q,&r);return (jint)r.status;
}
