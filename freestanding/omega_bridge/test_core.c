#include "omega_core.h"
int main(void){
 int32_t a[]={65536,131072,-65536};int32_t b[]={0,65536,-65536};
 uint32_t w[]={65536,65536,65536};uint64_t out=99;
 if(omega_residual_q16(a,b,w,3,&out)!=OMEGA_OK||out!=UINT64_C(8589934592))return 1;
 if(omega_residual_q16(a,b,w,0,&out)!=OMEGA_EMPTY||out!=0)return 2;
 if(omega_residual_q16(0,b,w,3,&out)!=OMEGA_RANGE)return 3;
 a[0]=INT32_MAX;b[0]=INT32_MIN;w[0]=UINT32_MAX;
 if(omega_residual_q16(a,b,w,3,&out)!=OMEGA_OVERFLOW)return 4;
 return 0;
}
