/* Round Climber lever board, first working version (the look comes later from the design pass).
   The loop: a player stacks levers on a row; the board shows each lever's recorded number, which pairs are tested,
   and which are not; "Copy this stack" writes lines for public evidence index. tools/kb_build.js turns those lines into
   test requests (public methodology notes), the team answers in public evidence index with an evidence file, and the next build
   shows the answer here. The ids below must match kb_build.js exactly (same hash, same prefix). */
(function () {
  "use strict";
  var KB = window.KB;
  if (KB) KB.requests = KB.requests || []; // Private queue omitted from public data.
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  if (!KB) { $("[data-levers]").innerHTML = "<p>kb/knowledge.js is missing: run <code>node tools/kb_build.js</code> in this folder.</p>"; return; }
  function hid(prefix, s) { var h = 5381; for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0; var t = h.toString(36); while (t.length < 7) t = "0" + t; return prefix + t; }
  function composeId(a, b) { return hid("Q", "COMPOSE|" + [a, b].sort().join("|")); }
  var num = function (v) { return typeof v === "number" && isFinite(v) ? v.toFixed(5).replace(/0+$/, "").replace(/\.$/, "") : "—"; };
  $("[data-built]").textContent = "knowledge built " + KB.builtAt.slice(0, 16).replace("T", " ") + " UTC";

  var LIVE = /works|filed|projected|open/;
  var byRow = {};
  KB.levers.forEach(function (l) { if (l.row && l.bits != null && l.bits < 0 || l.row && l.status === "closed") (byRow[l.row] = byRow[l.row] || []).push(l); });
  var rows = Object.keys(byRow).filter(function (k) { return byRow[k].some(function (l) { return LIVE.test(l.status) && l.bits < 0; }); });
  var key = function (k) { var m = k.match(/^(.*?)-r(\d+)$/); return m ? m[1] + "-" + ("000" + m[2]).slice(-3) : k + "-zzz"; };
  rows.sort(function (a, b) { return key(a) < key(b) ? -1 : 1; });
  var reqIds = {}; KB.requests.forEach(function (r) { reqIds[r.id] = r; });
  var state = { row: rows[0], on: [] };
  $("[data-row]").innerHTML = rows.map(function (r) { return '<option value="' + esc(r) + '">' + esc(r) + " (" + byRow[r].filter(function (l) { return LIVE.test(l.status); }).length + " levers)</option>"; }).join("");

  function pairInfo(a, b) { return KB.pairs[[a, b].sort().join("|")] || null; }
  function blockedBy(l) {
    for (var i = 0; i < state.on.length; i++) {
      if (state.on[i] === l.id) continue;
      var p = pairInfo(state.on[i], l.id);
      if (p && /NOT-COMPOSABLE|DEAD/.test(p.verdict)) return state.on[i];
    }
    return null;
  }
  var GROUP = [["works", "Found: measured or counted on a real program"], ["filed", "Filed in an entry"], ["projected", "Projected: priced, never built"], ["open", "Open: no verdict yet"]];
  function leverCard(l, dead) {
    var on = state.on.indexOf(l.id) >= 0, blk = !dead && !on ? blockedBy(l) : null;
    return '<div class="lever" role="button" tabindex="0" data-lever="' + l.id + '" aria-pressed="' + on + '" aria-disabled="' + (dead || !!blk) + '">' +
      '<span class="bits">' + esc(l.bitsText || "—") + '</span><span>' + esc(l.text.length > 220 ? l.text.slice(0, 220) + "..." : l.text) + '</span><span class="chip chip--' + l.status + '">' + l.status + "</span>" +
      (blk ? '<span class="why">a test says this does not stack with ' + blk + "</span>" : "") +
      '<span class="src">' + esc(l.basis || "no basis") + (l.found != null ? " | found " + l.found : "") + " | " + esc(l.source || "") + " | " + l.id + "</span></div>";
  }
  function renderLevers() {
    var all = byRow[state.row] || [];
    var html = GROUP.map(function (g) {
      var list = all.filter(function (l) { return l.status === g[0] && l.bits < 0; }).sort(function (a, b) { return a.bits - b.bits; });
      return list.length ? "<h3>" + esc(g[1]) + ' <span class="muted">' + list.length + "</span></h3>" + list.map(function (l) { return leverCard(l, false); }).join("") : "";
    }).join("");
    var dead = all.filter(function (l) { return l.status === "closed"; });
    if (dead.length) html += '<details class="group"><summary>Known not to work on this row (' + dead.length + ")</summary>" + dead.map(function (l) { return leverCard(l, true); }).join("") + "</details>";
    $("[data-levers]").innerHTML = html || "<p class=\"muted\">No levers with a number on this row yet.</p>";
    var b = (KB.rows || {})[state.row];
    $("[data-base]").innerHTML = b ? "our best <b>" + num(b.ours) + "</b>, board best <b>" + num(b.board) + "</b>" + (b.leader ? " (" + esc(b.leader) + ")" : "") : "no board score for this row in the export";
  }
  function renderStack() {
    var L = {}; KB.levers.forEach(function (l) { L[l.id] = l; });
    var on = state.on.map(function (id) { return L[id]; }).filter(Boolean);
    var b = (KB.rows || {})[state.row] || {};
    var sum = on.reduce(function (s, l) { return s + l.bits; }, 0);
    var pairs = [], untested = [], bad = 0;
    for (var i = 0; i < on.length; i++) for (var j = i + 1; j < on.length; j++) {
      var p = pairInfo(on[i].id, on[j].id), id = composeId(on[i].id, on[j].id);
      pairs.push({ a: on[i], b: on[j], p: p, id: id });
      if (!p) untested.push({ a: on[i], b: on[j], id: id });
      else if (/NOT-COMPOSABLE|DEAD/.test(p.verdict)) bad++;
    }
    var unmeasured = on.filter(function (l) { return l.status === "projected" || l.status === "open"; });
    var h = "<h2>Your stack</h2>";
    if (!on.length) { $("[data-stack]").innerHTML = h + '<p class="muted">Click levers on the left to stack them.</p>'; return; }
    h += '<div class="muted">if every lever stacks as recorded</div><div class="score">' + (typeof b.ours === "number" ? num(b.ours + sum) : "—") + '</div><div class="muted">our best ' + num(b.ours) + " " + (sum <= 0 ? "" : "+") + sum.toFixed(5) + " bits</div>";
    h += '<p><span class="chip chip--' + (untested.length || unmeasured.length ? "projected" : "works") + '">' + (untested.length || unmeasured.length ? "projected, not found" : "every piece tested") + "</span> " +
      pairs.length + " pairs: " + (pairs.length - untested.length) + " tested" + (bad ? ", " + bad + " known not to stack" : "") + ", " + untested.length + " untested. " + unmeasured.length + " lever(s) never built.</p>";
    if (pairs.length) h += '<ul class="pairs">' + pairs.map(function (x) { return "<li>" + x.a.id + " + " + x.b.id + ": " + (x.p ? '<span class="chip chip--' + (/NOT|DEAD/.test(x.p.verdict) ? "closed" : "works") + '">' + esc(x.p.verdict) + "</span> " + (x.p.bits == null ? "" : num(x.p.bits)) : '<span class="chip chip--open">untested</span> <code>' + x.id + "</code>" + (reqIds[x.id] ? ' <span class="muted">already requested</span>' : "")) + "</li>"; }).join("") + "</ul>";
    if (untested.length || unmeasured.length) {
      var now = new Date(), stamp = now.getFullYear() + "-" + ("0" + (now.getMonth() + 1)).slice(-2) + "-" + ("0" + now.getDate()).slice(-2) + " " + ("0" + now.getHours()).slice(-2) + ":" + ("0" + now.getMinutes()).slice(-2);
      var lines = untested.map(function (x) { return [stamp, x.id, "COMPOSE", state.row, x.a.id + "," + x.b.id, "lever board"].join("\t"); })
        .concat(unmeasured.map(function (l) { return [stamp, hid("Q", (l.status === "projected" ? "MEASURE|" : "DECIDE|") + l.id), l.status === "projected" ? "MEASURE" : "DECIDE", state.row, l.id, "lever board"].join("\t"); }));
      h += '<p><button type="button" class="btn btn--on" data-send>Copy this stack</button></p><p class="muted">Copies ' + lines.length + " line(s). This is a local export for your notes. Nothing is sent to the research team.</p>" +
        '<textarea class="out" readonly data-out>' + esc(lines.join("\n")) + "</textarea>";
    }
    h += '<p><button type="button" class="btn" data-clear>Clear the stack</button></p>';
    $("[data-stack]").innerHTML = h;
  }
  function toggle(id) {
    var l = KB.levers.filter(function (x) { return x.id === id; })[0];
    if (!l || l.status === "closed") return;
    var i = state.on.indexOf(id);
    if (i >= 0) state.on.splice(i, 1);
    else { if (blockedBy(l)) return; state.on.push(id); }
    renderLevers(); renderStack();
  }
  document.addEventListener("click", function (e) {
    var c = e.target.closest("[data-lever]"); if (c && c.getAttribute("aria-disabled") !== "true") { toggle(c.dataset.lever); return; }
    if (e.target.closest("[data-clear]")) { state.on = []; renderLevers(); renderStack(); return; }
    if (e.target.closest("[data-send]")) {
      var t = $("[data-out]"); t.select();
      var done = function () { e.target.textContent = "Copied."; };
      if (navigator.clipboard) navigator.clipboard.writeText(t.value).then(done, function () { document.execCommand("copy"); done(); }); else { document.execCommand("copy"); done(); }
    }
  });
  document.addEventListener("keydown", function (e) { var c = e.target.closest && e.target.closest("[data-lever]"); if (c && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); toggle(c.dataset.lever); } });
  $("[data-row]").addEventListener("change", function (e) { state.row = e.target.value; state.on = []; renderLevers(); renderStack(); });
  renderLevers(); renderStack();
})();
