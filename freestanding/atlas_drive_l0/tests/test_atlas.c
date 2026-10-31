/* Host test (no stdlib), return code = first failing case; executable host only. */
#include "../atlas.h"
static ra_atlas_request fresh(void){
 ra_atlas_request q={0};
 q.magic=RA_MAGIC;q.version=RA_VERSION;q.sequence=7u;q.previous_sequence=6u;
 q.present=RA_PRESENT_ALL;q.scope=RA_SCOPE_PRIVATE;
 q.watchdog_a=1u;q.watchdog_b=2u;q.watchdog_limit=5u;
 q.elapsed=1u;q.ttl=20u;q.count=1u;
 q.records[0]=(ra_atlas_record){101u,3u,201u,RA_KIND_DOCUMENT,
 RA_REL_DIRECT,RA_SCOPE_PRIVATE,RA_GAP_NONE,RA_ATTEST_ALL};
 return q;
}
int main(void){
 ra_atlas_request q=fresh();ra_atlas_receipt r,s;
 ra_atlas_plan(&q,&r);
 if(r.status!=RA_PLAN_ONLY||r.index_mask!=1u||r.held_mask!=0u||
    r.accepted_count!=1u||r.drive_writes||r.claim_allowed||r.publish_authorized) return 1;
 ra_atlas_plan(&q,&s);if(r.plan_crc32c!=s.plan_crc32c) return 2;
 ra_atlas_plan((const ra_atlas_request *)0,&r);if(r.status!=RA_BAD_INPUT)return 3;
 q=fresh();q.present=RA_PRESENT_SOURCE;ra_atlas_plan(&q,&r);if(r.status!=RA_MISSING)return 4;
 q=fresh();q.previous_sequence=q.sequence;ra_atlas_plan(&q,&r);if(r.status!=RA_STALE)return 5;
 q=fresh();q.watchdog_b=0u;ra_atlas_plan(&q,&r);if(r.status!=RA_WATCHDOG)return 6;
 q=fresh();q.elapsed=q.ttl;ra_atlas_plan(&q,&r);if(r.status!=RA_TTL)return 7;
 q=fresh();q.records[0].attestation&=~RA_ATTEST_RIGHTS;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD||r.held_mask!=1u)return 8;
 q=fresh();q.records[0].gap_type=RA_GAP_WITHHELD;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD||r.gap_mask!=1u)return 9;
 q=fresh();q.scope=RA_SCOPE_PUBLIC;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 10;
 q=fresh();q.count=2u;q.records[1]=q.records[0];ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD||r.duplicates_mask!=3u||r.held_mask!=3u)return 11;
 q=fresh();q.count=2u;q.records[1]=(ra_atlas_record){102u,1u,202u,RA_KIND_BLOB,
 RA_REL_ORTHOGONAL,RA_SCOPE_PRIVATE,RA_GAP_UNKNOWN,RA_ATTEST_ALL};
 ra_atlas_plan(&q,&r);if(r.status!=RA_PARTIAL||r.index_mask!=1u||
 r.held_mask!=2u||r.gap_mask!=2u)return 12;
 q=fresh();q.records[0].relation=8u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 13;
 q=fresh();q.count=RA_MAX+1u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_BAD_INPUT)return 14;
 q=fresh();q.records[0].kind=0u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 15;
 q=fresh();q.records[0].source_key=0u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 16;
 q=fresh();q.records[0].attestation|=0x80u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 17;
 q=fresh();q.previous_sequence=0xffffffffu;q.sequence=0u;
 ra_atlas_plan(&q,&r);if(r.status!=RA_STALE)return 18;
 q=fresh();q.count=0u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_MISSING||r.accepted_count||r.drive_writes)return 19;
 q=fresh();q.records[0].visibility=3u;ra_atlas_plan(&q,&r);
 if(r.status!=RA_HOLD)return 20;
 return 0;
}
