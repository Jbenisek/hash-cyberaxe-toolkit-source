#!/bin/bash
cd "$(dirname "$0")"
rm -f res.txt
echo "S 0 flats look $(../flats s0.txt 10 look | grep RESULT)" >> res.txt
echo "S 0 flats look1 $(../flats s0.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 0 flats plain $(../flats s0.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s0.txt 10 0 1 look > bf3_0_look.out
../../audit/bf3 s0.txt 10 0 1 none > bf3_0_none.out
echo "S 1 flats look $(../flats s1.txt 6 look | grep RESULT)" >> res.txt
echo "S 1 flats look1 $(../flats s1.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 1 flats plain $(../flats s1.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s1.txt 6 0 1 look > bf3_1_look.out
../../audit/bf3 s1.txt 6 0 1 none > bf3_1_none.out
echo "S 2 flats look $(../flats s2.txt 13 look | grep RESULT)" >> res.txt
echo "S 2 flats look1 $(../flats s2.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 2 flats plain $(../flats s2.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s2.txt 13 0 1 look > bf3_2_look.out
../../audit/bf3 s2.txt 13 0 1 none > bf3_2_none.out
echo "S 3 flats look $(../flats s3.txt 10 look | grep RESULT)" >> res.txt
echo "S 3 flats look1 $(../flats s3.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 3 flats plain $(../flats s3.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s3.txt 10 0 1 look > bf3_3_look.out
../../audit/bf3 s3.txt 10 0 1 none > bf3_3_none.out
echo "S 4 flats look $(../flats s4.txt 11 look | grep RESULT)" >> res.txt
echo "S 4 flats look1 $(../flats s4.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 4 flats plain $(../flats s4.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s4.txt 11 0 1 look > bf3_4_look.out
../../audit/bf3 s4.txt 11 0 1 none > bf3_4_none.out
echo "S 5 flats look $(../flats s5.txt 12 look | grep RESULT)" >> res.txt
echo "S 5 flats look1 $(../flats s5.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 5 flats plain $(../flats s5.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s5.txt 12 0 1 look > bf3_5_look.out
../../audit/bf3 s5.txt 12 0 1 none > bf3_5_none.out
echo "S 6 flats look $(../flats s6.txt 6 look | grep RESULT)" >> res.txt
echo "S 6 flats look1 $(../flats s6.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 6 flats plain $(../flats s6.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s6.txt 6 0 1 look > bf3_6_look.out
../../audit/bf3 s6.txt 6 0 1 none > bf3_6_none.out
echo "S 7 flats look $(../flats s7.txt 11 look | grep RESULT)" >> res.txt
echo "S 7 flats look1 $(../flats s7.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 7 flats plain $(../flats s7.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s7.txt 11 0 1 look > bf3_7_look.out
../../audit/bf3 s7.txt 11 0 1 none > bf3_7_none.out
echo "S 8 flats look $(../flats s8.txt 7 look | grep RESULT)" >> res.txt
echo "S 8 flats look1 $(../flats s8.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 8 flats plain $(../flats s8.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s8.txt 7 0 1 look > bf3_8_look.out
../../audit/bf3 s8.txt 7 0 1 none > bf3_8_none.out
echo "S 9 flats look $(../flats s9.txt 7 look | grep RESULT)" >> res.txt
echo "S 9 flats look1 $(../flats s9.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 9 flats plain $(../flats s9.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s9.txt 7 0 1 look > bf3_9_look.out
../../audit/bf3 s9.txt 7 0 1 none > bf3_9_none.out
echo "S 10 flats look $(../flats s10.txt 8 look | grep RESULT)" >> res.txt
echo "S 10 flats look1 $(../flats s10.txt 8 look1 | grep RESULT)" >> res.txt
echo "S 10 flats plain $(../flats s10.txt 8 plain | grep RESULT)" >> res.txt
../../audit/bf3 s10.txt 8 0 1 look > bf3_10_look.out
../../audit/bf3 s10.txt 8 0 1 none > bf3_10_none.out
echo "S 11 flats look $(../flats s11.txt 14 look | grep RESULT)" >> res.txt
echo "S 11 flats look1 $(../flats s11.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 11 flats plain $(../flats s11.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s11.txt 14 0 1 look > bf3_11_look.out
../../audit/bf3 s11.txt 14 0 1 none > bf3_11_none.out
echo "S 12 flats look $(../flats s12.txt 13 look | grep RESULT)" >> res.txt
echo "S 12 flats look1 $(../flats s12.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 12 flats plain $(../flats s12.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s12.txt 13 0 1 look > bf3_12_look.out
../../audit/bf3 s12.txt 13 0 1 none > bf3_12_none.out
echo "S 13 flats look $(../flats s13.txt 12 look | grep RESULT)" >> res.txt
echo "S 13 flats look1 $(../flats s13.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 13 flats plain $(../flats s13.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s13.txt 12 0 1 look > bf3_13_look.out
../../audit/bf3 s13.txt 12 0 1 none > bf3_13_none.out
echo "S 14 flats look $(../flats s14.txt 7 look | grep RESULT)" >> res.txt
echo "S 14 flats look1 $(../flats s14.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 14 flats plain $(../flats s14.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s14.txt 7 0 1 look > bf3_14_look.out
../../audit/bf3 s14.txt 7 0 1 none > bf3_14_none.out
echo "S 15 flats look $(../flats s15.txt 9 look | grep RESULT)" >> res.txt
echo "S 15 flats look1 $(../flats s15.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 15 flats plain $(../flats s15.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s15.txt 9 0 1 look > bf3_15_look.out
../../audit/bf3 s15.txt 9 0 1 none > bf3_15_none.out
echo "S 16 flats look $(../flats s16.txt 12 look | grep RESULT)" >> res.txt
echo "S 16 flats look1 $(../flats s16.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 16 flats plain $(../flats s16.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s16.txt 12 0 1 look > bf3_16_look.out
../../audit/bf3 s16.txt 12 0 1 none > bf3_16_none.out
echo "S 17 flats look $(../flats s17.txt 9 look | grep RESULT)" >> res.txt
echo "S 17 flats look1 $(../flats s17.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 17 flats plain $(../flats s17.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s17.txt 9 0 1 look > bf3_17_look.out
../../audit/bf3 s17.txt 9 0 1 none > bf3_17_none.out
echo "S 18 flats look $(../flats s18.txt 7 look | grep RESULT)" >> res.txt
echo "S 18 flats look1 $(../flats s18.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 18 flats plain $(../flats s18.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s18.txt 7 0 1 look > bf3_18_look.out
../../audit/bf3 s18.txt 7 0 1 none > bf3_18_none.out
echo "S 19 flats look $(../flats s19.txt 12 look | grep RESULT)" >> res.txt
echo "S 19 flats look1 $(../flats s19.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 19 flats plain $(../flats s19.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s19.txt 12 0 1 look > bf3_19_look.out
../../audit/bf3 s19.txt 12 0 1 none > bf3_19_none.out
echo "S 20 flats look $(../flats s20.txt 8 look | grep RESULT)" >> res.txt
echo "S 20 flats look1 $(../flats s20.txt 8 look1 | grep RESULT)" >> res.txt
echo "S 20 flats plain $(../flats s20.txt 8 plain | grep RESULT)" >> res.txt
../../audit/bf3 s20.txt 8 0 1 look > bf3_20_look.out
../../audit/bf3 s20.txt 8 0 1 none > bf3_20_none.out
echo "S 21 flats look $(../flats s21.txt 10 look | grep RESULT)" >> res.txt
echo "S 21 flats look1 $(../flats s21.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 21 flats plain $(../flats s21.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s21.txt 10 0 1 look > bf3_21_look.out
../../audit/bf3 s21.txt 10 0 1 none > bf3_21_none.out
echo "S 22 flats look $(../flats s22.txt 14 look | grep RESULT)" >> res.txt
echo "S 22 flats look1 $(../flats s22.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 22 flats plain $(../flats s22.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s22.txt 14 0 1 look > bf3_22_look.out
../../audit/bf3 s22.txt 14 0 1 none > bf3_22_none.out
echo "S 23 flats look $(../flats s23.txt 14 look | grep RESULT)" >> res.txt
echo "S 23 flats look1 $(../flats s23.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 23 flats plain $(../flats s23.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s23.txt 14 0 1 look > bf3_23_look.out
../../audit/bf3 s23.txt 14 0 1 none > bf3_23_none.out
echo "S 24 flats look $(../flats s24.txt 12 look | grep RESULT)" >> res.txt
echo "S 24 flats look1 $(../flats s24.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 24 flats plain $(../flats s24.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s24.txt 12 0 1 look > bf3_24_look.out
../../audit/bf3 s24.txt 12 0 1 none > bf3_24_none.out
echo "S 25 flats look $(../flats s25.txt 13 look | grep RESULT)" >> res.txt
echo "S 25 flats look1 $(../flats s25.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 25 flats plain $(../flats s25.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s25.txt 13 0 1 look > bf3_25_look.out
../../audit/bf3 s25.txt 13 0 1 none > bf3_25_none.out
echo "S 26 flats look $(../flats s26.txt 7 look | grep RESULT)" >> res.txt
echo "S 26 flats look1 $(../flats s26.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 26 flats plain $(../flats s26.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s26.txt 7 0 1 look > bf3_26_look.out
../../audit/bf3 s26.txt 7 0 1 none > bf3_26_none.out
echo "S 27 flats look $(../flats s27.txt 6 look | grep RESULT)" >> res.txt
echo "S 27 flats look1 $(../flats s27.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 27 flats plain $(../flats s27.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s27.txt 6 0 1 look > bf3_27_look.out
../../audit/bf3 s27.txt 6 0 1 none > bf3_27_none.out
echo "S 28 flats look $(../flats s28.txt 11 look | grep RESULT)" >> res.txt
echo "S 28 flats look1 $(../flats s28.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 28 flats plain $(../flats s28.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s28.txt 11 0 1 look > bf3_28_look.out
../../audit/bf3 s28.txt 11 0 1 none > bf3_28_none.out
echo "S 29 flats look $(../flats s29.txt 11 look | grep RESULT)" >> res.txt
echo "S 29 flats look1 $(../flats s29.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 29 flats plain $(../flats s29.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s29.txt 11 0 1 look > bf3_29_look.out
../../audit/bf3 s29.txt 11 0 1 none > bf3_29_none.out
echo "S 30 flats look $(../flats s30.txt 7 look | grep RESULT)" >> res.txt
echo "S 30 flats look1 $(../flats s30.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 30 flats plain $(../flats s30.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s30.txt 7 0 1 look > bf3_30_look.out
../../audit/bf3 s30.txt 7 0 1 none > bf3_30_none.out
echo "S 31 flats look $(../flats s31.txt 14 look | grep RESULT)" >> res.txt
echo "S 31 flats look1 $(../flats s31.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 31 flats plain $(../flats s31.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s31.txt 14 0 1 look > bf3_31_look.out
../../audit/bf3 s31.txt 14 0 1 none > bf3_31_none.out
echo "S 32 flats look $(../flats s32.txt 12 look | grep RESULT)" >> res.txt
echo "S 32 flats look1 $(../flats s32.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 32 flats plain $(../flats s32.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s32.txt 12 0 1 look > bf3_32_look.out
../../audit/bf3 s32.txt 12 0 1 none > bf3_32_none.out
echo "S 33 flats look $(../flats s33.txt 10 look | grep RESULT)" >> res.txt
echo "S 33 flats look1 $(../flats s33.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 33 flats plain $(../flats s33.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s33.txt 10 0 1 look > bf3_33_look.out
../../audit/bf3 s33.txt 10 0 1 none > bf3_33_none.out
echo "S 34 flats look $(../flats s34.txt 10 look | grep RESULT)" >> res.txt
echo "S 34 flats look1 $(../flats s34.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 34 flats plain $(../flats s34.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s34.txt 10 0 1 look > bf3_34_look.out
../../audit/bf3 s34.txt 10 0 1 none > bf3_34_none.out
echo "S 35 flats look $(../flats s35.txt 6 look | grep RESULT)" >> res.txt
echo "S 35 flats look1 $(../flats s35.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 35 flats plain $(../flats s35.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s35.txt 6 0 1 look > bf3_35_look.out
../../audit/bf3 s35.txt 6 0 1 none > bf3_35_none.out
echo "S 36 flats look $(../flats s36.txt 11 look | grep RESULT)" >> res.txt
echo "S 36 flats look1 $(../flats s36.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 36 flats plain $(../flats s36.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s36.txt 11 0 1 look > bf3_36_look.out
../../audit/bf3 s36.txt 11 0 1 none > bf3_36_none.out
echo "S 37 flats look $(../flats s37.txt 13 look | grep RESULT)" >> res.txt
echo "S 37 flats look1 $(../flats s37.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 37 flats plain $(../flats s37.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s37.txt 13 0 1 look > bf3_37_look.out
../../audit/bf3 s37.txt 13 0 1 none > bf3_37_none.out
echo "S 38 flats look $(../flats s38.txt 14 look | grep RESULT)" >> res.txt
echo "S 38 flats look1 $(../flats s38.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 38 flats plain $(../flats s38.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s38.txt 14 0 1 look > bf3_38_look.out
../../audit/bf3 s38.txt 14 0 1 none > bf3_38_none.out
echo "S 39 flats look $(../flats s39.txt 12 look | grep RESULT)" >> res.txt
echo "S 39 flats look1 $(../flats s39.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 39 flats plain $(../flats s39.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s39.txt 12 0 1 look > bf3_39_look.out
../../audit/bf3 s39.txt 12 0 1 none > bf3_39_none.out
echo "S 40 flats look $(../flats s40.txt 11 look | grep RESULT)" >> res.txt
echo "S 40 flats look1 $(../flats s40.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 40 flats plain $(../flats s40.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s40.txt 11 0 1 look > bf3_40_look.out
../../audit/bf3 s40.txt 11 0 1 none > bf3_40_none.out
echo "S 41 flats look $(../flats s41.txt 7 look | grep RESULT)" >> res.txt
echo "S 41 flats look1 $(../flats s41.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 41 flats plain $(../flats s41.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s41.txt 7 0 1 look > bf3_41_look.out
../../audit/bf3 s41.txt 7 0 1 none > bf3_41_none.out
echo "S 42 flats look $(../flats s42.txt 10 look | grep RESULT)" >> res.txt
echo "S 42 flats look1 $(../flats s42.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 42 flats plain $(../flats s42.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s42.txt 10 0 1 look > bf3_42_look.out
../../audit/bf3 s42.txt 10 0 1 none > bf3_42_none.out
echo "S 43 flats look $(../flats s43.txt 11 look | grep RESULT)" >> res.txt
echo "S 43 flats look1 $(../flats s43.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 43 flats plain $(../flats s43.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s43.txt 11 0 1 look > bf3_43_look.out
../../audit/bf3 s43.txt 11 0 1 none > bf3_43_none.out
echo "S 44 flats look $(../flats s44.txt 7 look | grep RESULT)" >> res.txt
echo "S 44 flats look1 $(../flats s44.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 44 flats plain $(../flats s44.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s44.txt 7 0 1 look > bf3_44_look.out
../../audit/bf3 s44.txt 7 0 1 none > bf3_44_none.out
echo "S 45 flats look $(../flats s45.txt 11 look | grep RESULT)" >> res.txt
echo "S 45 flats look1 $(../flats s45.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 45 flats plain $(../flats s45.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s45.txt 11 0 1 look > bf3_45_look.out
../../audit/bf3 s45.txt 11 0 1 none > bf3_45_none.out
echo "S 46 flats look $(../flats s46.txt 7 look | grep RESULT)" >> res.txt
echo "S 46 flats look1 $(../flats s46.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 46 flats plain $(../flats s46.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s46.txt 7 0 1 look > bf3_46_look.out
../../audit/bf3 s46.txt 7 0 1 none > bf3_46_none.out
echo "S 47 flats look $(../flats s47.txt 14 look | grep RESULT)" >> res.txt
echo "S 47 flats look1 $(../flats s47.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 47 flats plain $(../flats s47.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s47.txt 14 0 1 look > bf3_47_look.out
../../audit/bf3 s47.txt 14 0 1 none > bf3_47_none.out
echo "S 48 flats look $(../flats s48.txt 9 look | grep RESULT)" >> res.txt
echo "S 48 flats look1 $(../flats s48.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 48 flats plain $(../flats s48.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s48.txt 9 0 1 look > bf3_48_look.out
../../audit/bf3 s48.txt 9 0 1 none > bf3_48_none.out
echo "S 49 flats look $(../flats s49.txt 9 look | grep RESULT)" >> res.txt
echo "S 49 flats look1 $(../flats s49.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 49 flats plain $(../flats s49.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s49.txt 9 0 1 look > bf3_49_look.out
../../audit/bf3 s49.txt 9 0 1 none > bf3_49_none.out
echo "S 50 flats look $(../flats s50.txt 11 look | grep RESULT)" >> res.txt
echo "S 50 flats look1 $(../flats s50.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 50 flats plain $(../flats s50.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s50.txt 11 0 1 look > bf3_50_look.out
../../audit/bf3 s50.txt 11 0 1 none > bf3_50_none.out
echo "S 51 flats look $(../flats s51.txt 9 look | grep RESULT)" >> res.txt
echo "S 51 flats look1 $(../flats s51.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 51 flats plain $(../flats s51.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s51.txt 9 0 1 look > bf3_51_look.out
../../audit/bf3 s51.txt 9 0 1 none > bf3_51_none.out
echo "S 52 flats look $(../flats s52.txt 13 look | grep RESULT)" >> res.txt
echo "S 52 flats look1 $(../flats s52.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 52 flats plain $(../flats s52.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s52.txt 13 0 1 look > bf3_52_look.out
../../audit/bf3 s52.txt 13 0 1 none > bf3_52_none.out
echo "S 53 flats look $(../flats s53.txt 6 look | grep RESULT)" >> res.txt
echo "S 53 flats look1 $(../flats s53.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 53 flats plain $(../flats s53.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s53.txt 6 0 1 look > bf3_53_look.out
../../audit/bf3 s53.txt 6 0 1 none > bf3_53_none.out
echo "S 54 flats look $(../flats s54.txt 7 look | grep RESULT)" >> res.txt
echo "S 54 flats look1 $(../flats s54.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 54 flats plain $(../flats s54.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s54.txt 7 0 1 look > bf3_54_look.out
../../audit/bf3 s54.txt 7 0 1 none > bf3_54_none.out
echo "S 55 flats look $(../flats s55.txt 11 look | grep RESULT)" >> res.txt
echo "S 55 flats look1 $(../flats s55.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 55 flats plain $(../flats s55.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s55.txt 11 0 1 look > bf3_55_look.out
../../audit/bf3 s55.txt 11 0 1 none > bf3_55_none.out
echo "S 56 flats look $(../flats s56.txt 14 look | grep RESULT)" >> res.txt
echo "S 56 flats look1 $(../flats s56.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 56 flats plain $(../flats s56.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s56.txt 14 0 1 look > bf3_56_look.out
../../audit/bf3 s56.txt 14 0 1 none > bf3_56_none.out
echo "S 57 flats look $(../flats s57.txt 7 look | grep RESULT)" >> res.txt
echo "S 57 flats look1 $(../flats s57.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 57 flats plain $(../flats s57.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s57.txt 7 0 1 look > bf3_57_look.out
../../audit/bf3 s57.txt 7 0 1 none > bf3_57_none.out
echo "S 58 flats look $(../flats s58.txt 8 look | grep RESULT)" >> res.txt
echo "S 58 flats look1 $(../flats s58.txt 8 look1 | grep RESULT)" >> res.txt
echo "S 58 flats plain $(../flats s58.txt 8 plain | grep RESULT)" >> res.txt
../../audit/bf3 s58.txt 8 0 1 look > bf3_58_look.out
../../audit/bf3 s58.txt 8 0 1 none > bf3_58_none.out
echo "S 59 flats look $(../flats s59.txt 7 look | grep RESULT)" >> res.txt
echo "S 59 flats look1 $(../flats s59.txt 7 look1 | grep RESULT)" >> res.txt
echo "S 59 flats plain $(../flats s59.txt 7 plain | grep RESULT)" >> res.txt
../../audit/bf3 s59.txt 7 0 1 look > bf3_59_look.out
../../audit/bf3 s59.txt 7 0 1 none > bf3_59_none.out
echo "S 60 flats look $(../flats s60.txt 14 look | grep RESULT)" >> res.txt
echo "S 60 flats look1 $(../flats s60.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 60 flats plain $(../flats s60.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s60.txt 14 0 1 look > bf3_60_look.out
../../audit/bf3 s60.txt 14 0 1 none > bf3_60_none.out
echo "S 61 flats look $(../flats s61.txt 14 look | grep RESULT)" >> res.txt
echo "S 61 flats look1 $(../flats s61.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 61 flats plain $(../flats s61.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s61.txt 14 0 1 look > bf3_61_look.out
../../audit/bf3 s61.txt 14 0 1 none > bf3_61_none.out
echo "S 62 flats look $(../flats s62.txt 9 look | grep RESULT)" >> res.txt
echo "S 62 flats look1 $(../flats s62.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 62 flats plain $(../flats s62.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s62.txt 9 0 1 look > bf3_62_look.out
../../audit/bf3 s62.txt 9 0 1 none > bf3_62_none.out
echo "S 63 flats look $(../flats s63.txt 6 look | grep RESULT)" >> res.txt
echo "S 63 flats look1 $(../flats s63.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 63 flats plain $(../flats s63.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s63.txt 6 0 1 look > bf3_63_look.out
../../audit/bf3 s63.txt 6 0 1 none > bf3_63_none.out
echo "S 64 flats look $(../flats s64.txt 9 look | grep RESULT)" >> res.txt
echo "S 64 flats look1 $(../flats s64.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 64 flats plain $(../flats s64.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s64.txt 9 0 1 look > bf3_64_look.out
../../audit/bf3 s64.txt 9 0 1 none > bf3_64_none.out
echo "S 65 flats look $(../flats s65.txt 10 look | grep RESULT)" >> res.txt
echo "S 65 flats look1 $(../flats s65.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 65 flats plain $(../flats s65.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s65.txt 10 0 1 look > bf3_65_look.out
../../audit/bf3 s65.txt 10 0 1 none > bf3_65_none.out
echo "S 66 flats look $(../flats s66.txt 6 look | grep RESULT)" >> res.txt
echo "S 66 flats look1 $(../flats s66.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 66 flats plain $(../flats s66.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s66.txt 6 0 1 look > bf3_66_look.out
../../audit/bf3 s66.txt 6 0 1 none > bf3_66_none.out
echo "S 67 flats look $(../flats s67.txt 10 look | grep RESULT)" >> res.txt
echo "S 67 flats look1 $(../flats s67.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 67 flats plain $(../flats s67.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s67.txt 10 0 1 look > bf3_67_look.out
../../audit/bf3 s67.txt 10 0 1 none > bf3_67_none.out
echo "S 68 flats look $(../flats s68.txt 6 look | grep RESULT)" >> res.txt
echo "S 68 flats look1 $(../flats s68.txt 6 look1 | grep RESULT)" >> res.txt
echo "S 68 flats plain $(../flats s68.txt 6 plain | grep RESULT)" >> res.txt
../../audit/bf3 s68.txt 6 0 1 look > bf3_68_look.out
../../audit/bf3 s68.txt 6 0 1 none > bf3_68_none.out
echo "S 69 flats look $(../flats s69.txt 13 look | grep RESULT)" >> res.txt
echo "S 69 flats look1 $(../flats s69.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 69 flats plain $(../flats s69.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s69.txt 13 0 1 look > bf3_69_look.out
../../audit/bf3 s69.txt 13 0 1 none > bf3_69_none.out
echo "S 70 flats look $(../flats s70.txt 10 look | grep RESULT)" >> res.txt
echo "S 70 flats look1 $(../flats s70.txt 10 look1 | grep RESULT)" >> res.txt
echo "S 70 flats plain $(../flats s70.txt 10 plain | grep RESULT)" >> res.txt
../../audit/bf3 s70.txt 10 0 1 look > bf3_70_look.out
../../audit/bf3 s70.txt 10 0 1 none > bf3_70_none.out
echo "S 71 flats look $(../flats s71.txt 11 look | grep RESULT)" >> res.txt
echo "S 71 flats look1 $(../flats s71.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 71 flats plain $(../flats s71.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s71.txt 11 0 1 look > bf3_71_look.out
../../audit/bf3 s71.txt 11 0 1 none > bf3_71_none.out
echo "S 72 flats look $(../flats s72.txt 9 look | grep RESULT)" >> res.txt
echo "S 72 flats look1 $(../flats s72.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 72 flats plain $(../flats s72.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s72.txt 9 0 1 look > bf3_72_look.out
../../audit/bf3 s72.txt 9 0 1 none > bf3_72_none.out
echo "S 73 flats look $(../flats s73.txt 14 look | grep RESULT)" >> res.txt
echo "S 73 flats look1 $(../flats s73.txt 14 look1 | grep RESULT)" >> res.txt
echo "S 73 flats plain $(../flats s73.txt 14 plain | grep RESULT)" >> res.txt
../../audit/bf3 s73.txt 14 0 1 look > bf3_73_look.out
../../audit/bf3 s73.txt 14 0 1 none > bf3_73_none.out
echo "S 74 flats look $(../flats s74.txt 13 look | grep RESULT)" >> res.txt
echo "S 74 flats look1 $(../flats s74.txt 13 look1 | grep RESULT)" >> res.txt
echo "S 74 flats plain $(../flats s74.txt 13 plain | grep RESULT)" >> res.txt
../../audit/bf3 s74.txt 13 0 1 look > bf3_74_look.out
../../audit/bf3 s74.txt 13 0 1 none > bf3_74_none.out
echo "S 75 flats look $(../flats s75.txt 12 look | grep RESULT)" >> res.txt
echo "S 75 flats look1 $(../flats s75.txt 12 look1 | grep RESULT)" >> res.txt
echo "S 75 flats plain $(../flats s75.txt 12 plain | grep RESULT)" >> res.txt
../../audit/bf3 s75.txt 12 0 1 look > bf3_75_look.out
../../audit/bf3 s75.txt 12 0 1 none > bf3_75_none.out
echo "S 76 flats look $(../flats s76.txt 11 look | grep RESULT)" >> res.txt
echo "S 76 flats look1 $(../flats s76.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 76 flats plain $(../flats s76.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s76.txt 11 0 1 look > bf3_76_look.out
../../audit/bf3 s76.txt 11 0 1 none > bf3_76_none.out
echo "S 77 flats look $(../flats s77.txt 9 look | grep RESULT)" >> res.txt
echo "S 77 flats look1 $(../flats s77.txt 9 look1 | grep RESULT)" >> res.txt
echo "S 77 flats plain $(../flats s77.txt 9 plain | grep RESULT)" >> res.txt
../../audit/bf3 s77.txt 9 0 1 look > bf3_77_look.out
../../audit/bf3 s77.txt 9 0 1 none > bf3_77_none.out
echo "S 78 flats look $(../flats s78.txt 11 look | grep RESULT)" >> res.txt
echo "S 78 flats look1 $(../flats s78.txt 11 look1 | grep RESULT)" >> res.txt
echo "S 78 flats plain $(../flats s78.txt 11 plain | grep RESULT)" >> res.txt
../../audit/bf3 s78.txt 11 0 1 look > bf3_78_look.out
../../audit/bf3 s78.txt 11 0 1 none > bf3_78_none.out
echo "S 79 flats look $(../flats s79.txt 5 look | grep RESULT)" >> res.txt
echo "S 79 flats look1 $(../flats s79.txt 5 look1 | grep RESULT)" >> res.txt
echo "S 79 flats plain $(../flats s79.txt 5 plain | grep RESULT)" >> res.txt
../../audit/bf3 s79.txt 5 0 1 look > bf3_79_look.out
../../audit/bf3 s79.txt 5 0 1 none > bf3_79_none.out
