/* RAFAELIA L0: bounded freestanding ZIP32/APK structural probe.
 * Not an APK signature/DEX/payload authenticator. No libc, I/O, heap.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
_Static_assert(sizeof(u8)==1 && sizeof(u16)==2 && sizeof(u32)==4,"8/16/32-bit target");
enum {RA_OK_STRUCTURAL=0,RA_TRUNCATED=1,RA_NOT_ZIP=2,RA_UNSUPPORTED=3,
      RA_DIRECTORY=4,RA_ENTRY=5,RA_NO_MANIFEST=6,RA_UNSAFE_PATH=7,RA_TOO_MANY=8,RA_AMBIGUOUS_CRITICAL=9};
typedef struct {u32 status, entries, manifest_present, dex_present;} ra_apk_result;
static u16 r16(const u8 *p){return (u16)((u32)p[0]|((u32)p[1]<<8));}
static u32 r32(const u8 *p){return (u32)p[0]|((u32)p[1]<<8)|((u32)p[2]<<16)|((u32)p[3]<<24);}
static int span(u32 end,u32 at,u32 n){return at<=end && n<=end-at;}
static int eq(const u8 *a,const char *s,u32 n){
 u32 i;for(i=0;i<n;i++)if(a[i]!=(u8)s[i])return 0;return s[n]=='\0';
}
static int path_ok(const u8 *p,u32 n){
 u32 i;if(!n||p[0]=='/'||p[0]=='\\')return 0;
 for(i=0;i<n;i++){
  if(p[i]==0||p[i]=='\\'||p[i]==':')return 0;
  if((i==0||p[i-1]=='/')&&i+1<n&&p[i]=='.'&&p[i+1]=='.'&&
     (i+2==n||p[i+2]=='/'))return 0;
 }return 1;
}
static ra_apk_result out(u32 s,u32 n,u32 m,u32 d){ra_apk_result r={s,n,m,d};return r;}
ra_apk_result ra_apk_probe(const u8 *b,u32 len){
 u32 e,lower,cd,cdsize,off,count,i,m=0,d=0;
 if(!b||len<22)return out(RA_TRUNCATED,0,0,0);
 e=len-22;lower=e>65535u?e-65535u:0;
 while(r32(b+e)!=0x06054b50u||r16(b+e+20)!=len-e-22u){
  if(e==lower)return out(RA_NOT_ZIP,0,0,0);e--;
 }
 if(r16(b+e+4)||r16(b+e+6)||r16(b+e+8)!=r16(b+e+10))
  return out(RA_UNSUPPORTED,0,0,0);
 count=r16(b+e+10);cdsize=r32(b+e+12);cd=r32(b+e+16);
 if(!count||count==0xffffu||cdsize==0xffffffffu||cd==0xffffffffu)
  return out(RA_UNSUPPORTED,0,0,0);
 if(count>8192u)return out(RA_TOO_MANY,0,0,0);
 if(!span(e,cd,cdsize)||cdsize!=e-cd)return out(RA_DIRECTORY,0,0,0);
 off=cd;
 for(i=0;i<count;i++){
  u32 n,ex,com,rec,loc,ln,le,packed,j;u16 flags,method;const u8 *p,*q;
  if(!span(e,off,46))return out(RA_DIRECTORY,i,m,d);
  p=b+off;if(r32(p)!=0x02014b50u)return out(RA_DIRECTORY,i,m,d);
  flags=r16(p+8);method=r16(p+10);
  if((flags&0x41u)||(method!=0&&method!=8)||r16(p+34)||
     r32(p+42)==0xffffffffu||r32(p+20)==0xffffffffu||r32(p+24)==0xffffffffu)
   return out(RA_UNSUPPORTED,i,m,d);
  n=r16(p+28);ex=r16(p+30);com=r16(p+32);rec=46u+n+ex+com;
  if(!span(e,off,rec))return out(RA_DIRECTORY,i,m,d);
  q=p+46;if(!path_ok(q,n))return out(RA_UNSAFE_PATH,i,m,d);
  loc=r32(p+42);
  if(!span(cd,loc,30))return out(RA_ENTRY,i,m,d);
  if(r32(b+loc)!=0x04034b50u||r16(b+loc+6)!=flags||
     r16(b+loc+8)!=method)return out(RA_ENTRY,i,m,d);
  ln=r16(b+loc+26);le=r16(b+loc+28);packed=r32(p+20);
  if(ln!=n||!span(cd,loc,30u+n+le)||!span(cd,loc+30u+n+le,packed))
   return out(RA_ENTRY,i,m,d);
  for(j=0;j<n;j++)if(b[loc+30+j]!=q[j])return out(RA_ENTRY,i,m,d);
  /* A ZIP may contain repeated names; Android critical entry ambiguity is unsafe.
   * Reject a second central-directory declaration for these exact root names.
   * This is not a signature, CRC, alias or decompression check. */
  if(n==19u&&eq(q,"AndroidManifest.xml",n)){
   if(m)return out(RA_AMBIGUOUS_CRITICAL,i,m,d);
   m=1;
  }
  if(n==11u&&eq(q,"classes.dex",n)){
   if(d)return out(RA_AMBIGUOUS_CRITICAL,i,m,d);
   d=1;
  }
  off+=rec;
 }
 if(off!=e)return out(RA_DIRECTORY,count,m,d);
 return m?out(RA_OK_STRUCTURAL,count,m,d):out(RA_NO_MANIFEST,count,m,d);
}
