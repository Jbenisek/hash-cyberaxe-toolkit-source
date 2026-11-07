# Round Climber: game design brief

For: Claude Design. Build the complete game UI (every screen, control, state and layout below) as HTML, CSS and
JavaScript that calls the engine described in section 14. You design and build the interface. You do not write
any of the math: the engine owns every verdict, number and rule check.

Owner's direction, in their words: "fix it so an expert would enjoy using it", "a normal game layout", it must
work "on a 720p screen or mobile", and it is meant to be shown to experts.

---

## 1. What the game is

Round Climber is an arcade puzzle built on a real research question about reduced-round SHA-256. The player picks
which of SHA-256's 16 message words carry a difference, then climbs a tower of rows. Each row is one more step of
SHA-256's message schedule. A row passes when the player's difference can still keep every expanded word they
demanded be zero at zero. The climb stops at the first row that fails. That row is the wall.

The research frontier is row 40. Two routes are already known from published research: one stops at row 38, one at
row 39. Nobody has a light route past 39. A light shape that passes row 40 is a genuine open question, and the game
sends it to the research team for their real test.

Two audiences use the same screen:

- **Casual players** press presets, Random, and Climb. They need the climb to feel good and the result to be clear.
- **Experts** (cryptographers) build shapes word by word and want the numbers: freedom in bits, rank, which word
  blocked the climb, and a concrete difference that survives. They will judge the game in two minutes on whether
  its claims are true and whether it shows its working.

## 2. Non-negotiables

1. **Hosted locally only.** The game runs from a local server on the owner's machine. It is never published to the
   internet. Do not add analytics, share-to-web features, or calls to any server except Google Fonts.
2. **Every claim on screen is true.** The check is a necessary condition for a real route, never proof of one. No
   copy may say or imply that a pass is a real result, a discovery or a break. Section 12 gives the exact strings.
3. **Weight counts.** A shape's weight is the number of words carrying a difference. Heavy shapes pass rows easily
   and mean nothing. Only light shapes earn the frontier, the finds log, and "send to the team". See section 5.
4. **No private research material in the UI.** No research file names, folder paths, team member names, or
   internal codes. The two known routes may be named "the paper's 38-step route" and "the board's 39-step route".
5. **Vocabulary.** Use "route", "shape", "difference", "check", "row", "wall", "frontier". Never "attack",
   "exploit", "break", "crack" or "collision attack".
6. **One page app.** One HTML entry, no build step, no framework required. Libraries only if they do substantial
   work, loaded from a pinned CDN version.

## 3. Glossary for the designer

| Term | Meaning | Shown as |
|---|---|---|
| Message word | W0 to W15, the 16 words of the input block | 16 toggle tiles |
| Expanded word | W16 and up, computed from the message words by the schedule | one per tower row |
| Row n | a path of n steps; row n introduces expanded word W(n-1) | tower rung, 17 at the base, 42 at the top |
| Shape | the set of message words with a difference, plus the expanded words marked active | the current build |
| Active word | an expanded word the player lets stay nonzero; every other expanded word must be zero | toggle on its row |
| Weight | message words in the shape + active expanded words | always visible number |
| Budget | the most weight a shape may carry and still count (provisional 12) | gauge with a limit |
| Freedom | bits of difference that survive at a row; 0 means the row fails | number and bar per row |
| Wall | the first row that fails | red row |
| Height | the highest row that passes | headline score |
| Frontier | row 40 | marked line on the tower |
| Known route | a shape published research already has (38-step, 39-step) | star on its top row |
| Find | a light shape that reaches 40, or 38 or 39 by a route not already known | saved to the record |
| Witness | one concrete difference that survives at a row, in hex, verified by the engine | expert inspector |
| Blame | the expanded word that made the wall row fail | named on the wall row |

## 4. The core loop

1. Build a shape: toggle message words, optionally toggle active words on rows W16 to W31.
2. Climb: the engine checks rows 17 upward and stops at the wall. Rows light up one by one (skippable).
3. Read the result: height, weight, freedom at the top, blame at the wall, valid or heavy.
4. Adjust and climb again. Every climb is logged; finds are saved permanently.

Step mode: the player can advance one row at a time and toggle the next row's active word before it is checked.

## 5. Rules (the engine enforces these; the UI displays them)

- **Weight** = number of message words with a difference + number of active expanded words.
- **Budget** = 12, labelled "provisional" until the research team sets the figure. Settings shows it read-only.
- **Valid climb**: weight at or under budget. **Heavy climb**: weight over budget. A heavy climb still runs and
  shows its rows, but its score does not count, it earns no badges, it is never a find, and it is never offered
  to the team. The UI must make this unmistakable before and after the climb (gauge turns red over budget).
- **Active words** are allowed only on W16 to W31. Tiles for W32 and up are locked, with the reason on hover/tap.
- **Score order**: height first, then lower weight. Two shapes at row 39: the lighter one ranks higher.
- **Find**: valid, and either height 40 or more, or height 38 or 39 with a shape that is not a known route.
- **Known route recognised**: when the current shape equals a known route and stops at its known height, the top
  row gets a star and the result says so.
- **Controls gate everything**: the engine runs five self-checks at load (the known routes stop where published
  research says, and a recorded rank matches). If any fails, Climb and Step are disabled and the sensor shows red.

## 6. Screens

### 6.1 Title screen
- Game name, one-line pitch, the player's best (height and weight) and counts (finds, badges).
- Buttons: **Play**, **Tutorial**, **Record**, **Settings**.
- Sensor line: "Engine verified: 5 of 5 checks pass" or the failure.
- Background: animated, but Play is reachable and readable in the first frame.

### 6.2 Main game screen (the one that matters)
A normal game layout: a full-viewport stage that never scrolls as a page. Regions:

- **Top HUD bar**: menu button, game name, sensor light, height, weight against budget, best, record button,
  tutorial button, settings button.
- **Left panel, the Builder**: 16 message-word tiles in a 4×4 or 8×2 grid; presets (Paper 38, Board 39,
  Random light, Clear); weight gauge with the budget mark; validity badge (Valid / Heavy).
- **Centre, the Tower** (the playfield): rows 17 to 42 bottom to top, the frontier line at 40, each row showing its
  number, its expanded word tile (active toggle), a freedom bar with value, and its state. The current row is
  always in view; the tower auto-scrolls to it during a climb. The tower is the visual hero.
- **Right panel, the Inspector** (experts): for the selected row (click any row): freedom, rank, constraint count,
  pass/fail, blame word on a wall row, the witness difference as 16 hex words with a "verified" mark, and the
  schedule view (section 8).
- **Bottom action bar**: Climb, Step, Reset, Undo, Share code. Large, thumb-reachable on phones.

### 6.3 Climb result
After every climb a compact result card (not a blocking modal on desktop; a bottom sheet on phones): height,
weight, valid/heavy, top-row freedom, wall row and its blame word, plus one of the messages in section 12. Buttons:
Climb again, Inspect wall, Save shape, and (only for a valid find) Send to the team.

### 6.4 Record
Tabs: **Finds**, **Scores** (ranked: height then weight), **History** (last 100 climbs with time, shape code,
height, weight, valid/heavy), **Badges**. Every entry can be loaded back into the Builder with one click.

### 6.5 Tutorial
A three-step guided first climb on the main screen (coach marks, not a wall of text): pick words, climb, read the
wall. Plus a reference page: rules, the glossary, and the honest scope paragraph (section 12). Reopenable.

### 6.6 Settings
Motion and starfield, climb speed (instant / fast / cinematic), sound (off by default, enabled from a button),
scanlines, number format (hex groups on/off), budget (read-only, "provisional"), engine check details (the five
checks with pass marks), erase record (two-step confirm on the page; browser confirm dialogs are not allowed).

### 6.7 Pause menu
Esc or the menu button on the game screen: Resume, Tutorial, Settings, Title screen.

## 7. Every control

| Control | Where | Does | States | Key |
|---|---|---|---|---|
| Message word W0–W15 | Builder | toggles the word in the shape; resets the climb | off / on | 0–9, A–F, with Shift for W10–W15 or a picker |
| Active word tile | each tower row W16–W31 | toggles the expanded word active; resets the climb | off / on / locked (W32+) | click only |
| Preset Paper 38 / Board 39 | Builder | loads the known route | — | — |
| Random light | Builder | random shape within budget | — | R |
| Clear | Builder | empties the shape | — | Backspace |
| Climb | action bar | runs to the wall | enabled / disabled (no words, or engine checks failed) | Enter |
| Step | action bar | checks one more row | enabled / disabled | Space |
| Reset | action bar | back to the base, shape kept | — | Home |
| Undo | action bar | undo the last shape change | enabled when history exists | Ctrl+Z |
| Share code | action bar | shows the shape as a short text code, copy button; paste a code to load | — | Ctrl+S |
| Row select | tower | selects a row for the Inspector | selected | Up/Down |
| Send to the team | result card | shows the result line to copy | only for a valid find | — |
| Record, Tutorial, Settings, Menu | HUD | open their screens | — | Esc for menu |

Copy buttons must fall back to selecting the text when the clipboard is refused, and say so.

## 8. Expert features (what makes an expert enjoy it)

1. **Inspector numbers** per row: freedom (bits), rank, number of constrained bits, unknowns (32 × words).
2. **Blame**: the wall row names the expanded word whose demand to be zero made the row fail.
3. **Witness**: a concrete surviving difference at the selected row, 16 hex words, with the engine's verification
   (it re-expands the difference and confirms every demanded word is zero). Button: "Show another witness".
4. **Schedule view**: a matrix, message words across, expanded words W16–W41 down, a filled cell where that message
   word feeds that expanded word. Highlights the current shape's words and the wall word. This lets an expert see
   why a shape fails.
5. **Share codes**: a compact text code for any shape, so experts can trade shapes in chat.
6. **Sandbox toggle**: ignores the budget for exploration; everything climbed in sandbox is labelled "sandbox, does
   not count" and never scores, logs as a find, or offers sending.
7. **Compare**: pin a shape and climb another beside it; the tower shows both freedom bars per row.
8. **Keyboard-first**: every action has a key (section 7); a "?" overlay lists them.
9. **Tabular mono numerals** for every number; hex in 4-character groups.

## 9. Layout requirements

The main game screen must fit without page scrolling at each of these sizes. The tower may scroll inside its own
panel, but the current row and the action bar are always visible.

| Viewport | Layout |
|---|---|
| 1920×1080 | Builder left, Tower centre, Inspector right, action bar bottom |
| 1366×768 and 1280×720 | same three columns, compact rows; tower rows at least 22px; nothing cut off |
| 1024×768 tablet | Tower centre, Builder and Inspector as collapsible side drawers |
| 844×390 phone landscape | Tower left, Builder right, Inspector in a drawer |
| 390×844 phone portrait | tabs Build / Climb / Inspect; the action bar fixed at the bottom with safe-area insets; one column; no horizontal scroll |

Touch targets at least 44px. The phone layout keeps the tower readable: row number, freedom bar and state. The
active-word tile can move into a row tap menu on phones.

## 10. Game feel

- Climb animation: rows light one after another (cinematic about 60ms per row, fast about 15ms, instant none);
  any key or click skips to the end.
- The wall hits: a short shake and a red flash on the wall row; respects reduced motion.
- The frontier: crossing row 40 with a valid light shape gets the one big celebration in the game. A heavy pass
  gets no celebration, just the heavy notice.
- Toasts: at most three on screen; several badges from one climb announce in one toast.
- Sound: off by default; a soft tick per row, a thud at the wall, a chord at a valid frontier. Starts only after a
  user click.

## 11. Badges

| Badge | Earned by (valid climbs only) |
|---|---|
| Lift-off | first valid climb |
| Quarter tower | reach row 25 |
| Two-block | reach row 31 |
| Paper ceiling | reach row 38 |
| Board ceiling | reach row 39 |
| Frontier | reach row 40 with a valid shape |
| Scholar | rediscover the paper's 38-step route |
| Historian | rediscover the board's 39-step route |
| Featherweight | reach row 38 with weight 9 or less |
| Persistent | 10 climbs |
| Relentless | 50 climbs |
| Cartographer | 5 finds |
| Inspector | open a witness at a wall row |
| Courier | copy a find for the team |

## 12. Copy (exact strings where it matters)

- Scope paragraph (tutorial and settings): "Each row runs the XOR-linear model of SHA-256's message schedule. A pass
  means a nonzero difference on your words keeps every word you demanded zero at zero up to that step. That is
  necessary for a real route and far from proof of one: the check does not price active words, does not model the
  carries of modular addition, and does not model the compression rounds where real conditions live. The research
  team's own tests do that."
- Valid frontier: "Row {h} with weight {w}. That is a light shape past the frontier, and nobody has a real route
  here. Send it to the team for their real test."
- Heavy pass: "Row {h}, but weight {w} is over the budget of {b}. Heavy shapes climb easily and mean nothing, so
  this climb does not count."
- Known route: "Row {h}: this is {route}, a route published research already has. It stops here for a real reason."
- Wall: "Row {wall} failed: your difference forces {word} to be nonzero. That is the wall for this shape."
- Not a find: "Row {h} with weight {w}. A good climb, but below the frontier."
- Engine checks failed: "The engine failed a self-check, so climbing is off."

## 13. Persistence

Per-player, in the browser (localStorage, every read and write in try/catch; the game must work when storage is
blocked). Keys: best, finds, scores, history, badges, settings, tutorial-done. Erase is a two-step confirm on the
page.

## 14. Engine contract (the UI calls this; the engine side supplies it)

The engine is one script, `engine.js`, exposing `window.RoundEngine`. All math lives there. Status: `freedom`,
`controls` and the known routes exist today in the current build; the rest are added by the engine side to this
contract before integration.

```js
RoundEngine.MIN_ROW      // 17
RoundEngine.MAX_ROW      // 42
RoundEngine.FRONTIER     // 40
RoundEngine.LAST_ACTIVE  // 31  (highest expanded word that may be active)
RoundEngine.BUDGET       // 12, provisional
RoundEngine.KNOWN        // { paper38: {name, words, active, reach}, board39: {...} }

RoundEngine.controls()
  // -> [{ name, pass }]  five self-checks; climbing allowed only if every pass is true

RoundEngine.weight(shape)            // shape = { words:[0..15], active:[16..31] } -> integer
RoundEngine.valid(shape)             // -> { ok, weight, budget, reasons:[...] }

RoundEngine.row(shape, n)
  // -> { n, pass, freedom, rank, unknowns, constrainedBits, blame }   blame: expanded word index when it fails

RoundEngine.climb(shape, fromRow?)
  // -> { rows:[row results from fromRow up to and including the wall], height, wall, blame,
  //      weight, valid, knownRoute: key|null, find: bool }

RoundEngine.witness(shape, n, seed?)
  // -> { words:[16 hex strings], verified: bool }   one surviving difference at row n, re-checked by the engine

RoundEngine.dependencyMatrix()
  // -> boolean[26][16]   expanded word W16..W41 by message word W0..W15

RoundEngine.encodeShape(shape) -> string
RoundEngine.decodeShape(code)  -> shape | null
```

The UI never computes a verdict itself and never hardcodes a result.

## 15. Acceptance (the owner's browser test checks all of this)

- Each viewport in section 9 shows the whole main screen with no page scroll and no horizontal scroll.
- Every control in section 7 is visible, clickable, and not covered by another element.
- Paper 38 climbs to 38 and walls at 39; Board 39 climbs to 39 and walls at 40, starred as a known route.
- A shape over budget (for example all 16 message words plus W16–W31 active) is marked heavy before the climb,
  earns nothing, logs no find, and offers no sending.
- A find survives a page reload and a reclimb, and is never duplicated.
- Esc opens and closes the pause menu; Enter climbs; Space steps.
- Zero console errors on load and during every flow.
- Reduced motion turns off the shake, the starfield and the row animation.

## 16. What to deliver

`index.html`, `style.css`, `ui.js` (and art assets if any), wired to `engine.js` through the contract in section
14. A short list of any requirement you could not meet, with the reason.

## Science engine (2026-10-23, Ledger, CyberAxe order)
Read SCIENCE_ENGINE_SPEC.md: verdict ladder A-D, budget, in-browser CaDiCaL (WASM) solver, encoder port, controls, recording, candidate export.
- Known-shape check: SCIENCE_ENGINE_SPEC.md section 12 (data kit/known_scan_cands.json).
- Echo arrows / hallway / wall hint: SCIENCE_ENGINE_SPEC.md section 13.
