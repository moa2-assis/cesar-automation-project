# report_dashboard.py
# Dashboard dark + donut progress + filtros/busca/sort + colapso de erro
# Mantém a API: reset_session, upsert_result, add_screenshot, add_video,
# write_dashboard, write_and_open_dashboard, write_session_summary

import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime

_REPORTS = []
_REPORT_INDEX = {}
_SESSION_START = datetime.now()


def reset_session():
    """Zera buffers globais (útil em runs consecutivos e em sessionstart)."""
    global _REPORTS, _REPORT_INDEX, _SESSION_START
    _REPORTS = []
    _REPORT_INDEX = {}
    _SESSION_START = datetime.now()


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def html_escape(s: str) -> str:
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _read_session_meta(dir_path: Path):
    p = Path(dir_path) / "session_meta.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def upsert_result(item, rep, order=None, test_dirname=None) -> None:
    """
    Grava somente o resultado da fase 'call' (evita sobrescritas por setup/teardown).
    Usa longrepr com fallback seguro (xfail/skip podem não ter longreprtext).
    """
    if getattr(rep, "when", None) != "call":
        return

    nodeid = item.nodeid
    payload = {
        "nodeid": nodeid,
        "name": getattr(item, "name", nodeid.split("::")[-1]),
        "when": "call",
        "outcome": getattr(rep, "outcome", "unknown"),
        "duration": getattr(rep, "duration", None),
        "error": "",
    }

    # erro, se houver:
    if getattr(rep, "failed", False):
        err_text = ""
        if hasattr(rep, "longreprtext") and isinstance(rep.longreprtext, str):
            err_text = rep.longreprtext
        elif hasattr(rep, "longrepr"):
            try:
                err_text = str(rep.longrepr)
            except Exception:
                err_text = ""
        payload["error"] = err_text

    if order is not None:
        payload["order"] = order
    if test_dirname:
        payload["dir"] = test_dirname

    idx = _REPORT_INDEX.get(nodeid)
    if idx is not None:
        _REPORTS[idx].update(payload)
    else:
        _REPORT_INDEX[nodeid] = len(_REPORTS)
        _REPORTS.append(payload)


def add_screenshot(item, rel_path: str) -> None:
    idx = _REPORT_INDEX.get(item.nodeid)
    if idx is not None and rel_path:
        _REPORTS[idx]["screenshot"] = rel_path


def add_video(item, rel_path: str) -> None:
    idx = _REPORT_INDEX.get(item.nodeid)
    if idx is not None and rel_path:
        _REPORTS[idx]["video"] = rel_path


# =====================  UI (CSS/JS)  =====================

_DARK_CSS = r"""
:root{
  --bg:#0f1115;
  --panel:#141821;
  --panel-2:#0c0f14;
  --text:#e6eaf2;
  --muted:#9aa4b2;
  --pass:#20c997;
  --fail:#ff6b6b;
  --skip:#f2c94c;
  --border:#242b36;
  --accent:#6ea8fe;
  --link:#8ab4ff;
  --code-bg:#0b0d12;
}
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0; background:var(--bg); color:var(--text);
  font: 14px/1.5 Inter,system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
}
a{color:var(--link); text-decoration:none}
a:hover{text-decoration:underline}
h1{margin:24px 0 12px; font-size:22px; letter-spacing:.2px}

.container{max-width:1200px; margin:0 auto; padding:0 16px 40px}
.card{
  background:linear-gradient(180deg,var(--panel),var(--panel-2));
  border:1px solid var(--border); border-radius:14px; padding:14px 16px; margin:10px 0;
  box-shadow:0 10px 20px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.02);
}

.summary{
  display:grid; gap:12px; grid-template-columns: repeat(5, minmax(0,1fr));
  align-items:stretch;
}
.kpi{
  padding:12px 14px; border-radius:12px; border:1px solid var(--border);
  background: radial-gradient(1200px 1200px at -20% -20%,rgba(110,168,254,.08),transparent 40%),
              linear-gradient(180deg,var(--panel),var(--panel-2));
}
.kpi b{display:block; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.08em}
.kpi span{display:block; font-size:20px; margin-top:6px}
.kpi.pass span{color:var(--pass)}
.kpi.fail span{color:var(--fail)}
.kpi.skip span{color:var(--skip)}

.progress-donut{
  display:flex; align-items:center; justify-content:center;
  position:relative; min-height:130px; padding:12px;
}
.donut{
  position:relative; width:140px; height:140px;
  display:grid; place-items:center;
}
.donut svg{width:140px; height:140px; transform:rotate(-90deg)}
.donut .bg{stroke:#1a2230; stroke-width:12; fill:none}
.donut .fg{stroke:var(--pass); stroke-width:12; fill:none; stroke-linecap:round; transition:stroke-dashoffset .6s ease, stroke .3s ease}
.donut .label{
  position:absolute; inset:0; display:grid; place-items:center; transform:rotate(0);
  font-weight:700; font-size:20px
}
.donut .sub{display:block; margin-top:2px; font-size:11px; color:var(--muted); font-weight:600; letter-spacing:.06em}

.toolbar{
  display:flex; flex-wrap:wrap; gap:8px; align-items:center; justify-content:space-between; margin:14px 0;
}
.controls{display:flex; gap:8px; flex-wrap:wrap}
.btn{
  cursor:pointer; user-select:none;
  background:var(--panel); color:var(--text); border:1px solid var(--border); border-radius:10px; padding:8px 10px;
}
.btn:hover{border-color:#344055; background:#171c26}
.btn.active{outline:2px solid var(--accent); outline-offset:1px}

.search{
  display:flex; gap:8px; align-items:center;
  background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:6px 8px;
}
.search input{
  background:transparent; border:0; color:var(--text); outline:none; min-width:240px
}

table{
  width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:14px;
  border:1px solid var(--border);
}
thead th{
  position:sticky; top:0; background:var(--panel);
  padding:12px 10px; text-align:left; font-weight:600; border-bottom:1px solid var(--border);
  cursor:pointer; user-select:none;
}
thead th .sort{opacity:.55; margin-left:6px; font-size:11px}
tbody tr{background:var(--panel-2)}
tbody tr:nth-child(odd){background:#121722}
tbody tr:hover{background:#1a2130}
td{padding:10px; border-bottom:1px solid var(--border); vertical-align:top}

.badge{padding:4px 8px; border-radius:999px; font-size:12px; font-weight:600; display:inline-block}
.badge.pass{background:rgba(32,201,151,.12); color:var(--pass); border:1px solid rgba(32,201,151,.35)}
.badge.fail{background:rgba(255,107,107,.12); color:var(--fail); border:1px solid rgba(255,107,107,.35)}
.badge.skip{background:rgba(242,201,76,.12); color:var(--skip); border:1px solid rgba(242,201,76,.35)}

.artifacts a{margin-right:10px}

pre{
  margin:0; max-height:160px; overflow:auto; background:var(--code-bg);
  border:1px solid var(--border); border-radius:10px; padding:10px; white-space:pre-wrap
}
pre.collapsed{max-height:52px}
.row-actions{display:flex; gap:8px; margin-top:6px}
.linklike{cursor:pointer; color:var(--link); font-size:12px}
.linklike:hover{text-decoration:underline}

.footer{margin-top:18px; color:var(--muted); font-size:12px; text-align:center}

@media (max-width:900px){
  .summary{grid-template-columns: repeat(2,minmax(0,1fr));}
  thead{display:none}
  tbody tr{display:grid; grid-template-columns: 1fr; gap:6px; padding:8px}
  td{border:0; padding:4px 0}
  td::before{content:attr(data-th) ": "; color:var(--muted); font-weight:600}
}
"""

_DARK_JS = r"""
(function(){
  const $ = (sel,ctx=document)=>ctx.querySelector(sel);
  const $$ = (sel,ctx=document)=>Array.from(ctx.querySelectorAll(sel));
  function save(k,v){ try{ localStorage.setItem(k, JSON.stringify(v)); }catch(e){} }
  function load(k,def){ try{ const v = localStorage.getItem(k); return v? JSON.parse(v): def }catch(e){ return def } }

  function computeStats(table, considerHidden=false){
    const rows = $$('tbody tr', table).filter(r=> considerHidden ? true : r.style.display !== 'none');
    let total=0, passed=0, failed=0, skipped=0;
    rows.forEach(r=>{
      if (considerHidden || r.style.display !== 'none'){
        total++;
        const badge = r.querySelector('td:nth-child(4) .badge');
        const cls = badge ? (badge.classList.contains('passed')?'passed':
                             badge.classList.contains('failed')?'failed':
                             badge.classList.contains('skipped')?'skipped':'') : '';
        if(cls==='passed') passed++;
        else if(cls==='failed') failed++;
        else if(cls==='skipped') skipped++;
      }
    });
    const passRate = total ? (passed/total)*100 : 0;
    return {total, passed, failed, skipped, passRate};
  }

  // donut progress component
  function mountDonut(){
    if ($('#donut-card')) return;
    const wrap = document.createElement('div');
    wrap.className='card';
    wrap.id='donut-card';
    wrap.innerHTML = `
      <div class="summary">
        <div class="kpi">
          <b>Session</b><span id="kpi-session">—</span>
        </div>
        <div class="kpi pass"><b>Passed</b><span id="kpi-passed">0</span></div>
        <div class="kpi fail"><b>Failed</b><span id="kpi-failed">0</span></div>
        <div class="kpi skip"><b>Skipped</b><span id="kpi-skipped">0</span></div>
        <div class="kpi progress-donut">
          <div class="donut" aria-label="Pass rate">
            <svg viewBox="0 0 120 120">
              <circle class="bg" cx="60" cy="60" r="52"></circle>
              <circle class="fg" id="donut-fg" cx="60" cy="60" r="52"
                      stroke-dasharray="326.726" stroke-dashoffset="326.726"></circle>
            </svg>
            <div class="label">
              <div><span id="donut-label">0%</span><div class="sub">pass rate</div></div>
            </div>
          </div>
        </div>
      </div>
    `;
    const container = $('.container') || document.body;
    container.insertBefore(wrap, container.querySelector('h1').nextSibling);
    // session name (if available)
    const session = document.body.getAttribute('data-session') || '';
    if(session) $('#kpi-session').textContent = session;
  }

  function updateDonut(stats){
    const fg = $('#donut-fg'); if(!fg) return;
    // circumference ~ 2 * pi * r = 2*3.14159*52 = 326.726
    const C = 326.726;
    const pct = Math.max(0, Math.min(100, stats.passRate));
    const off = C * (1 - pct/100);
    fg.style.strokeDashoffset = off.toFixed(2);
    // cor baseada em faixa
    fg.style.stroke = pct >= 90 ? '#20c997' : (pct >= 70 ? '#46d4bd' : (pct >= 40 ? '#e5c07b' : '#ff6b6b'));
    const lbl = $('#donut-label'); if(lbl) lbl.textContent = `${pct.toFixed(1)}%`;
    // KPIs
    const p = $('#kpi-passed'), f = $('#kpi-failed'), s = $('#kpi-skipped');
    if(p) p.textContent = String(stats.passed);
    if(f) f.textContent = String(stats.failed);
    if(s) s.textContent = String(stats.skipped);
  }

  function ensureToolbar(){
    if ($('#toolbar')) return;
    const wrap = document.createElement('div');
    wrap.className='card';
    wrap.innerHTML = `
      <div id="toolbar" class="toolbar">
        <div class="controls">
          <button class="btn filter" data-filter="all">All</button>
          <button class="btn filter" data-filter="passed">Passed</button>
          <button class="btn filter" data-filter="failed">Failed</button>
          <button class="btn filter" data-filter="skipped">Skipped</button>
          <button class="btn" id="toggle-compact">Compact</button>
        </div>
        <div class="search">
          🔎 <input id="search" placeholder="Buscar por nome/erro..." />
          <button class="btn" id="clear">Limpar</button>
        </div>
      </div>
    `;
    const container = $('.container') || document.body;
    container.insertBefore(wrap, container.querySelector('table'));
  }

  function enhanceTable(){
    const table = $('table'); if(!table) return;

    // Add data-th for responsive + badges + collapse
    const ths = $$('thead th', table);
    const rows = $$('tbody tr', table);
    rows.forEach(row=>{
      const tds = $$('td', row);
      tds.forEach((td,i)=> td.setAttribute('data-th', (ths[i] && ths[i].innerText.trim()) || ''));
      // badge styling by outcome
      const out = row.querySelector('td:nth-child(4)');
      if(out){
        const val = out.textContent.trim();
        out.innerHTML = `<span class="badge ${val}">${val}</span>`;
      }
      // error block collapse + actions
      const errCell = row.lastElementChild;
      if(errCell){
        const pre = errCell.querySelector('pre');
        if(pre){
          pre.classList.add('collapsed');
          const actions = document.createElement('div');
          actions.className='row-actions';
          const toggle = document.createElement('span');
          toggle.className='linklike'; toggle.textContent='expandir';
          toggle.addEventListener('click',()=>{
            pre.classList.toggle('collapsed');
            toggle.textContent = pre.classList.contains('collapsed') ? 'expandir' : 'recolher';
          });
          const copy = document.createElement('span');
          copy.className='linklike'; copy.textContent='copiar erro';
          copy.addEventListener('click',()=>{
            navigator.clipboard.writeText(pre.innerText).catch(()=>{});
          });
          actions.appendChild(toggle); actions.appendChild(copy);
          errCell.appendChild(actions);
        }
      }
    });

    // Sorting
    ths.forEach((th, idx)=>{
      const span = document.createElement('span');
      span.className='sort'; span.textContent='⇅';
      th.appendChild(span);
      th.addEventListener('click', ()=> sortBy(idx));
    });

    function sortBy(idx){
      const tbody = $('tbody', table);
      const rows = $$('tr', tbody);
      const current = table.getAttribute('data-sort') || '';
      const dir = current === `${idx}:asc` ? 'desc' : 'asc';
      table.setAttribute('data-sort', `${idx}:${dir}`);
      rows.sort((a,b)=>{
        const ta = (a.children[idx]?.innerText||'').trim().toLowerCase();
        const tb = (b.children[idx]?.innerText||'').trim().toLowerCase();
        if(!isNaN(parseFloat(ta)) && !isNaN(parseFloat(tb))){
          return (dir==='asc'?1:-1)*(parseFloat(ta)-parseFloat(tb));
        }
        return (dir==='asc'?1:-1)*(ta>tb?1:ta<tb?-1:0);
      });
      rows.forEach(r=>tbody.appendChild(r));
      save('dash_sort', `${idx}:${dir}`);
    }

    // Filters & search
    const btns = $$('.filter');
    const search = $('#search');
    const clear = $('#clear');
    const compact = $('#toggle-compact');

    function updateButtons(){
      const want = load('dash_filter','all');
      btns.forEach(b=> b.classList.toggle('active', b.dataset.filter===want));
    }

    function applyFilters(){
      const active = btns.find(b=>b.classList.contains('active'));
      const status = active ? active.dataset.filter : 'all';
      const q = (search.value||'').toLowerCase();

      $$('tbody tr', table).forEach(tr=>{
        const outBadge = tr.querySelector('td:nth-child(4) .badge');
        const text = tr.innerText.toLowerCase();
        const matchesStatus = (status==='all') || (outBadge && outBadge.classList.contains(status));
        const matchesQuery = !q || text.includes(q);
        tr.style.display = (matchesStatus && matchesQuery) ? '' : 'none';
      });

      save('dash_filter', status);
      save('dash_query', q);
      updateButtons();

      // Atualiza donut com base no filtro atual
      const statsFiltered = computeStats(table, /*considerHidden*/false);
      updateDonut(statsFiltered);
    }

    // restore state
    const savedFilter = load('dash_filter','all');
    const savedQuery = load('dash_query','');
    const savedSort = load('dash_sort',null);

    btns.forEach(b=> b.classList.toggle('active', b.dataset.filter===savedFilter));
    if(search) search.value = savedQuery||'';
    if(savedSort){
      const [i,dir] = savedSort.split(':');
      sortBy(parseInt(i,10));
      if(dir==='desc') sortBy(parseInt(i,10)); // toggle again
    }

    btns.forEach(b=> b.addEventListener('click', ()=>{
      btns.forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      applyFilters();
    }));
    if(search){ search.addEventListener('input', applyFilters); }
    if(clear){ clear.addEventListener('click', ()=>{ search.value=''; applyFilters(); }); }

    compact?.addEventListener('click', ()=>{
      document.body.classList.toggle('compact');
      compact.classList.toggle('active');
      save('dash_compact', document.body.classList.contains('compact'));
    });
    if(load('dash_compact', false)){ document.body.classList.add('compact'); compact?.classList.add('active'); }

    // Inicial: badge & donut dos totais
    const statsAll = computeStats(table, /*considerHidden*/true);
    updateDonut(statsAll);
    applyFilters(); // aplica filtro/busca salvos e atualiza donut filtrado
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    // lê nome da sessão do <body data-session="">
    mountDonut();
    ensureToolbar();
    enhanceTable();
  });
})();
"""


def _build_dashboard_html(session_dir_name: str, dir_path: Path) -> str:
    total = len(_REPORTS)
    failed = sum(1 for r in _REPORTS if r.get("outcome") == "failed")
    passed = sum(1 for r in _REPORTS if r.get("outcome") == "passed")
    skipped = sum(1 for r in _REPORTS if r.get("outcome") == "skipped")

    def pct(x):
        return (x / total * 100.0) if total else 0.0

    # cards de resumo (além do donut)
    summary_html = (
        f"<div class='card'><div class='summary'>"
        f"<div class='kpi'><b>Total</b><span>{total}</span></div>"
        f"<div class='kpi pass'><b>Passed</b><span>{passed} ({pct(passed):.1f}%)</span></div>"
        f"<div class='kpi fail'><b>Failed</b><span>{failed} ({pct(failed):.1f}%)</span></div>"
        f"<div class='kpi skip'><b>Skipped</b><span>{skipped} ({pct(skipped):.1f}%)</span></div>"
        f"<div class='kpi'><b>Started</b><span>{html_escape(_SESSION_START.strftime('%Y-%m-%d %H:%M:%S'))}</span></div>"
        f"</div></div>"
    )

    # ordena por: failed -> passed -> skipped, depois por 'order' se existir
    outcome_weight = {"failed": 0, "passed": 1, "skipped": 2}
    rows = []
    for r in sorted(
        _REPORTS,
        key=lambda x: (outcome_weight.get(x.get("outcome"), 9), x.get("order", 999999))
    ):
        cls = {"failed": "fail", "passed": "pass", "skipped": "skip"}.get(r.get("outcome"), "")
        err = html_escape((r.get("error") or "")[:4000])
        dur_raw = r.get("duration")
        dur = f"{dur_raw:.2f}s" if isinstance(dur_raw, (int, float)) else ""
        files = " | ".join([x for x in [
            f"📸 <a href='{r.get('screenshot')}'>screenshot</a>" if r.get("screenshot") else "",
            f"🎥 <a href='{r.get('video')}'>video</a>" if r.get("video") else ""
        ] if x])
        rows.append(
            f"<tr class='{cls}'>"
            f"<td>{html_escape(str(r.get('order','')))}</td>"
            f"<td>{html_escape(r.get('name',''))}</td>"
            f"<td>{html_escape(r.get('when',''))}</td>"
            f"<td>{html_escape(r.get('outcome',''))}</td>"
            f"<td>{dur}</td>"
            f"<td class='artifacts'>{files}</td>"
            f"<td><pre>{err}</pre></td>"
            f"</tr>"
        )

    caps = _read_session_meta(dir_path).get("capabilities", {})
    env_html = ""
    if caps:
        env_html = (
            f"<div class='card'><b>Environment</b><br>"
            f"deviceName: {html_escape(str(caps.get('appium:deviceName', '')))} | "
            f"platform: {html_escape(str(caps.get('platformName', '')))} | "
            f"appPackage: {html_escape(str(caps.get('appium:appPackage', '')))}</div>"
        )

    # body carrega data-session pro donut exibir
    return f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test Dashboard</title>
<style>{_DARK_CSS}</style>
<script>{_DARK_JS}</script>
</head>
<body data-session="{html_escape(session_dir_name)}">
  <div class="container">
    <h1>Test Dashboard</h1>
    {summary_html}
    {env_html}
    <table class="table">
      <thead>
        <tr>
          <th>Order</th>
          <th>Test</th>
          <th>When</th>
          <th>Outcome</th>
          <th>Duration</th>
          <th>Artifacts</th>
          <th>Error</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    <div class="footer">generated at {html_escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</div>
  </div>
</body>
</html>"""


def write_dashboard(output_dir: Path) -> Path:
    """Gera o dashboard.html sem abrir o navegador."""
    ensure_dir(str(output_dir))
    path = Path(output_dir) / "dashboard.html"
    html = _build_dashboard_html(Path(output_dir).name, output_dir)
    path.write_text(html, encoding="utf-8")
    print(f"\nDashboard written to {path}")
    return path


def write_and_open_dashboard(output_dir: Path) -> None:
    """Gera o dashboard.html e abre no navegador (se não for CI)."""
    path = write_dashboard(output_dir)
    if not os.environ.get("CI"):
        try:
            webbrowser.open(path.resolve().as_uri())
        except Exception:
            pass


def write_session_summary(output_dir: Path, exitstatus: int) -> None:
    ensure_dir(str(output_dir))
    total = len(_REPORTS)
    failed = sum(1 for r in _REPORTS if r.get("outcome") == "failed")
    passed = sum(1 for r in _REPORTS if r.get("outcome") == "passed")
    skipped = sum(1 for r in _REPORTS if r.get("outcome") == "skipped")
    finished = datetime.now()

    payload = {
        "session_info": {
            "timestamp": Path(output_dir).name,
            "started_at": _SESSION_START.strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": finished.strftime("%Y-%m-%d %H:%M:%S"),
            "pytest_exitstatus": exitstatus,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": round((passed / total * 100.0), 2) if total else 0.0,
        },
        "tests": _REPORTS,
    }

    (Path(output_dir) / "session_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )