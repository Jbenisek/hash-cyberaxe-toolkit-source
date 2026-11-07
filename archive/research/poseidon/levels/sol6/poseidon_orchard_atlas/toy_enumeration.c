#include <stdint.h>
#include <stdio.h>
#include <time.h>
#define Q 257
static const int RC[64][3]={{28,87,165},{143,190,79},{73,116,7},{9,181,124},{22,237,246},{243,176,207},{79,178,92},{192,169,182},{158,21,211},{131,27,168},{53,200,226},{123,166,173},{176,87,193},{162,123,6},{181,33,131},{102,93,147},{117,200,7},{236,137,144},{115,141,107},{232,58,193},{44,252,154},{148,209,187},{216,44,83},{229,250,227},{4,239,79},{222,63,248},{8,125,249},{199,177,176},{102,34,53},{75,223,101},{47,128,131},{92,9,58},{100,133,248},{222,57,184},{26,56,151},{52,29,50},{223,162,172},{16,33,31},{226,196,84},{45,45,48},{113,66,20},{130,150,47},{148,136,102},{130,244,10},{75,118,91},{211,59,91},{164,217,40},{91,39,123},{120,243,157},{47,113,37},{191,10,125},{190,42,199},{213,14,200},{58,159,79},{213,181,48},{2,31,128},{176,220,254},{44,131,245},{181,172,81},{175,33,238},{87,174,56},{227,198,99},{202,81,84},{129,175,150}};
static const int M[3][3]={{103,43,147},{43,147,225},{147,225,200}};
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
}