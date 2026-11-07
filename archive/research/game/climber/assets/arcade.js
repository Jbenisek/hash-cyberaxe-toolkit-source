/* Round Climber — an arcade over a real SHA-256 reduced-round schedule check. The row is the step count; the
   player's choice is which message words carry a difference.

   The verdict math is the XOR-linear model of SHA-256's message schedule: for row n, is there a NONZERO difference
   on the chosen message words that keeps every expanded word
   W16..W(n-1) the player left "off" at zero? "Freedom" is the GF(2) kernel dimension. Passing is NECESSARY for a
   real differential path, never a proof — the signed characteristic + solver is the team's job. The instrument runs
   five controls at load (two settled shapes must stop where the research says; a recorded rank must match); a failed
   control turns climbing off. This is reduced-round research (37–40 of 64 steps) studied openly; a pass is far from
   a collision. Everything the game shows about progress lives in localStorage, so a find is never lost on a reclimb. */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var MIN_N = 17, MAX_N = 42, FRONTIER = 40, LAST_ACTIVE = 31;
  // where a found square goes; the hosted build swaps this for a public line (tools/build_site.js)
  var SEND_HINT = "paste it at the end of the team's queue file (public evidence index)";
  var KNOWN = {
    paper38: { name: "the paper's 38-step shape", words: [7, 8, 9, 10, 11, 15], allowed: [16, 23, 25], reach: 38 },
    board39: { name: "the board's accepted 39-step shape", words: [8, 9, 10, 11, 12], allowed: [16, 17, 24, 26], reach: 39 },
  };

  /* ---------------- the schedule and the image of every message bit ---------------- */
  var rotr = function (x, n) { return ((x >>> n) | (x << (32 - n))) >>> 0; };
  var s0 = function (x) { return (rotr(x, 7) ^ rotr(x, 18) ^ (x >>> 3)) >>> 0; };
  var s1 = function (x) { return (rotr(x, 17) ^ rotr(x, 19) ^ (x >>> 10)) >>> 0; };
  var IMG = [];
  for (var w = 0; w < 16; w++) {
    IMG.push([]);
    for (var b = 0; b < 32; b++) {
      var W = []; for (var j = 0; j < 16; j++) W.push(j === w ? (1 << b) >>> 0 : 0);
      for (var i = 16; i < MAX_N; i++) W.push((s1(W[i - 2]) ^ W[i - 7] ^ s0(W[i - 15]) ^ W[i - 16]) >>> 0);
      IMG[w].push(W.slice(16));
    }
  }
  function freedom(words, allowed, n) {
    var cons = [];
    for (var t = 16; t < n; t++) if (allowed.indexOf(t) < 0) cons.push(t - 16);
    var L = cons.length, basis = {}, rank = 0, unknowns = words.length * 32;
    for (var wi = 0; wi < words.length; wi++) for (var bi = 0; bi < 32; bi++) {
      var img = IMG[words[wi]][bi], v = new Uint32Array(L);
      for (var k = 0; k < L; k++) v[k] = img[cons[k]];
      for (;;) {
        var top = -1;
        for (var k2 = L - 1; k2 >= 0; k2--) if (v[k2]) { top = k2 * 32 + (31 - Math.clz32(v[k2])); break; }
        if (top < 0) break;
        var bv = basis[top];
        if (!bv) { basis[top] = v; rank++; break; }
        for (var k3 = 0; k3 < L; k3++) v[k3] ^= bv[k3];
      }
    }
    return unknowns - rank;
  }

  /* ---------------- instrument controls ---------------- */
  var CONTROLS = [
    ["board 39-step shape holds at 39", freedom(KNOWN.board39.words, KNOWN.board39.allowed, 39) > 0],
    ["board 39-step shape fails at 40", freedom(KNOWN.board39.words, KNOWN.board39.allowed, 40) === 0],
    ["paper 38-step shape holds at 38", freedom(KNOWN.paper38.words, KNOWN.paper38.allowed, 38) > 0],
    ["paper 38-step shape fails at 39", freedom(KNOWN.paper38.words, KNOWN.paper38.allowed, 39) === 0],
    ["words 8–12 with W24, W26, W39–W42 forced zero has no freedom", (function () { var a = []; for (var t = 16; t < 43; t++) if ([24, 26, 39, 40, 41, 42].indexOf(t) < 0) a.push(t); return freedom([8, 9, 10, 11, 12], a, MAX_N) === 0; })()],
  ];
  var controlsOk = CONTROLS.every(function (c) { return c[1]; });
  var controlsText = controlsOk ? CONTROLS.length + "/" + CONTROLS.length + " controls pass" : "CONTROLS FAILED";
  $$("[data-controls-status]").forEach(function (el) { el.textContent = controlsText; });
  var foot = $("[data-controls-foot]"); if (foot) foot.textContent = controlsOk ? "Instrument verified: " + CONTROLS.length + "/" + CONTROLS.length + " controls pass." : "Instrument failed its controls; climbing is disabled.";
  var sdot = $("[data-sensor-dot]"); if (sdot) sdot.className = "hud__dot" + (controlsOk ? " is-ok" : " is-bad");
  var snote = $("[data-sensor-note]"); if (snote) snote.innerHTML = CONTROLS.map(function (c) { return (c[1] ? "✓ " : "✗ ") + c[0]; }).join("<br>");

  /* ---------------- persistence ---------------- */
  var KEY = "climber.v2";
  var DEF = { best: null, climbs: 0, finds: [], scores: [], badges: {}, sends: 0, settings: { motion: true, anim: true, scan: false } };
  var DB = load();
  function load() { try { var o = JSON.parse(localStorage.getItem(KEY)); if (o && o.settings) return Object.assign({}, DEF, o); } catch (e) {} return JSON.parse(JSON.stringify(DEF)); }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(DB)); } catch (e) { /* private window: memory only */ } }

  /* ---------------- achievements ---------------- */
  var BADGES = [
    { id: "liftoff", name: "Lift-off", desc: "Complete your first climb", t: function (c) { return DB.climbs >= 1; } },
    { id: "r25", name: "Quarter tower", desc: "Reach row 25", t: function (c) { return c.h >= 25; } },
    { id: "r31", name: "Two-block", desc: "Reach row 31", t: function (c) { return c.h >= 31; } },
    { id: "r38", name: "Paper ceiling", desc: "Reach row 38", t: function (c) { return c.h >= 38; } },
    { id: "r39", name: "Board ceiling", desc: "Reach row 39", t: function (c) { return c.h >= 39; } },
    { id: "frontier", name: "Frontier", desc: "Reach row 40, the edge", t: function (c) { return c.h >= FRONTIER; } },
    { id: "scholar", name: "Scholar", desc: "Rediscover the paper 38-step shape", t: function (c) { return c.knownKey === "paper38"; } },
    { id: "historian", name: "Historian", desc: "Rediscover the board 39-step shape", t: function (c) { return c.knownKey === "board39"; } },
    { id: "grind10", name: "Persistent", desc: "10 climbs", t: function (c) { return DB.climbs >= 10; } },
    { id: "grind50", name: "Relentless", desc: "50 climbs", t: function (c) { return DB.climbs >= 50; } },
    { id: "cart5", name: "Cartographer", desc: "Log 5 finds", t: function (c) { return DB.finds.length >= 5; } },
    { id: "courier", name: "Courier", desc: "Send a square to the team", t: function (c) { return DB.sends >= 1; } },
  ];
  // every badge a climb earns is announced in ONE toast (a first climb to 39 earns six at once; six popups buried
  // the record panel and, on a phone, the controls — seen in the e2e screenshots)
  function checkBadges(ctx) {
    var got = [];
    BADGES.forEach(function (b) {
      if (DB.badges[b.id]) return;
      if (b.t(ctx)) { DB.badges[b.id] = Date.now(); got.push(b); }
    });
    if (got.length === 1) toast("🏅 Badge unlocked", got[0].name + " — " + got[0].desc);
    else if (got.length > 1) toast("🏅 " + got.length + " badges unlocked", got.map(function (b) { return b.name; }).join(" · "));
  }

  /* ---------------- game state ---------------- */
  var st = { words: [], allowed: [], top: MIN_N - 1, pass: {}, failAt: null };
  var key = function (ws, al) { return ws.slice().sort(num).join(".") + "|" + al.slice().sort(num).join("."); };
  function num(a, b) { return a - b; }
  function sameSet(a, b) { return a.length === b.length && a.slice().sort(num).join() === b.slice().sort(num).join(); }
  function knownKeyFor(ws, al, h) { for (var k in KNOWN) if (KNOWN[k].reach === h && sameSet(ws, KNOWN[k].words) && sameSet(al, KNOWN[k].allowed)) return k; return null; }

  /* ---------------- build the board ---------------- */
  (function buildWords() {
    var h = ""; for (var i = 0; i < 16; i++) h += '<button type="button" class="tile" data-word="' + i + '" aria-pressed="false" title="message word W' + i + '">W' + i + "</button>";
    $("[data-words]").innerHTML = h;
  })();
  (function buildLadder() {
    var h = "";
    for (var n = MIN_N; n <= MAX_N; n++) {
      var t = n - 1, late = t > LAST_ACTIVE;
      h += '<div class="lrow row--locked' + (n === FRONTIER ? " row--frontier" : "") + '" data-row="' + n + '">' +
        '<span class="n">' + n + "</span>" +
        '<button type="button" class="tile tile--a" data-active="' + t + '" aria-pressed="false"' + (late ? ' disabled title="W' + t + ' is past the point a difference can be cancelled before the frontier"' : ' title="let W' + t + ' stay active; off demands it be zero"') + ">W" + t + "</button>" +
        '<span class="bar"><i data-bar="' + n + '"></i></span>' +
        '<span class="res" data-res="' + n + '"></span></div>';
    }
    $("[data-ladder]").innerHTML = h;
  })();

  function syncTiles() {
    $$("[data-word]").forEach(function (b) { b.setAttribute("aria-pressed", String(st.words.indexOf(+b.dataset.word) >= 0)); });
    $$("[data-active]").forEach(function (b) { b.setAttribute("aria-pressed", String(st.allowed.indexOf(+b.dataset.active) >= 0)); });
  }
  function renderLadder() {
    var ladder = $("[data-ladder]");
    for (var n = MIN_N; n <= MAX_N; n++) {
      var row = ladder.querySelector('[data-row="' + n + '"]'), bar = ladder.querySelector('[data-bar="' + n + '"]'), res = ladder.querySelector('[data-res="' + n + '"]');
      row.classList.remove("row--locked", "row--next", "row--pass", "row--fail", "row--known");
      if (st.pass[n]) { row.classList.add("row--pass"); var fr = st.pass[n]; bar.style.width = Math.max(8, Math.min(100, fr * 1.6)) + "%"; res.textContent = fr + " free"; }
      else if (st.failAt === n) { row.classList.add("row--fail"); bar.style.width = "100%"; res.textContent = "blocked"; }
      else { bar.style.width = "0"; res.textContent = ""; if (n === st.top + 1 && st.failAt == null) row.classList.add("row--next"); else if (n > st.top) row.classList.add("row--locked"); }
      if (knownKeyFor(st.words, st.allowed, n)) row.classList.add("row--known");
    }
    $("[data-height]").textContent = st.top >= MIN_N ? "row " + st.top : "—";
    $("[data-objective]").textContent = st.words.length + "w · " + st.allowed.length + "a";
    $("[data-freedom]").textContent = st.pass[st.top] != null ? st.pass[st.top] + " bits" : "—";
    $("[data-best]").textContent = DB.best ? "row " + DB.best.h : "—";
    var sb = $("[data-start-best]"); if (sb) sb.innerHTML = DB.best ? "best climb <b>row " + DB.best.h + "</b> · " + DB.finds.length + " finds · " + Object.keys(DB.badges).length + "/" + BADGES.length + " badges" : "no climbs yet";
  }
  function message(text, cls) { var m = $("[data-msg]"); m.textContent = text; m.className = "ticker" + (cls ? " is-" + cls : ""); }

  /* ---------------- climb ---------------- */
  function climb(oneRow) {
    clearSend();
    if (!controlsOk) { message("The instrument failed its controls, so climbing is off.", "fail"); return; }
    if (!st.words.length) { message("Pick at least one message word first.", ""); return; }
    var n = st.top + 1;
    for (; n <= MAX_N; n++) {
      var fr = freedom(st.words, st.allowed, n);
      if (fr > 0) { st.pass[n] = fr; st.top = n; if (oneRow) break; }
      else { st.failAt = n; break; }
    }
    renderLadder();
    if (st.failAt != null || !oneRow || st.top === MAX_N) finishRun();
    else report(false);
  }
  function finishRun() {
    DB.climbs++;
    var h = st.top, knownKey = knownKeyFor(st.words, st.allowed, h);
    var isFind = h >= 38 && !knownKey;              // reached a high row by a route not already known
    var isFrontier = h >= FRONTIER;
    // personal best
    var newBest = !DB.best || h > DB.best.h;
    if (newBest && h >= MIN_N) { DB.best = { h: h, words: st.words.slice(), allowed: st.allowed.slice() }; toast("⬆ New best", "Row " + h); }
    // scores: best height per unique shape
    if (h >= 20) recordScore(h);
    // finds: saved forever, never lost on a reclimb
    if (isFind || isFrontier) saveFind(h, isFrontier ? "frontier" : "new");
    checkBadges({ h: h, knownKey: knownKey });
    save();
    renderLadder();   // the BEST gauge and start-screen line read DB.best, which was only just saved
    renderLog();
    report(true);
  }
  function recordScore(h) {
    var k = key(st.words, st.allowed);
    var e = DB.scores.filter(function (s) { return s.k === k; })[0];
    if (e) { if (h > e.h) { e.h = h; e.t = Date.now(); } }
    else DB.scores.push({ k: k, h: h, words: st.words.slice(), allowed: st.allowed.slice(), t: Date.now() });
    DB.scores.sort(function (a, b) { return b.h - a.h || b.t - a.t; });
    if (DB.scores.length > 20) DB.scores.length = 20;
  }
  function saveFind(h, verdict) {
    var k = key(st.words, st.allowed) + "|" + h;
    if (DB.finds.some(function (f) { return f.k === k; })) { toast("✔ Already in your finds", "Row " + h + " kept."); return; }
    DB.finds.unshift({ k: k, h: h, verdict: verdict, words: st.words.slice(), allowed: st.allowed.slice(), t: Date.now() });
    if (DB.finds.length > 60) DB.finds.length = 60;
    toast(verdict === "frontier" ? "⭐ FRONTIER FIND saved" : "✦ Find saved", "Row " + h + " · in your Finds forever");
  }
  function report(done) {
    var h = st.top, knownKey = knownKeyFor(st.words, st.allowed, h);
    if (st.failAt && h < MIN_N) { message("Stuck at the bottom: this support can't even reach row " + MIN_N + ".", "fail"); return; }
    if (h >= FRONTIER) { message("Row " + h + " passes, and the frontier is " + FRONTIER + ". No one has a real path here — this is worth the team's full test.", "frontier"); offerSend(h, "reached the frontier at row " + h); return; }
    if (knownKey) { message("Row " + h + ": this is " + KNOWN[knownKey].name + ", a route the team already knows. It stops here for a real reason, not a bug.", "win"); return; }
    if (st.failAt) {
      if (h >= 38) { message("Climbed to row " + h + " by a shape not in the known set, then row " + st.failAt + " blocked it. Saved to your Finds — send it for the real test.", "frontier"); offerSend(h, "reached row " + h + " with a shape not in the known set"); }
      else message("Climbed to row " + h + ", then row " + st.failAt + " demanded a word be zero that your difference forces nonzero. That's the wall for this shape. Change the support and climb again.", "fail");
      return;
    }
    message("Row " + h + " passes. Keep climbing.", "win");
  }

  /* ---------------- send a square to the team ---------------- */
  function offerSend(h, why) {
    var now = new Date();
    var stamp = now.getFullYear() + "-" + ("0" + (now.getMonth() + 1)).slice(-2) + "-" + ("0" + now.getDate()).slice(-2) + " " + ("0" + now.getHours()).slice(-2) + ":" + ("0" + now.getMinutes()).slice(-2);
    var opts = "words:" + st.words.join(".") + "|active:" + st.allowed.join(".");
    var reqId = "Qtry" + djb("TRY|sha256|" + h + "|" + opts);
    var line = [stamp, reqId, "TRY", "sha256-r" + h, opts, why + "; schedule-check pass only, needs the signed/solver test"].join("\t");
    var slot = $("[data-send-slot]");
    slot.innerHTML = '<div class="sendbox"><p>Send this square for the team\'s real test:</p><button type="button" class="chip" data-copy>Copy the result</button> <span class="muted">' + SEND_HINT + '</span><textarea class="out" readonly>' + line + "</textarea></div>";
  }
  function clearSend() { var slot = $("[data-send-slot]"); if (slot) slot.innerHTML = ""; }
  function djb(s) { var h = 5381; for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0; var t = h.toString(36); while (t.length < 7) t = "0" + t; return t; }

  /* ---------------- the log drawer ---------------- */
  var tab = "finds";
  function renderLog() {
    var box = $("[data-tabpanel]"); if (!box) return;
    var fmt = function (t) { var d = new Date(t); return (d.getMonth() + 1) + "/" + d.getDate() + " " + ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2); };
    if (tab === "finds") {
      box.innerHTML = DB.finds.length ? DB.finds.map(function (f) {
        return '<button type="button" class="rec" data-load="' + f.k + '"><span class="rec__badge ' + (f.verdict === "frontier" ? "is-front" : "is-find") + '">' + (f.verdict === "frontier" ? "FRONTIER" : "ROW " + f.h) + '</span><span class="rec__shape">W' + f.words.join(" W") + '</span><span class="rec__t">' + fmt(f.t) + '</span></button>';
      }).join("") : '<p class="empty">No finds yet. Reach row 38+ by a new route, or the frontier, and it is saved here forever.</p>';
    } else if (tab === "scores") {
      box.innerHTML = DB.scores.length ? '<ol class="scores">' + DB.scores.map(function (s, i) {
        return '<li class="rec" data-load="' + key(s.words, s.allowed) + '"><span class="rec__rank">' + (i + 1) + '</span><span class="rec__h">row ' + s.h + '</span><span class="rec__shape">W' + s.words.join(" W") + '</span></li>';
      }).join("") + "</ol>" : '<p class="empty">Climb to row 20 or higher and your best shapes rank here.</p>';
    } else {
      box.innerHTML = '<div class="badges">' + BADGES.map(function (b) {
        var got = DB.badges[b.id];
        return '<div class="badge' + (got ? " is-got" : "") + '"><span class="badge__i">' + (got ? "🏅" : "🔒") + '</span><span class="badge__n">' + b.name + '</span><span class="badge__d">' + b.desc + '</span></div>';
      }).join("") + "</div>";
    }
  }
  function loadShape(k) {
    var all = DB.finds.concat(DB.scores);
    var e = all.filter(function (x) { return (x.k === k) || (key(x.words, x.allowed) === k); })[0];
    if (!e) return;
    st.words = e.words.slice(); st.allowed = e.allowed.slice(); resetClimb(); syncTiles();
    message("Loaded a saved shape. Press CLIMB to run it again.", "");
  }

  /* ---------------- presets, reset ---------------- */
  function resetClimb() { st.top = MIN_N - 1; st.pass = {}; st.failAt = null; clearSend(); renderLadder(); }
  function applyPreset(p) {
    if (p === "clear") { st.words = []; st.allowed = []; }
    else if (p === "random") { st.words = []; st.allowed = []; var c = 3 + Math.floor(Math.random() * 4); while (st.words.length < c) { var x = 6 + Math.floor(Math.random() * 8); if (st.words.indexOf(x) < 0) st.words.push(x); } st.words.sort(num); }
    else if (KNOWN[p]) { st.words = KNOWN[p].words.slice(); st.allowed = KNOWN[p].allowed.slice(); }
    syncTiles(); resetClimb(); message(p === "clear" ? "Cleared." : "Shape set. Press CLIMB.", "");
  }

  /* ---------------- screens & overlays ---------------- */
  function setScreen(name) {
    document.body.setAttribute("data-screen", name === "game" ? "game" : "start");
    $$('[data-view]').forEach(function (v) { v.hidden = v.getAttribute("data-view") !== (name === "game" ? "game" : "start"); });
    if (name === "game") { renderLadder(); renderLog(); }
  }
  function openSheet(which) {
    var ov = $("[data-overlay]"); ov.hidden = false;
    $$('[data-sheet]').forEach(function (s) { s.hidden = s.getAttribute("data-sheet") !== which; });
  }
  function closeSheet() { $("[data-overlay]").hidden = true; }

  /* ---------------- settings ---------------- */
  function applySettings() {
    document.body.classList.toggle("no-motion", !DB.settings.motion);
    document.body.classList.toggle("no-anim", !DB.settings.anim);
    document.body.classList.toggle("scanlines", !!DB.settings.scan);
    $$("[data-opt]").forEach(function (c) { c.checked = !!DB.settings[c.dataset.opt]; });
  }

  /* ---------------- toasts ---------------- */
  function toast(title, body) {
    var box = $("[data-toasts]"); if (!box) return;
    while (box.children.length >= 3) box.removeChild(box.firstChild);   // never more than three on screen
    var el = document.createElement("div"); el.className = "toast";
    el.innerHTML = "<b>" + title + "</b><span>" + body + "</span>";
    box.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("in"); });
    setTimeout(function () { el.classList.remove("in"); setTimeout(function () { el.remove(); }, 400); }, 3400);
  }

  /* ---------------- events ---------------- */
  document.addEventListener("click", function (e) {
    var g = e.target.closest("[data-go]"); if (g) { var dest = g.dataset.go; if (dest === "help" || dest === "settings") openSheet(dest); else setScreen(dest); return; }
    if (e.target.closest("[data-close]")) { closeSheet(); return; }
    if (e.target.closest("[data-overlay]") && e.target.matches("[data-overlay]")) { closeSheet(); return; }
    var wb = e.target.closest("[data-word]"); if (wb) { var wv = +wb.dataset.word, i = st.words.indexOf(wv); if (i >= 0) st.words.splice(i, 1); else st.words.push(wv); st.words.sort(num); syncTiles(); resetClimb(); return; }
    var ab = e.target.closest("[data-active]"); if (ab && !ab.disabled) { var av = +ab.dataset.active, j = st.allowed.indexOf(av); if (j >= 0) st.allowed.splice(j, 1); else st.allowed.push(av); st.allowed.sort(num); syncTiles(); resetClimb(); return; }
    var pb = e.target.closest("[data-preset]"); if (pb) { applyPreset(pb.dataset.preset); return; }
    if (e.target.closest("[data-climb]")) { climb(false); return; }
    if (e.target.closest("[data-step]")) { climb(true); return; }
    if (e.target.closest("[data-reset]")) { resetClimb(); message("Back at the bottom.", ""); return; }
    var tabBtn = e.target.closest("[data-tab]"); if (tabBtn) { tab = tabBtn.dataset.tab; $$("[data-tab]").forEach(function (b) { b.classList.toggle("is-active", b === tabBtn); }); renderLog(); return; }
    var rec = e.target.closest("[data-load]"); if (rec) { loadShape(rec.dataset.load); return; }
    if (e.target.closest("[data-copy]")) {
      var ta = $(".sendbox .out"), btn = e.target.closest("[data-copy]");
      if (ta) {
        ta.focus(); ta.select();   // selected either way, so the player can copy by hand if the clipboard is refused
        var done = function (ok) { btn.textContent = ok ? "Copied" : "Selected — press Ctrl+C"; };
        try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(ta.value).then(function () { done(true); }, function () { done(false); }); else done(false); } catch (x) { done(false); }
        DB.sends++; save(); checkBadges({ h: st.top });
      }
      return;
    }
    // erase asks twice on the page itself (hosted pages refuse confirm() popups)
    var wipe = e.target.closest("[data-wipe]");
    if (wipe) {
      if (wipe.dataset.armed !== "1") {
        wipe.dataset.armed = "1"; wipe.textContent = "Tap again to erase everything"; wipe.classList.add("chip--danger");
        setTimeout(function () { if (wipe.dataset.armed === "1") { wipe.dataset.armed = ""; wipe.textContent = "Erase finds, scores & badges"; wipe.classList.remove("chip--danger"); } }, 4000);
        return;
      }
      wipe.dataset.armed = ""; wipe.textContent = "Erase finds, scores & badges"; wipe.classList.remove("chip--danger");
      DB = JSON.parse(JSON.stringify(DEF)); save(); applySettings(); renderLadder(); renderLog(); toast("Record erased", "Starting fresh.");
      return;
    }
  });
  document.addEventListener("change", function (e) {
    var o = e.target.closest("[data-opt]"); if (o) { DB.settings[o.dataset.opt] = o.checked; save(); applySettings(); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSheet();
    if (document.body.getAttribute("data-screen") !== "game") return;
    if (e.key === "Enter") { e.preventDefault(); climb(false); }
    else if (e.key === " ") { e.preventDefault(); climb(true); }
  });

  /* ---------------- boot ---------------- */
  applySettings();
  syncTiles();
  renderLadder();
  renderLog();
  if (!controlsOk) $$("[data-climb],[data-step]").forEach(function (b) { b.disabled = true; });
})();
