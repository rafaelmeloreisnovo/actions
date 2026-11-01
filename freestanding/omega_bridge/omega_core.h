/* Experimental cross-domain numeric primitive; no physical equivalence claimed.
   Freestanding ISO C11, no libc calls, no heap or I/O. */
#ifndef RAFAELIA_OMEGA_CORE_H
#define RAFAELIA_OMEGA_CORE_H
#include <stdint.h>
#include <stddef.h>
#define OMEGA_OK 0
#define OMEGA_EMPTY 1
#define OMEGA_RANGE 2
#define OMEGA_OVERFLOW 3
/* Q16 squared residual statistic, unsigned positive weights; overflow fails closed.
   Domain adapters must validate units, calibration and covariance separately. */
static inline int omega_residual_q16(const int32_t *observed,const int32_t *predicted,const uint32_t *weight,size_t n,uint64_t *out){
 if(!out)return OMEGA_RANGE;
 *out=0;
 if(!n)return OMEGA_EMPTY;
 if(!observed||!predicted||!weight)return OMEGA_RANGE;
 uint64_t sum=0;
 for(size_t i=0;i<n;i++){
  int64_t d=(int64_t)observed[i]-(int64_t)predicted[i];
  uint64_t a=(uint64_t)(d<0?-d:d);
  if(a>UINT64_C(3037000499))return OMEGA_OVERFLOW;
  uint64_t sq=a*a;
  if(weight[i] && sq>UINT64_MAX/(uint64_t)weight[i])return OMEGA_OVERFLOW;
  uint64_t term=(sq*(uint64_t)weight[i])>>16;
  if(sum>UINT64_MAX-term)return OMEGA_OVERFLOW;
  sum+=term;
 }
 *out=sum;return OMEGA_OK;
}
#endif
