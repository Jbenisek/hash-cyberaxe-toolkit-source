from poseidon_core import parameters
from pathlib import Path
import subprocess,json,time
B=Path(__file__).resolve().parent;rc,m,_=parameters()
q=257
# Toy model explicitly preserves the 4+56+4 schedule, but NOT the native field.
# Reduce the native constants and use a small Cauchy MDS with every minor nonzero.
mm=[[pow(1+i+4+j,-1,q) for j in range(3)] for i in range(3)]
src=r'''#include <stdint.h>
#include <stdio.h>
#include <time.h>
#define Q 257
static const int RC[64][3]=RCVALUES;
static const int M[3][3]=MVALUES;
static int S[Q*Q][3];
static int p5(int a){int b=a*a%Q;return b*b%Q*a%Q;}
int main(void){
 for(int a=0;a<Q;a++)for(int b=0;b<Q;b++){int i=a*Q+b;S[i][0]=a;S[i][1]=b;S[i][2]=2;}
 puts("round_index,inputs,distinct_full_states,distinct_digest_values,min_bucket,max_bucket,unordered_collisions,unordered_noncollisions,unordered_pairs");
 for(int r=0;r<64;r++){
  int count[Q]={0};
  for(int i=0;i<Q*Q;i++){
   int z[3],t[3];for(int j=0;j<3;j++)z[j]=(S[i][j]+RC[r][j])%Q;
   for(int j=0;j<3;j++)if(j==0 || r<4 || r>=60)z[j]=p5(z[j]);
   for(int j=0;j<3;j++){t[j]=0;for(int k=0;k<3;k++)t[j]=(t[j]+M[j][k]*z[k])%Q;}
   for(int j=0;j<3;j++)S[i][j]=t[j];count[t[0]]++;
  }
  int distinct=0,mn=Q*Q,mx=0; uint64_t cols=0,pairs=(uint64_t)(Q*Q)*(Q*Q-1)/2;
  for(int h=0;h<Q;h++){if(count[h])distinct++;if(count[h]<mn)mn=count[h];if(count[h]>mx)mx=count[h];cols+=(uint64_t)count[h]*(count[h]-1)/2;}
  // Full-state distinctness follows independently from each bijective layer;
  // here check it literally with a bitset over all 257^3 toy states.
  static unsigned char seen[(Q*Q*Q+7)/8];
  for(unsigned i=0;i<sizeof(seen);i++)seen[i]=0;
  int ds=0;for(int i=0;i<Q*Q;i++){int k=(S[i][0]*Q+S[i][1])*Q+S[i][2];if(!(seen[k/8]&(1u<<(k%8))))ds++;seen[k/8]|=1u<<(k%8);}
  printf("%d,%d,%d,%d,%d,%d,%llu,%llu,%llu\n",r,Q*Q,ds,distinct,mn,mx,(unsigned long long)cols,(unsigned long long)(pairs-cols),(unsigned long long)pairs);
 }
 return 0;
}'''
src=src.replace('RCVALUES','{'+','.join('{'+','.join(str(x%q) for x in row)+'}' for row in rc)+'}').replace('MVALUES','{'+','.join('{'+','.join(map(str,row))+'}' for row in mm)+'}')
(B/'toy_enumeration.c').write_text(src)
start=time.perf_counter();subprocess.run(['cc','-O3','-std=c11',str(B/'toy_enumeration.c'),'-o',str(B/'toy_enumeration')],check=True)
with (B/'data/toy_full_input_counts.csv').open('w') as f:subprocess.run([str(B/'toy_enumeration')],stdout=f,check=True)
(B/'data/toy_config.json').write_text(json.dumps({'p':q,'capacity':2,'width':3,'exponent':5,'full_rounds':[0,1,2,3,60,61,62,63],'constants':'native RC reduced mod 257','MDS':mm,'native_target':False,'inputs_exhausted':q*q,'compile_and_run_wall_seconds':time.perf_counter()-start},indent=2))
