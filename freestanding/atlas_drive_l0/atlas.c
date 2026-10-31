/* RAFAELIA Atlas L0 / fixed-memory, no libc, no allocator, no I/O.
 * CRC-32C detects accidental plan changes; it is NOT a signature, MAC or cipher.
 * Sensitive source IDs or CRCs must not be published as public receipts. */
#include "atlas.h"

void ra_atlas_plan(const ra_atlas_request *req, ra_atlas_receipt *out)
{
 ra_u32 i,j,acc=0u,held=0u,dup=0u,gaps=0u,crc=0xffffffffu,k;
 ra_u32 count=0u,accepted_count=0u,held_count=0u;
 if(out==(ra_atlas_receipt *)0) return;
 out->status=RA_BAD_INPUT;
 out->index_mask=0u;out->held_mask=0u;out->duplicates_mask=0u;
 out->gap_mask=0u;out->accepted_count=0u;out->held_count=0u;
 out->plan_crc32c=0u;out->drive_writes=0u;
 out->publish_authorized=0u;out->claim_allowed=0u;
 if(req==(const ra_atlas_request *)0) return;
 if(req->magic!=RA_MAGIC||req->version!=RA_VERSION||
    req->count>RA_MAX||(req->scope!=RA_SCOPE_PUBLIC&&req->scope!=RA_SCOPE_PRIVATE)||
    (req->present&~RA_PRESENT_ALL)!=0u) return;
 if(req->present!=RA_PRESENT_ALL){out->status=RA_MISSING;return;}
 if(req->previous_sequence==0xffffffffu||
    req->sequence!=req->previous_sequence+1u){out->status=RA_STALE;return;}
 if(!req->watchdog_a||!req->watchdog_b||!req->watchdog_limit||
    req->watchdog_a>req->watchdog_limit||
    req->watchdog_b>req->watchdog_limit){out->status=RA_WATCHDOG;return;}
 if(!req->ttl||req->elapsed>=req->ttl){out->status=RA_TTL;return;}
 count=req->count;
 if(count==0u){out->status=RA_MISSING;return;}
 for(i=0u;i<count;i++){
  const ra_atlas_record *p=&req->records[i];
  ra_u32 bit=1u<<i,bad=0u,duplicate=0u;
  if(!p->source_key||!p->revision||!p->target_key||
     p->kind<RA_KIND_DOCUMENT||p->kind>RA_KIND_OBSERVATION||
     p->relation<RA_REL_DIRECT||p->relation>RA_REL_INTEGRATIVE||
     p->visibility<RA_SCOPE_PUBLIC||p->visibility>RA_SCOPE_PRIVATE||
     p->gap_type>RA_GAP_UNIDENTIFIABLE||
     (p->attestation&~RA_ATTEST_ALL)!=0u||
     p->attestation!=RA_ATTEST_ALL||p->visibility>req->scope) bad=1u;
  /* Both copies of any conflicting/duplicate source key are held: no first-win. */
  for(j=0u;j<count;j++){
   if(i!=j&&p->source_key!=0u&&p->source_key==req->records[j].source_key)
    duplicate=1u;
  }
  if(duplicate){dup|=bit;bad=1u;}
  if(p->gap_type!=RA_GAP_NONE){gaps|=bit;bad=1u;}
  if(bad){held|=bit;held_count++;}else{acc|=bit;accepted_count++;}
  /* Bound metadata checksum to accepted result and normalized type (not source IDs).
   * CRC is a nonsecret accidental-change detector, not source authenticity. */
  k=(bad?0x484f4c44u:0x504c414eu)^p->kind^((p->relation&255u)<<8)^
    ((p->visibility&255u)<<16)^((p->gap_type&255u)<<24);
  for(j=0u;j<4u;j++){
   ra_u32 b=(k>>(8u*j))&255u,m;
   crc^=b;
   for(m=0u;m<8u;m++)crc=(crc>>1u)^(0x82f63b78u&(0u-(crc&1u)));
  }
 }
 out->index_mask=acc;out->held_mask=held;out->duplicates_mask=dup;
 out->gap_mask=gaps;out->accepted_count=accepted_count;
 out->held_count=held_count;out->plan_crc32c=~crc;
 out->status=held_count==0u?RA_PLAN_ONLY:(accepted_count?RA_PARTIAL:RA_HOLD);
 /* NEVER emit actual Drive writes, public publication or scientific approval. */
}
