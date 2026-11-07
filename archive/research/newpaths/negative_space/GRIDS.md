# GRIDS: tried and untried combinations

Built by build.py from records.csv (224 records: alive 46, dead 130, n/a 31, open 17). Grids use the 2-round records with status alive, dead or open
(tools, concerns and the 1-round track are left out). Cell text: `A a/n` tried-alive (a alive of n), `D n` tried-dead,
`o n` untried but n ideas logged (never run), `.` untried, `X` impossible or provably no gain (reason under the grid).
Record ids per cell: cells.csv. Axis codes: AXES.md. In the layer grid most `.` cells come from methods coded `all`
(no single layer); GAPS.md ranks only the untried cells that have a mechanism.

Marks per grid: basextech impossible 6; basextech tried-alive 9; basextech tried-dead 26; basextech untried 4; freextech impossible 28; freextech tried-alive 10; freextech tried-dead 29; freextech untried 5; layerxtech impossible 4; layerxtech tried-alive 9; layerxtech tried-dead 36; layerxtech untried 5

## Grid: free x tech

| free \ tech | trail | gd | join | sym | class | canc | alg | heur | cost |
|---|---|---|---|---|---|---|---|---|---|
| **msg** | D 8 | A 3/26 | D 12 | D 10 | A 1/2 | D 6 | D 7 | D 7 | o 1 |
| **len** | D 2 | X | X | X | X | A 9/17 | X | X | X |
| **ctr** | D 1 | A 3/9 | D 1 | X | D 3 | D 4 | D 1 | . | X |
| **flag** | D 1 | X | X | X | X | D 4 | X | X | X |
| **cv** | . | D 2 | D 2 | X | D 1 | A 1/3 | X | . | X |
| **const** | D 2 | D 1 | D 1 | D 1 | A 10/18 | D 2 | A 1/1 | D 1 | X |
| **mem** | X | D 1 | D 1 | X | X | X | . | X | A 1/2 |
| **none** | D 1 | X | X | D 1 | A 5/9 | X | D 2 | D 1 | A 9/13 |

X reasons:
- len x gd, len x join, len x class, len x alg, len x heur, flag x gd, flag x join, flag x class, flag x alg, flag x heur: few legal values fixed by message size or node position: a pair difference only, not a per-trial unknown.
- len x sym, ctr x sym, flag x sym, cv x sym, mem x sym: row 2 is IV0..IV3 in every compression; no metadata or CV choice makes the state symmetric (C5, S12).
- len x cost, ctr x cost, flag x cost, cv x cost, const x cost: cost levers add no freedom (see row none).
- mem x trail, mem x canc, mem x class, mem x heur: tables cut cost per trial, never the number of trials (R21, C15).
- none x trail, none x gd, none x join, none x sym, none x canc, none x alg, none x heur: no freedom added: measurement, convention or cost only.
- cv x alg: a solved CV word is a 32-bit preimage of the previous block (X5).

## Grid: base x tech

| base \ tech | trail | gd | join | sym | class | canc | alg | heur | cost |
|---|---|---|---|---|---|---|---|---|---|
| **fh** | D 4 | A 3/12 | D 8 | D 1 | A 12/21 | A 9/20 | D 4 | D 4 | A 9/16 |
| **ctr** | D 1 | A 3/8 | D 1 | X | A 4/8 | X | A 1/2 | . | A 1/1 |
| **mode** | D 2 | D 1 | D 1 | X | D 1 | A 1/13 | . | . | . |
| **fam** | X | D 17 | D 4 | D 1 | D 2 | D 1 | D 3 | D 3 | X |
| **gen** | D 8 | D 1 | D 3 | D 10 | D 1 | D 2 | D 2 | D 2 | X |

X reasons:
- fam x trail: the family method has no input difference to propagate.
- ctr x sym, mode x sym, fh x sym: row 2 is IV0..IV3 in every compression; no metadata or CV choice makes the state symmetric (C5, S12).
- ctr x canc: both messages share t: no extra difference to cancel (METHOD_NOTE M4).
- fam x cost: cost saves at most log2(430) = 8.7 bits; best family form is 144 (I4).
- gen x cost: cost saves at most 8.7 bits; best generic form is 144 (T8).

## Grid: layer x tech

| layer \ tech | trail | gd | join | sym | class | canc | alg | heur | cost |
|---|---|---|---|---|---|---|---|---|---|
| **r0** | D 1 | A 3/6 | X | D 1 | D 2 | A 9/19 | X | X | D 1 |
| **r1c** | D 4 | D 1 | D 1 | . | A 4/8 | D 5 | A 1/2 | D 1 | o 1 |
| **r1d** | D 2 | A 3/19 | D 8 | D 1 | A 12/20 | D 2 | D 4 | D 1 | A 1/1 |
| **fold** | D 1 | D 2 | D 1 | D 1 | D 1 | D 1 | D 1 | D 1 | D 1 |
| **mode** | D 2 | D 3 | D 2 | X | D 1 | A 1/8 | . | . | . |
| **all** | D 5 | D 8 | D 5 | D 9 | D 1 | D 1 | D 4 | D 6 | A 9/13 |

X reasons:
- mode x sym: row 2 is IV0..IV3 in every compression; no metadata or CV choice makes the state symmetric (C5, S12).
- r0 x trail, r0 x join, r0 x alg, r0 x heur: round 0 is solved exactly by its cheap inverse (C4, T3): nothing there to search.
