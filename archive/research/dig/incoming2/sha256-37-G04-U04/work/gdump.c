// own code (U04): enumerate G by the definition (E4 over 2^29), dump (a0,c7) sorted by c7 ; validate vs published counts
#include "common.h"
#define B(w,i) (((w)>>(i))&1u)
typedef struct{u32 c7,a0;}P;
static int cmp(const void*a,const void*b){const P*x=a,*y=b; if(x->c7!=y->c7) return x->c7<y->c7?-1:1; return x->a0<y->a0?-1:(x->a0>y->a0);}
int main(){
  load_chi("../../../../tools/traillab/chi/chi37.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E6=EE(&X,6),E7=EE(&X,7),E8=EE(&X,8);
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8], c7c=E7-2*A3+S0(A2)-S1(E6)-K[7];
  u32 dW8=Y.W[8]-X.W[8]; P*g=malloc(sizeof(P)*13000000); u64 n=0;
  for(u32 E4=0;E4<(1u<<29);E4++){u32 w8=W8C-E4,w8y=w8+dW8;
    if(!wordok(2,8,w8,w8y)) continue;
    // printed two-bit conditions on W8 from the definition (bit 29 =1; w1!=w12; w8!=w25; w14==w18)
    if(!(B(w8,1)!=B(w8,12)&&B(w8,8)!=B(w8,25)&&B(w8,14)==B(w8,18)&&B(w8,29))) continue;
    u32 a0=E4-C4; g[n].a0=a0; g[n].c7=c7c+MAJ(A2,A1,a0)-CH(E6,E5,E4); n++; }
  qsort(g,n,sizeof(P),cmp);
  FILE*f=fopen("gset.bin","wb"); fwrite(g,sizeof(P),n,f); fclose(f);
  u64 ncl=0,big=0,bigv=0; FILE*h=fopen("classes.txt","w");
  for(u64 i=0;i<n;){u64 j=i;while(j<n&&g[j].c7==g[i].c7)j++; u64 s=j-i; ncl++; if(s>=3456){big++;bigv+=s;} fprintf(h,"%08x %llu\n",g[i].c7,(unsigned long long)s); i=j;}
  fclose(h);
  printf("published a0 %08x in G? ",AA(&X,0)); { u32 a0=AA(&X,0); int in=0; for(u64 i=0;i<n;i++) if(g[i].a0==a0){in=1;break;} printf("%d\n",in);}
  printf("|G|=%llu classes=%llu big(>=3456)=%llu variants=%llu  c7const(derived)=%08x\n",(unsigned long long)n,(unsigned long long)ncl,(unsigned long long)big,(unsigned long long)bigv,c7c);
  return 0;}
