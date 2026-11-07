/* Round Climber encyclopedia: every record in kb/knowledge.js (built by tools/kb_build.js), searchable and filterable.
   Works from file:// (the data is a script, not a fetch). */
(function () {
  "use strict";
  var KB = window.KB;
  if (KB) KB.requests = KB.requests || []; // Private queue omitted from public data.
  var $ = function (s) { return document.querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  if (!KB) { $("[data-list]").innerHTML = "<p>kb/knowledge.js is missing: run <code>node tools/kb_build.js</code> in this folder.</p>"; return; }
  var chip = function (s) { return '<span class="chip chip--' + esc(String(s).replace(/[^\w\/-]/g, "-")) + '">' + esc(s) + "</span>"; };
  var long = function (s, n) {
    s = String(s || ""); n = n || 360;
    if (s.length <= n) return esc(s);
    return '<details><summary>' + esc(s.slice(0, n)) + '...</summary>' + esc(s) + "</details>";
  };
  var num = function (v) { return typeof v === "number" && isFinite(v) ? v.toFixed(5).replace(/0+$/, "").replace(/\.$/, "") : "—"; };
  $("[data-built]").textContent = "built " + KB.builtAt.slice(0, 16).replace("T", " ") + " UTC" + (KB.missing && KB.missing.length ? ", sources missing: " + KB.missing.join(", ") : "");

  var leverById = {}; KB.levers.forEach(function (l) { leverById[l.id] = l; });
  var openReq = KB.requests.filter(function (r) { return r.state === "open"; });

  /* headline cards */
  var count = function (list, f) { var o = {}; list.forEach(function (x) { var k = f(x); o[k] = (o[k] || 0) + 1; }); return o; };
  var ls = count(KB.levers, function (l) { return l.status; });
  $("[data-cards]").innerHTML = [
    ["levers recorded", KB.levers.length, (ls.works || 0) + " found, " + (ls.filed || 0) + " filed, " + (ls.projected || 0) + " projected, " + (ls.closed || 0) + " dead"],
    ["grid cells", KB.cells.length, KB.cells.filter(function (c) { return c.status === "blocked"; }).length + " parked as blocked"],
    ["round-dig answers", KB.dig.length, KB.dig.filter(function (d) { return d.letter === "O"; }).length + " never asked, " + KB.dig.filter(function (d) { return d.letter === "L"; }).length + " only by neighbour"],
    ["projected checked", KB.pvf.length, KB.pvf.filter(function (p) { return p.outcome === "found"; }).length + " held up"],
    ["filings", KB.filings.length, KB.filings.filter(function (f) { return f.status === "passed"; }).length + " passed the judges"],
    ["research snapshot", "public", "Operational request queue excluded"]
  ].map(function (c) { return '<div class="card"><b>' + c[1] + "</b><span>" + esc(c[0]) + "</span><div class=\"muted\">" + esc(c[2]) + "</div></div>"; }).join("");

  /* row-by-row summary */
  (function () {
    var rows = {};
    var touch = function (k) { if (!k) k = "(no row)"; return rows[k] || (rows[k] = { k: k, lw: 0, lp: 0, lc: 0, lo: 0, ca: 0, cc: 0, cn: 0, cb: 0, req: 0 }); };
    KB.levers.forEach(function (l) { var o = touch(l.row); if (/works|filed/.test(l.status)) o.lw++; else if (l.status === "projected") o.lp++; else if (l.status === "closed") o.lc++; else if (l.status === "open") o.lo++; });
    KB.cells.forEach(function (c) { var o = touch(c.row); if (c.status === "alive") o.ca++; else if (c.status === "closed") o.cc++; else if (c.status === "n/a") o.cn++; else if (c.status === "blocked") o.cb++; });
    openReq.forEach(function (r) { touch(r.row).req++; });
    Object.keys(KB.rows || {}).forEach(function (k) { touch(k); });
    var key = function (k) { var m = k.match(/^(.*?)-r(\d+)$/); return m ? m[1] + "-" + ("000" + m[2]).slice(-3) : k + "-zzz"; };
    var list = Object.keys(rows).sort(function (a, b) { return key(a) < key(b) ? -1 : 1; }).map(function (k) { return rows[k]; });
    $("[data-summary]").innerHTML = '<table class="summary"><thead><tr><th>row</th><th>our best</th><th>board best</th><th>levers found</th><th>projected</th><th>dead</th><th>open</th><th>cells alive</th><th>closed</th><th>n/a</th><th>blocked</th><th>tests owed</th></tr></thead><tbody>' +
      list.map(function (o) { var b = (KB.rows || {})[o.k] || {}; return "<tr><td><a href=\"#\" data-row-link=\"" + esc(o.k) + "\">" + esc(o.k) + "</a></td><td>" + num(b.ours) + "</td><td>" + num(b.board) + (b.leader && b.leader !== "Jbenisek" ? ' <span class="muted">' + esc(b.leader) + "</span>" : "") + "</td><td>" + o.lw + "</td><td>" + o.lp + "</td><td>" + o.lc + "</td><td>" + o.lo + "</td><td>" + o.ca + "</td><td>" + o.cc + "</td><td>" + o.cn + "</td><td>" + o.cb + "</td><td><b>" + o.req + "</b></td></tr>"; }).join("") + "</tbody></table>";
  })();

  /* the tabs */
  var TABS = {
    levers: { label: "Levers", items: KB.levers, status: function (x) { return x.status; },
      head: ["bits", "status", "row", "lever and notes", "basis", "applied in", "found (answered)", "source"],
      row: function (l) { return [esc(l.bitsText || "—"), chip(l.status), esc(l.row || "—"), long(l.text) + (l.notes ? '<div class="muted">' + long(l.notes, 220) + "</div>" : ""), esc(l.basis), esc(l.applied), l.found != null || l.foundVerdict ? esc((l.foundVerdict || "") + " " + (l.found == null ? "" : l.found)) : '<span class="muted">not yet</span>', '<code>' + esc(l.source) + "</code> " + '<span class="muted mono">' + l.id + "</span>"]; } },
    cells: { label: "Grid cells", items: KB.cells, status: function (x) { return x.status; },
      head: ["grid", "row of the grid", "column", "status", "alive / dead", "reason", "file"],
      row: function (c) { return [esc(c.grid), long(c.rowName, 120), esc(c.col), chip(c.status), long([c.alive, c.dead].filter(Boolean).join(" | "), 120), long(c.reason, 300), '<code>' + esc(c.file) + "</code>"]; } },
    dig: { label: "Round dig", items: KB.dig, status: function (x) { return x.letter; },
      head: ["round", "line", "question", "letter"],
      row: function (d) { return ["r" + d.round, esc(d.part) + ' <span class="muted">' + esc(d.partName) + "</span>", esc(d.q), chip(d.letter)]; } },
    pvf: { label: "Projected vs found", items: KB.pvf, status: function (x) { return x.outcome; },
      head: ["when", "row", "projected", "found", "outcome", "verdict as written", "why", "source"],
      row: function (p) { return [esc(p.t), long(p.subject, 140), esc(p.projected), "<b>" + esc(p.found) + "</b>", chip(p.outcome), long(p.verdict, 80), long(p.why, 200), '<code>' + esc(p.source) + "</code>"]; } },
    done: { label: "Agent results", items: KB.done, status: function (x) { return x.verdict; },
      head: ["when", "item", "verdict", "result", "file"],
      row: function (d) { return [esc(d.t), long(d.item, 140), chip(d.verdict), long(d.result, 300), '<code>' + esc(d.file) + "</code>"]; } },
    filings: { label: "Filings", items: KB.filings, status: function (x) { return x.status; },
      head: ["filed", "entry", "score", "status", "row", "result"],
      row: function (f) { return [esc(f.t), '<code>' + esc(f.sub) + "</code> " + '<span class="muted">' + esc(f.slot) + "</span>", num(f.score), chip(f.status), esc(f.row || f.track || "—"), long(f.result, 200)]; } },
    requests: { label: "Tests owed", items: KB.requests, status: function (x) { return x.state === "open" ? "open" : x.state === "answered" ? "answered" : "rejected"; },
      head: ["id", "type", "row", "state", "what is asked", "subject"],
      row: function (r) {
        var subj = r.levers ? r.levers.map(function (id) { var l = leverById[id]; return l ? id + " (" + (l.bitsText || "?") + ") " + l.text.slice(0, 80) : id; }).join(" + ") : r.lever && leverById[r.lever] ? (leverById[r.lever].bitsText || "?") + " " + leverById[r.lever].text : r.subject;
        return ['<code>' + esc(r.id) + "</code>", esc(r.type) + (r.fromPlayer ? ' <span class="chip chip--filed">player x' + r.fromPlayer + "</span>" : ""), esc(r.row || "—"), chip(r.state === "open" ? "open" : r.state === "answered" ? "answered" : "rejected"), esc(r.title), long(subj, 240) + (r.answer ? '<div class="muted">answer: ' + esc(r.answer.verdict + " " + (r.answer.bits == null ? "" : r.answer.bits) + " " + r.answer.evidence) + "</div>" : "")];
      } }
  };
  var state = { tab: "levers", q: "", row: "all", status: "all", shown: 200 };
  delete TABS.requests; // Private queue has no public tab.
  $("[data-tabs]").innerHTML = Object.keys(TABS).map(function (k) { return '<button type="button" role="tab" data-tab="' + k + '" aria-pressed="' + (k === state.tab) + '">' + esc(TABS[k].label) + " <span class=\"muted\">" + TABS[k].items.length + "</span></button>"; }).join("");

  function fillFilters() {
    var T = TABS[state.tab];
    var rows = {}, sts = {};
    T.items.forEach(function (x) { rows[x.row || "(no row)"] = 1; sts[T.status(x)] = (sts[T.status(x)] || 0) + 1; });
    $("[data-filter-row]").innerHTML = '<option value="all">all rows</option>' + Object.keys(rows).sort().map(function (r) { return '<option value="' + esc(r) + '"' + (r === state.row ? " selected" : "") + ">" + esc(r) + "</option>"; }).join("");
    $("[data-filter-status]").innerHTML = '<option value="all">every status</option>' + Object.keys(sts).sort(function (a, b) { return sts[b] - sts[a]; }).map(function (s) { return '<option value="' + esc(s) + '"' + (s === state.status ? " selected" : "") + ">" + esc(s) + " (" + sts[s] + ")</option>"; }).join("");
    if (!rows[state.row]) state.row = "all";
    if (!sts[state.status]) state.status = "all";
  }
  function render() {
    var T = TABS[state.tab];
    var q = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    var list = T.items.filter(function (x) {
      if (state.row !== "all" && (x.row || "(no row)") !== state.row) return false;
      if (state.status !== "all" && T.status(x) !== state.status) return false;
      if (q.length) { var hay = JSON.stringify(x).toLowerCase(); for (var i = 0; i < q.length; i++) if (hay.indexOf(q[i]) < 0) return false; }
      return true;
    });
    var shown = list.slice(0, state.shown);
    $("[data-count]").textContent = "showing " + shown.length + " of " + list.length;
    $("[data-list]").innerHTML = '<table class="list"><thead><tr>' + T.head.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      shown.map(function (x) { return "<tr>" + T.row(x).map(function (c, i) { return '<td class="' + (i === 3 ? "text" : "") + '">' + c + "</td>"; }).join("") + "</tr>"; }).join("") + "</tbody></table>";
    var more = $("[data-more]"); more.hidden = list.length <= state.shown;
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-tab]");
    if (t) { state.tab = t.dataset.tab; state.shown = 200; document.querySelectorAll("[data-tab]").forEach(function (b) { b.setAttribute("aria-pressed", String(b === t)); }); fillFilters(); render(); return; }
    var rl = e.target.closest("[data-row-link]");
    if (rl) { e.preventDefault(); state.row = rl.dataset.rowLink; fillFilters(); render(); $("[data-tabs]").scrollIntoView({ block: "start" }); return; }
    if (e.target.closest("[data-more]")) { state.shown += 200; render(); }
  });
  $("[data-search]").addEventListener("input", function (e) { state.q = e.target.value; state.shown = 200; render(); });
  $("[data-filter-row]").addEventListener("change", function (e) { state.row = e.target.value; state.shown = 200; render(); });
  $("[data-filter-status]").addEventListener("change", function (e) { state.status = e.target.value; state.shown = 200; render(); });
  fillFilters(); render();
})();
