"""Fuzzing Lab: interactive local runner and research results dashboard."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from scripts.ui_runner import get_history, run_experiment, snapshot, ALLOWED_RUNS, ALLOWED_SEEDS

ROOT = Path(__file__).resolve().parent
META = {
    1: dict(title="Order JSON parser", tagline="Unexpected exception", language="Python", tool="Atheris", mechanism="TypeError", color="#4e9ed9", phase="Structured inputs + exception oracle", challenge="F15 · Suitable inputs / F14 · Replay"),
    2: dict(title="Loyalty & discount rules", tagline="Logical mismatch", language="Python", tool="Atheris + reference oracle", mechanism="OracleMismatch", color="#a48af1", phase="Reference oracle + input evaluation", challenge="F15 · Suitable inputs / F18 · Diagnostics"),
    3: dict(title="Binary message parser", tagline="Heap buffer overflow", language="C++", tool="libFuzzer + ASan", mechanism="AddressSanitizer", color="#ed9a63", phase="Input generation + memory oracle", challenge="F16 · Configuration / F18 · Diagnostics"),
    4: dict(title="Resource cleanup", tagline="Memory leak", language="C++", tool="libFuzzer + LSan", mechanism="LeakSanitizer", color="#59c5af", phase="Sanitizer oracle + saved replay", challenge="F14 · Replay / F18 · Diagnostics"),
}

st.set_page_config(page_title="Fuzzing Lab | Research demonstration", page_icon="🔬", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
/* Scientific light theme: restrained ink, paper, teal and muted indigo. */
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],[data-testid="stMain"],.main{background:#f3f5f7!important;color:#253549!important}
[data-testid="stHeader"]{background:#f3f5f7!important}
[data-testid="stSidebar"]{background:#edf1f4!important}
.block-container{max-width:1270px;padding-top:1.65rem;padding-bottom:3.5rem}
h1,h2,h3,h4,p,label{color:#253549}
h1,h2,h3{letter-spacing:-.025em!important}
[data-testid="stVerticalBlock"]{gap:.7rem}
.fl-hero{background:#fff;border:1px solid #d7e0e7;border-top:4px solid #2d8290;border-radius:9px;padding:26px 29px;margin-bottom:15px}
.fl-eyebrow{font-size:11px;letter-spacing:.105em;text-transform:uppercase;color:#397988;font-weight:750}
.fl-h1{font-size:34px;color:#1c3446;font-weight:730;letter-spacing:-.03em;margin:9px 0}
.fl-sub{font-size:14px;line-height:1.6;color:#526b7a;max-width:850px}
.fl-badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.fl-tag{font-size:11px;font-weight:600;color:#356274;background:#edf4f6;border:1px solid #d0e1e6;border-radius:5px;padding:5px 9px}
.fl-section{font-size:19px;font-weight:710;color:#274257;letter-spacing:-.02em;margin:12px 0 8px}
.fl-card{height:170px;padding:17px;border:1px solid #d7e0e7;border-radius:8px;background:#fff;overflow:hidden;border-top:3px solid #bdd3dc}
.fl-cardtop{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.fl-index{font-size:10px;color:#61798b;font-weight:700;letter-spacing:.055em}
.fl-cardtitle{font-size:16px;font-weight:700;color:#213e50;line-height:1.25;margin-bottom:8px}
.fl-desc{font-size:12px;color:#5c7181;line-height:1.45}
.fl-cardfoot{display:flex;align-items:center;justify-content:space-between;margin-top:16px;gap:6px}
.fl-pill{font-size:10px;font-weight:650;padding:4px 7px;border-radius:5px;background:#eef3f6;color:#506878}
.fl-verified{color:#26775d}.fl-pending{color:#9a752a}
.fl-insight{background:#eef5f6;border:1px solid #d1e2e5;border-radius:7px;padding:15px 18px;color:#365461;font-size:13px;line-height:1.6}
.fl-visual{background:#fff;border:1px solid #d4dee5;border-radius:8px;padding:18px;margin:12px 0;color:#253a4f}
.fl-visual-title{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:#3c7280;font-weight:780;margin-bottom:15px}
.fl-flow{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.fl-node{flex:1;min-width:140px;padding:16px 13px;border-radius:6px;background:#f2f7fa;border:1px solid #d2e0e6;text-align:center}
.fl-node small{display:block;color:#5d7b8a;font-size:10px;font-weight:750;letter-spacing:.06em;text-transform:uppercase;margin-bottom:7px}
.fl-node b{display:block;font-size:16px;color:#244459}.fl-node span{display:block;color:#667b88;font-size:11px;margin-top:7px;line-height:1.4}
.fl-arrow{display:flex;align-items:center;color:#608a98;font-weight:800;font-size:22px}
.fl-node.fl-warning{background:#fff3ed;border-color:#e4b6a5}.fl-node.fl-good{background:#edf8f2;border-color:#a8d5bb}
.fl-buffer{display:flex;flex-wrap:wrap;gap:5px;margin-top:15px}
.fl-cell{border:1px solid #8ebec6;background:#e6f2f4;width:40px;height:43px;border-radius:5px;text-align:center;padding-top:5px;color:#276775;font-weight:750;font-size:15px}
.fl-cell small{display:block;color:#4e7e87;font-weight:500;font-size:9px}
.fl-cell.fl-over{border:1px dashed #d39d7d;background:#fff0e8;color:#965b3c}
.fl-footnote{font-size:11px;color:#607789;line-height:1.6;margin-top:11px}
.fl-compare{display:grid;grid-template-columns:1fr 1fr;gap:12px}.fl-comparebox{padding:18px;border-radius:7px;border:1px solid #d6e0e6;background:#f8fafb}
.fl-comparebox strong{font-size:14px;color:#263f52}.fl-big{font-size:28px;font-weight:750;color:#213e51;margin-top:8px}.fl-small{font-size:11px;color:#5b7180}
[data-testid="stMetric"]{padding:12px;border-radius:7px;border:1px solid #d5e0e6;background:#fff}
[data-testid="stMetricValue"]{font-size:1.65rem!important;color:#244a5d!important}
[data-testid="stDataFrame"],div[data-testid="stExpander"],div[data-testid="stVerticalBlockBorderWrapper"]{border-radius:7px!important}
[data-testid="stTabs"] button{font-weight:550!important}
[data-testid="stWidgetLabel"] p{color:#3b5365!important}
div[role="radiogroup"]{border:1px solid #d5e0e6;background:#fff;padding:.25rem .5rem;border-radius:7px;display:inline-flex;gap:.45rem}
[data-testid="stCodeBlock"]{border:1px solid #d5dee5;border-radius:6px}
.fl-labstrip{display:flex;align-items:stretch;gap:6px;flex-wrap:wrap;margin:12px 0 17px}
.fl-step{flex:1;min-width:140px;background:#fff;border:1px solid #d8e1e7;border-left:3px solid #478996;padding:12px 10px;border-radius:4px}
.fl-step b{display:block;font-size:12px;color:#2c5268}.fl-step span{display:block;font-size:11px;color:#667e8c;margin-top:4px}
.fl-connector{align-self:center;color:#849ca9;font-size:18px}
@media(max-width:760px){.fl-h1{font-size:27px}.fl-hero{padding:20px}.fl-card{height:auto;min-height:158px}.fl-arrow,.fl-connector{display:none}}
</style>""", unsafe_allow_html=True)


def navigate_to_runner(target: int) -> None:
    """Streamlit executes callbacks before rebuilding widgets for the next rerun.

    Never assign to a key owned by an already-instantiated st.radio widget
    inside the body of a page; Streamlit raises WidgetAlreadyInstantiated.
    """
    st.session_state["selected_run_target"] = target
    st.session_state["main_page"] = "Run lab"


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def read_result(n: int) -> dict | None:
    file = ROOT / f"Eksperimenti {n}.json"
    if not file.is_file():
        return None
    try:
        data = json.loads(file.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) and data.get("experiment") == n else None
    except (OSError, ValueError):
        return None


def versions(data: dict | None) -> dict:
    if not isinstance(data, dict):
        return {}
    return {r.get("version"): r for r in data.get("results", []) if isinstance(r, dict)}


def verified(data: dict | None) -> bool:
    if not isinstance(data, dict):
        return False
    return data.get("status") == "Verifikuar" and data.get("reproduced") is True and data.get("fixed_replay_ok") is True


def safe_path(reference: object) -> Path | None:
    if not isinstance(reference, str) or not reference:
        return None
    try:
        file = (ROOT / reference).resolve()
        return file if file.is_relative_to(ROOT) and file.is_file() else None
    except (OSError, ValueError):
        return None


def log_excerpt(reference: object) -> str:
    file = safe_path(reference)
    if file is None:
        return ""
    try:
        lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    terms = ("ERROR:", "SUMMARY:", "OracleMismatch", "TypeError", "Traceback", "stat::number_of_executed_units")
    return "\n".join(line.strip() for line in lines if any(t in line for t in terms))[:1800]


def full_log(reference: object, label: str) -> None:
    file = safe_path(reference)
    if file is not None:
        with st.expander(label):
            st.code(file.read_text(encoding="utf-8", errors="replace"), language="text")


def visual(n: int, data: dict | None) -> None:
    replay = (data or {}).get("replay") or {}
    hx = replay.get("input_hex")
    if n == 1:
        value = replay.get("input_utf8") if replay.get("input_utf8") is not None else '{"items":[{"quantity":2,"unit_price_cents":"15.50"}]}'
        markup = f'''<div class="fl-visual"><div class="fl-visual-title">Failure anatomy · Order input validation</div>
        <div class="fl-flow"><div class="fl-node"><small>1 · Input</small><b>Order JSON</b><span>Structured order with item fields</span></div><div class="fl-arrow">→</div>
        <div class="fl-node"><small>2 · Validation</small><b>Price type</b><span>Buggy branch omits type check</span></div><div class="fl-arrow">→</div>
        <div class="fl-node fl-warning"><small>3 · Failure</small><b>Unexpected exception</b><span>Invalid value reaches arithmetic</span></div></div>
        <div class="fl-footnote">Saved input: <code>{e(str(value)[:240])}</code> · Fixed version validates quantity and price before arithmetic.</div></div>'''
    elif n == 2:
        markup = '''<div class="fl-visual"><div class="fl-visual-title">Failure anatomy · Boundary of a business rule</div>
        <div class="fl-flow"><div class="fl-node"><small>1 · Order</small><b>3 items</b><span>First complete bonus group</span></div><div class="fl-arrow">→</div>
        <div class="fl-node fl-warning"><small>2 · Buggy</small><b>3 points</b><span>Off-by-one bonus threshold</span></div><div class="fl-arrow">≠</div>
        <div class="fl-node fl-good"><small>3 · Oracle</small><b>4 points</b><span>3 base + floor(3/3) bonus</span></div></div>
        <div class="fl-footnote">Illustrative deterministic boundary case from the source code, not a claim about the saved fuzzing-trigger input. The reference calculation is independent of the buggy branch.</div></div>'''
    elif n == 3:
        declared = None
        if isinstance(hx, str):
            try:
                payload = bytes.fromhex(hx)
                if len(payload) >= 2 and payload[0] == 0xA5:
                    declared = payload[1]
            except ValueError:
                pass
        count = str(declared) if declared is not None else "10"
        slots = ''.join(f'<div class="fl-cell">{i}<small>valid</small></div>' for i in range(8))
        extras = '<div class="fl-cell fl-over">8<small>overflow</small></div><div class="fl-cell fl-over">9<small>overflow</small></div>'
        markup = f'''<div class="fl-visual"><div class="fl-visual-title">Failure anatomy · Binary payload vs allocated capacity</div>
        <div class="fl-flow"><div class="fl-node"><small>Header</small><b>0xA5</b><span>Message marker</span></div><div class="fl-arrow">→</div>
        <div class="fl-node"><small>Declared length</small><b>{e(count)} bytes</b><span>Read from byte 1 of saved input</span></div><div class="fl-arrow">→</div>
        <div class="fl-node fl-warning"><small>Destination buffer</small><b>8 bytes</b><span>Buggy code trusts declared length</span></div></div>
        <div class="fl-buffer">{slots}{extras}</div>
        <div class="fl-footnote">Green: allocated indices 0–7 · Orange: examples of writes outside capacity. Fixed version rejects lengths above 8. Saved input hex: <code>{e(hx or 'Not recorded yet')}</code></div></div>'''
    else:
        op = None
        if isinstance(hx, str):
            try:
                raw = bytes.fromhex(hx)
                if len(raw) >= 2:
                    op = raw[1]
            except ValueError:
                pass
        op_text = f"0x{op:02X}" if op is not None else "0x80–0xFF"
        markup = f'''<div class="fl-visual"><div class="fl-visual-title">Failure anatomy · Early return and resource ownership</div>
        <div class="fl-flow"><div class="fl-node"><small>1 · Input</small><b>0xB4 / {e(op_text)}</b><span>High bit activates error path</span></div><div class="fl-arrow">→</div>
        <div class="fl-node"><small>2 · Allocation</small><b>64 bytes</b><span>Dynamic buffer on heap</span></div><div class="fl-arrow">→</div>
        <div class="fl-node fl-warning"><small>3 · Buggy path</small><b>Early return</b><span>delete[] is skipped</span></div></div>
        <div class="fl-footnote">Fixed: std::unique_ptr releases the resource even when the function returns early (RAII). Saved triggering input: <code>{e(hx or 'Not recorded yet')}</code>. Refer to the sanitizer log for exact leak totals.</div></div>'''
    html_block(markup)


def experiment_card(n: int, data: dict | None) -> None:
    m = META[n]
    ok = verified(data)
    html_block(f'''<div class="fl-card" ><div class="fl-cardtop"><span class="fl-index">EXPERIMENT {n:02d} · {m['language']}</span><span class="fl-index">{e(m['mechanism'])}</span></div>
    <div class="fl-cardtitle">{e(m['title'])}</div><div class="fl-desc">{e(m['tagline'])}<br>{e(m['tool'])}</div>
    <div class="fl-cardfoot"><span class="fl-pill">{e(m['tool'])}</span><span class="{'fl-verified' if ok else 'fl-pending'}" style="font-size:11px;font-weight:700">{'● Verified' if ok else '○ Awaiting fuzz run'}</span></div></div>''')


def summary_table(results: dict[int, dict | None]) -> None:
    data = []
    for n, m in META.items():
        row = versions(results[n]); bug = row.get("buggy", {}); fixed = row.get("fixed", {})
        data.append({"Experiment": f"{n:02d}", "Test target": m["title"], "Detection": m["mechanism"], "Runs to issue": bug.get("runs"), "Fixed runs": fixed.get("runs"), "Verification": "Recorded ✓" if verified(results[n]) else "Awaiting"})
    st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True, column_config={"Runs to issue": st.column_config.NumberColumn(format="%d"), "Fixed runs": st.column_config.NumberColumn(format="%d")})


def comparison_chart(results: dict[int, dict | None]) -> None:
    """Only show recorded values. Never use fixed-run budgets as a common speed comparator."""
    records = []
    for n in META:
        data = results[n]
        if verified(data):
            bug = versions(data).get("buggy", {})
            runs = bug.get("runs")
            if isinstance(runs, int) and runs > 0:
                records.append({"Target": f"Exp {n:02d} · {META[n]['title']}", "Runs until issue": runs})
    st.markdown("**Observed runs until a reported defect**")
    if records:
        # One recorded campaign per target. These counts describe outcomes, not relative tool performance.
        st.bar_chart(pd.DataFrame(records).set_index("Target"), horizontal=True, color="#3f8a99", height=max(170, len(records) * 68))
        st.caption("Only verified target versions are plotted. Counts come from individual recorded campaigns, with different programs and failure modes; they do not rank tools or languages.")
    else:
        st.info("The comparison will appear when a verified fuzzing result is recorded.")


def verification_matrix(results: dict[int, dict | None]) -> None:
    rows = []
    for n in META:
        data = results[n]
        v = versions(data)
        bug, fixed = v.get("buggy", {}), v.get("fixed", {})
        rows.append({
            "Target": f"{n:02d} · {META[n]['title']}",
            "Defect reproduced": "Confirmed" if data and data.get("reproduced") is True else "Pending",
            "Fixed replay": "Passed" if data and data.get("fixed_replay_ok") is True else "Pending",
            "Fixed fuzz runs": fixed.get("runs"),
            "Evidence": "Verified" if verified(data) else "Not yet verified",
        })
    st.markdown("**Verification evidence matrix**")
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True,
                 column_config={"Fixed fuzz runs": st.column_config.NumberColumn(format="%d")})
    st.caption("Fixed fuzz-run limits are shown as test evidence, not as a measure of defects eliminated or a performance benchmark.")


# Mappings below are an interpretive alignment of two independently cited papers,
# NOT empirical counts measured in Paper A or in our local lab.
RESEARCH_STAGES = {
    "PREPROCESS": {
        "description": "Prepare the program-under-test, build, instrumentation and harness before the campaign.",
        "challenge": "F16 · Setting up and using the fuzzer",
        "issue_count": 32,
        "examples": "Atheris environment and Clang/libFuzzer sanitizer configuration across all four targets.",
        "scope": "The local setup is demonstrable; we did not measure developers' setup effort.",
    },
    "SCHEDULE": {
        "description": "Select fuzz configurations/test cases for each iteration, mostly handled inside Atheris and libFuzzer.",
        "challenge": "No isolated Paper B category is used as a quantitative proxy for this stage.",
        "issue_count": None,
        "examples": "The runner sets a bounded run budget and seed; the fuzz engine implements its own scheduling.",
        "scope": "We did not instrument or experimentally compare scheduling algorithms.",
    },
    "INPUTGEN": {
        "description": "Produce candidate test cases for the target's input format.",
        "challenge": "F15 · Difficulty generating appropriate inputs",
        "issue_count": 6,
        "examples": "Structured JSON orders, loyalty inputs and binary messages in experiments 1–3.",
        "scope": "The selected GitHub category count is not a measure of test-case quality in our lab.",
    },
    "INPUTEVAL": {
        "description": "Execute the program-under-test and apply a bug oracle to detect unexpected behavior.",
        "challenge": "F14 · Reproducing failures; F18 · Unhelpful diagnostic messages",
        "issue_count": None,
        "examples": "Exception, reference oracle, ASan and LSan, with saved inputs and replay checks.",
        "scope": "Reproduction and diagnosis relate to the evaluation workflow; no developer survey was run here.",
    },
    "CONFUPDATE": {
        "description": "Update the fuzzing configuration using execution feedback.",
        "challenge": "Paper B challenges have no unique one-to-one mapping to this internal engine phase.",
        "issue_count": None,
        "examples": "Instrumentation and feedback are handled by existing fuzzers; the local app records run metadata.",
        "scope": "Run history is not itself the algorithmic CONFUPDATE operation.",
    },
}


def evidence_pipeline(data: dict | None) -> None:
    """Reflect real runner / recorded evidence, not a pretend five-step engine."""
    known = isinstance(data, dict)
    evaluated = known and bool(versions(data).get("buggy"))
    reproduced = known and data.get("reproduced") is True
    fixed_ok = known and data.get("fixed_replay_ok") is True
    fully_verified = verified(data)
    checks = [
        ("01 · Prepare", "Target & harness ready", True),
        ("02 · Fuzz", "Recorded campaign", evaluated),
        ("03 · Detect", "Buggy result saved", evaluated),
        ("04 · Replay", "Defect reproduced", reproduced),
        ("05 · Verify", "Fixed tests recorded", fixed_ok and fully_verified),
    ]
    content = '<div class="fl-labstrip">' + ''.join(
        '<div class="fl-step" style="border-left-color:' + ('#27836b' if done else '#b5c1c9') + '">' +
        '<b>' + e(label) + '</b><span>' + e(description) + '</span><span style="font-weight:700;color:' +
        ('#23765d' if done else '#788895') + '">' + ('Recorded' if done else 'Pending') + '</span></div>'
        for label, description, done in checks
    ) + '</div>'
    html_block(content)
    st.caption("The steps show readiness and recorded evidence, not real-time internal fuzzer iterations. "
               "Atheris/libFuzzer implement scheduling, test generation and feedback internally.")


def research_comparison() -> None:
    st.markdown("### Two perspectives on fuzzing")
    st.dataframe(pd.DataFrame([
        {"Dimension": "Research goal", "Paper A · Manès et al.": "Technical systematization", "Paper B · Nourry et al.": "Practitioners' challenges"},
        {"Dimension": "Study design", "Paper A · Manès et al.": "Literature survey and general model", "Paper B · Nourry et al.": "GitHub issue analysis and survey"},
        {"Dimension": "Main output", "Paper A · Manès et al.": "Algorithm 1; taxonomy and design choices", "Paper B · Nourry et al.": "39 challenge categories (22 process, 17 provider)"},
        {"Dimension": "Lab connection", "Paper A · Manès et al.": "Inputs → evaluation → replay", "Paper B · Nourry et al.": "Setup, inputs, reproduction, diagnosis"},
        {"Dimension": "Evidence limits", "Paper A · Manès et al.": "Not a common new fuzzer benchmark", "Paper B · Nourry et al.": "Context-dependent observations; survey sample"},
    ]), hide_index=True, use_container_width=True)
    st.caption("[1] Manès et al., Algorithm 1 and §§2–7; [2] Nourry et al., §§2–4. The comparison is methodological, not a score or ranking.")

    st.markdown("### Selected challenges in Paper B, situated within Paper A's model")
    counts = pd.DataFrame([
        {"Selected category": "PREPROCESS · F16 · Setup", "GitHub issues": 32},
        {"Selected category": "INPUTGEN · F15 · Inputs", "GitHub issues": 6},
        {"Selected category": "INPUTEVAL-related · F14 · Replay", "GitHub issues": 19},
        {"Selected category": "INPUTEVAL-related · F18 · Diagnostics", "GitHub issues": 7},
    ])
    st.bar_chart(counts.set_index("Selected category"), horizontal=True, color="#477f8d", height=285)
    st.caption("The issue counts are from Paper B, Fig. 2 (171 fuzzing-process issues: F16=32, F15=6, F14=19, F18=7). "
               "The association with Paper A phases is our *conceptual interpretation*, not a grouping created or measured by either paper. "
               "Only four selected categories are plotted; these figures do not establish that one phase is objectively harder.")
    st.markdown("**Inspect a technical phase**")
    stage = st.selectbox("Paper A phase", list(RESEARCH_STAGES), key="research_stage")
    detail = RESEARCH_STAGES[stage]
    html_block(f"""<div class="fl-visual"><div class="fl-flow">
      <div class="fl-node"><small>Paper A · Algorithm 1</small><b>{e(stage)}</b><span>{e(detail['description'])}</span></div>
      <div class="fl-arrow">→</div>
      <div class="fl-node"><small>Paper B · Fig. 2</small><b>Developer challenge</b><span>{e(detail['challenge'])}</span></div>
      <div class="fl-arrow">→</div>
      <div class="fl-node"><small>Our lab · Example</small><b>Practical link</b><span>{e(detail['examples'])}</span></div>
    </div><div class="fl-footnote">Scope: {e(detail['scope'])}</div></div>""")
    st.caption("The arrows indicate an explanatory relation, **not** a causal finding. Our lab does not reproduce the developer survey.")


def process_strip() -> None:
    items = [("01 · Prepare", "Choose target & seed"), ("02 · Execute", "Generate and evaluate inputs"),
             ("03 · Detect", "Oracle or sanitizer report"), ("04 · Replay", "Verify the saved input"),
             ("05 · Fix", "Run corrected variant")]
    content = '<div class="fl-labstrip">' + ''.join(
        f'<div class="fl-step"><b>{e(title)}</b><span>{e(detail)}</span></div>'
        + ('<span class="fl-connector">→</span>' if i < len(items) - 1 else '')
        for i, (title, detail) in enumerate(items)) + '</div>'
    html_block(content)


html_block('''<section class="fl-hero"><div class="fl-eyebrow">Academic case study · Software testing</div><div class="fl-h1">Fuzzing Experiment Lab</div><div class="fl-sub">Four controlled targets. One reproducible workflow: generate inputs, detect unexpected behavior, replay the defect and inspect the corrected version.</div><div class="fl-badges"><span class="fl-tag">Python · Atheris</span><span class="fl-tag">C++ · libFuzzer</span><span class="fl-tag">AddressSanitizer</span><span class="fl-tag">LeakSanitizer</span></div></section>''')

page = st.radio("Page", ["Overview", "Explore experiments", "Run lab", "Research connection"], horizontal=True, label_visibility="collapsed", key="main_page")
results = {n: read_result(n) for n in META}

if page == "Overview":
    total = sum(verified(d) for d in results.values())
    html_block('<div class="fl-section">Experiments at a glance</div>')
    cols = st.columns(4, gap="small")
    for n, c in enumerate(cols, start=1):
        with c:
            experiment_card(n, results[n])
    html_block('<div class="fl-section">Recorded evidence</div>')
    a, b, c = st.columns(3)
    a.metric("Verified target versions", f"{total} / 4")
    b.metric("Updated Python targets", "2")
    c.metric("Updated C++ targets", "2")
    summary_table(results)
    html_block('<div class="fl-section">Experimental comparisons</div>')
    ch, ev = st.tabs(["Recorded discovery effort", "Verification matrix"])
    with ch:
        comparison_chart(results)
    with ev:
        verification_matrix(results)
    html_block('<div class="fl-section">Method · one reproducible workflow</div>')
    process_strip()
    st.caption("This strip describes the real runner workflow; stage-specific statuses appear under Explore experiments.")
    recent = get_history()
    if recent:
        st.markdown("**Recent local executions**")
        st.dataframe(pd.DataFrame([{"UTC": r.get("started_utc", "")[:19], "Experiment": r.get("experiment") or "Python checks", "Mode": r["mode"], "Result": "Completed" if r.get("success") else "Needs attention", "Evidence": r.get("evidence_status") or "—"} for r in recent[:6]]), hide_index=True, use_container_width=True)
    html_block('''<div class="fl-insight"><b>How to read these results.</b> “Runs to issue” describes one recorded fuzzing campaign for each target. The programs, failure modes and environments differ, so the counts are <b>not</b> a comparison of fuzzer speed or programming languages. A completed fixed run does not prove that all defects are absent.</div>''')
    with st.expander("What does each experiment investigate?"):
        for n, m in META.items():
            st.markdown(f"**{n:02d} · {m['title']}** — {m['phase']}  ")

elif page == "Explore experiments":
    choice = st.selectbox("Select a target", list(META), format_func=lambda n: f"{n:02d} · {META[n]['title']} — {META[n]['tagline']}")
    m = META[choice]; data = results[choice]; rows = versions(data)
    st.caption(f"EXPERIMENT {choice:02d}   /   {m['language']}   /   {m['tool']}")
    st.header(m["title"])
    st.write(m["tagline"])
    st.caption("For a fresh execution choose **Run lab** above; this page explores recorded evidence and test cases.")
    st.button("Open Run lab to execute this experiment", key=f"go_run_{choice}",
              on_click=navigate_to_runner, args=(choice,))
    if verified(data):
        st.success("Recorded verification: defect reproduced in the buggy version and fixed-version replay passed. This dashboard reads saved evidence; it does not execute fuzzing live.")
    else:
        st.warning("The updated target has no verified fuzzing campaign recorded yet. Deterministic checks alone do not establish a completed fuzz run.")

    st.markdown("**Execution evidence pipeline**")
    evidence_pipeline(data)
    tabs = st.tabs(["01 · Failure anatomy", "02 · Buggy vs fixed", "03 · Logs & replay", "04 · Research context"])
    with tabs[0]:
        process_strip()
        visual(choice, data)
        st.caption("The visual explains the mechanism of failure. Details not provided by the fuzz run are explicitly labeled illustrative.")
        st.markdown("**Explore an input condition (illustration, not a fuzz run)**")
        if choice == 1:
            qty = st.number_input("Quantity", min_value=1, max_value=100, value=2, step=1, key="exp1_qty")
            price_kind = st.selectbox("Unit price field", ["Integer cents", "null", "String"], key="exp1_price_type")
            price = 1550 if price_kind == "Integer cents" else (None if price_kind == "null" else "15.50")
            payload = {"items": [{"quantity": qty, "unit_price_cents": price}]}
            st.code(json.dumps(payload, ensure_ascii=False), language="json")
            sys.path.insert(0, str(ROOT / 'experiment_1'))
            from order_parser import parse_order, OrderValidationError
            cols = st.columns(2)
            for col, fixed in zip(cols, (False, True)):
                try:
                    out = parse_order(json.dumps(payload).encode(), fixed=fixed)
                    label = f"Accepted: {out['total_cents']} cents"
                except OrderValidationError as exc:
                    label = f"Controlled rejection: {type(exc).__name__}"
                except Exception as exc:
                    label = f"Unexpected failure: {type(exc).__name__}"
                col.metric('Fixed implementation' if fixed else 'Buggy implementation', label)
        elif choice == 2:
            qty = st.slider("Quantity (items)", 1, 15, 3, key="exp2_qty")
            cents = st.select_slider("Unit price (cents)", options=[500, 1000, 2500], value=1000, key="exp2_price")
            coupon = st.selectbox('Coupon', ['NONE', 'SAVE10'], key="exp2_coupon")
            sys.path.insert(0, str(ROOT / 'experiment_2'))
            from loyalty_rules import reference, calculate
            inp = dict(quantity=qty, unit_price_cents=cents, coupon=coupon)
            expected = reference(inp); actual = calculate(inp, fixed=False); corrected = calculate(inp, fixed=True)
            a, b, c = st.columns(3)
            a.metric('Buggy points', actual['points'])
            b.metric('Oracle points', expected['points'], delta=expected['points'] - actual['points'], delta_color='normal')
            c.metric('Fixed points', corrected['points'])
            st.caption(f"Subtotal after discount: {expected['total_cents']} cents · Bonus threshold: every three items. This calculation is deterministic, not a new fuzzing measurement.")
        elif choice == 3:
            declared = st.slider('Declared payload length (bytes)', 1, 16, 10, key="exp3_len")
            st.caption('Assuming the message contains at least the declared number of bytes and has a valid 0xA5 header.')
            allocated = ''.join(f'<span style="display:inline-block;border:1px solid #acc8d4;background:#e8f2f6;color:#34576c;padding:9px;width:34px;text-align:center;margin:2px;border-radius:3px">{i}</span>' for i in range(8))
            overflow = ''.join(f'<span style="display:inline-block;border:1px solid #ce9b7c;background:#fff0e8;color:#98573f;padding:9px;width:34px;text-align:center;margin:2px;border-radius:3px">{i}</span>' for i in range(8, min(declared, 16)))
            html_block(f'<div style="margin:10px 0">{allocated}{overflow}</div>')
            st.markdown(f"**Buggy:** {'out-of-bounds write is reachable' if declared > 8 else 'within buffer capacity'}  ·  **Fixed:** {'rejects declared length above 8' if declared > 8 else 'accepts length if the full payload exists'}")
        else:
            op = st.slider('Operation code', 0, 255, 192, key='exp4_op')
            triggered = bool(op & 0x80)
            c1, c2 = st.columns(2)
            c1.metric('Buggy cleanup', 'Leak path' if triggered else 'Released')
            c2.metric('RAII cleanup', 'Released')
            st.caption(f"Operation 0x{op:02X}. The high bit {'is' if triggered else 'is not'} set; the buggy implementation {'skips' if triggered else 'reaches'} delete[]. This is a control-flow illustration, not a live sanitizer report.")
        with st.expander("Test specification and expected behavior"):
            descriptions = {
                1: "Valid JSON orders contain an items list of objects with integer quantity and unit_price_cents; invalid data must be rejected with OrderValidationError, not an unexpected exception.",
                2: "Reward points = quantity + floor(quantity / 3). A SAVE10 coupon discounts the subtotal by 10% when eligible. A separate reference oracle checks the result.",
                3: "Message format: 0xA5 | declared payload length | payload. The allocated destination buffer is 8 bytes, so declared lengths greater than 8 must be rejected.",
                4: "Message format: 0xB4 | operation code. A high-bit operation code triggers an early exit after a 64-byte allocation. RAII releases memory on all exit paths.",
            }
            st.write(descriptions[choice])
    with tabs[1]:
        first, second = st.columns(2)
        for col, name in ((first, "buggy"), (second, "fixed")):
            item = rows.get(name, {})
            with col:
                with st.container(border=True):
                    st.markdown(f"**{'Buggy version · Issue present' if name == 'buggy' else 'Fixed version · Corrective check'}**")
                    m1, m2 = st.columns(2)
                    m1.metric("Runs", f"{item['runs']:,}" if item.get("runs") is not None else "—")
                    m2.metric("Time (s)", f"{item['duration_seconds']:.3f}" if isinstance(item.get("duration_seconds"), (int,float)) else "—")
                    st.caption(item.get("status", "Not run on this updated target"))
        st.caption("Each fixed campaign has its own bounded run count. The run durations are not comparable across different experiment targets.")
        if data and data.get("timestamp_utc"):
            st.caption(f"Recorded at {data['timestamp_utc']} · seed: {data.get('seed', 'not provided')}")
    with tabs[2]:
        if data is None:
            st.info(f"Run `python3 experiment_{choice}/run_experiment.py` with the required fuzzing dependencies installed to produce a verified record.")
        else:
            input_hex = (data.get("replay") or {}).get("input_hex")
            if isinstance(input_hex, str):
                st.markdown("**Triggering input · hexadecimal**")
                st.code(input_hex if input_hex else "(empty input)", language="text")
                if choice in (1, 2) and isinstance((data.get("replay") or {}).get("input_utf8"), str):
                    with st.expander("UTF-8 interpretation of input"):
                        st.code((data.get("replay") or {})["input_utf8"], language="json")
            rr1, rr2 = st.columns(2)
            rr1.metric("Error reproduced", "Yes" if data.get("reproduced") else "Not confirmed")
            rr2.metric("Fixed replay", "Passed" if data.get("fixed_replay_ok") else "Not confirmed")
            excerpt = log_excerpt(rows.get("buggy", {}).get("log"))
            if excerpt:
                st.markdown("**Diagnostic summary**")
                st.code(excerpt, language="text")
            full_log(rows.get("buggy", {}).get("log"), "Full buggy log")
            full_log(rows.get("fixed", {}).get("log"), "Full fixed log")
            full_log(data.get("replay_log"), "Replay report")
            if data.get("source_file"):
                st.caption(f"Target source: {data['source_file']}")
    with tabs[3]:
        st.markdown("**Paper A · Technical model**")
        st.write(m["phase"])
        st.markdown("**Paper B · Developer challenge taxonomy**")
        st.write(m["challenge"])
        st.caption("The Paper B categories are conceptual links to laboratory activities, not measured frequencies or a reproduction of the authors’ developer study.")

elif page == "Run lab":
    st.header("Local experiment runner")
    st.caption("Run only the project’s four known experiments. The dashboard does not execute arbitrary commands or accept custom scripts.")
    run_mode = st.radio("Execution mode", options=["Quick verification", "Fuzzing campaign"], horizontal=True)
    n = st.selectbox('Target', list(META), index=list(META).index(st.session_state.get("selected_run_target", 1)) if st.session_state.get("selected_run_target", 1) in META else 0, format_func=lambda k: f"Experiment {k} — {META[k]['title']}", disabled=(run_mode == "Quick verification"))
    if run_mode == "Fuzzing campaign":
        left, right = st.columns(2)
        limit = left.selectbox("Maximum fuzz runs per version", list(ALLOWED_RUNS), index=0)
        seed = right.selectbox("Reproducibility seed", list(ALLOWED_SEEDS), index=0)
        st.info("The runner executes buggy and fixed variants, then attempts replay. On Windows it calls the configured WSL/Ubuntu environment; Atheris and Clang must be installed there. A new run is not guaranteed to find a defect within the limit.")
    else:
        limit, seed = 1000, 1
        st.info("Runs the deterministic checks for the two updated Python targets. This is not a full fuzzing campaign and does not verify C++ sanitizer runs.")
    consent = st.checkbox("I understand that this will execute local test code and update experiment result files.")
    if st.button("Run selected check" if run_mode == "Quick verification" else f"Run experiment {n}", type="primary", disabled=not consent):
        with st.status("Running local checks...", expanded=True) as status:
            record = run_experiment(None if run_mode == "Quick verification" else n,
                                    'quick' if run_mode == "Quick verification" else 'fuzz', limit, seed)
            if record['success']:
                status.update(label='Execution completed', state='complete', expanded=False)
            else:
                status.update(label='Execution needs attention', state='error', expanded=True)
        st.session_state['last_run_id'] = record['id']
        if record['success']:
            st.success('The runner completed. See the saved log and any new result snapshot below.')
        else:
            st.error(record.get('error') or 'The script exited without passing its required checks; see log below.')
    st.subheader('Execution history')
    histories = get_history()
    if histories:
        view = pd.DataFrame([{'UTC': x['started_utc'][:19], 'Target': f"Experiment {x['experiment']}" if x['experiment'] else 'Python checks',
                              'Mode': x['mode'], 'Runs limit': x['runs'], 'Seed': x['seed'],
                              'Runner': 'Passed' if x['success'] else 'Failed', 'Fuzz evidence': x.get('evidence_status') or '—', 'Run ID': x['id']} for x in histories[:40]])
        st.dataframe(view, hide_index=True, use_container_width=True)
        choice_id = st.selectbox('Inspect a recorded execution', [x['id'] for x in histories], format_func=lambda x: f"{x[:16]}  ·  {next((str(r.get('experiment') or 'checks') for r in histories if r['id']==x), '')}")
        picked = next(r for r in histories if r['id'] == choice_id)
        st.caption(f"Result: {'passed' if picked['success'] else 'did not pass'} · {picked.get('source')} · {picked['started_utc']}")
        log_file = safe_path(picked.get('log'))
        if log_file:
            with st.expander('Execution output', expanded=not picked['success']):
                st.code(log_file.read_text(encoding='utf-8', errors='replace')[-12000:], language='text')
        recorded = snapshot(picked)
        if recorded:
            v = versions(recorded)
            aa, bb = st.columns(2)
            aa.metric('Buggy runs to report', v.get('buggy', {}).get('runs') or '—')
            bb.metric('Fixed runs', v.get('fixed', {}).get('runs') or '—')
            st.caption(f"Evidence: {recorded.get('status')} · Replay: {recorded.get('reproduced')} · Fixed replay: {recorded.get('fixed_replay_ok')}")
        matching = [r for r in histories if r['mode'] == 'fuzz' and r['experiment'] == picked.get('experiment') and snapshot(r) and verified(snapshot(r))]
        if len(matching) > 1:
            points=[]
            for rec in reversed(matching):
                evidence=snapshot(rec)
                points.append({'Run': rec['id'][:15], 'Runs to reported issue': versions(evidence).get('buggy',{}).get('runs')})
            st.markdown('**Repeated runs of the same target**')
            st.line_chart(pd.DataFrame(points).set_index('Run'))
            st.caption('Exploratory run-to-run variation for this target only. Different targets or fuzzing tools are not compared.')
    else:
        st.caption('No local executions have been launched from this dashboard yet. Archived JSON evidence remains available under Overview and Explore experiments.')

else:
    st.header("Research connection · Paper A and Paper B")
    st.caption("Independent synthesis from the original journal papers: technical stages, documented challenges, and evidence from our controlled lab.")
    research_comparison()
    st.markdown("### Experiments as examples, not a benchmark")
    st.dataframe(pd.DataFrame([{"Experiment": f"{n:02d} · {m['title']}",
                                "Paper A · selected technical activity": m["phase"],
                                "Paper B · related concern": m["challenge"]}
                               for n, m in META.items()]), hide_index=True, use_container_width=True)
    st.info("The experiments demonstrate selected elements of the fuzzing model. They do not verify the frequency of developer challenges, and results from different targets must not be used to rank tools or languages.")
    st.markdown("**Original scientific sources**")
    st.markdown("[1] V. J. M. Manès et al., *The Art, Science, and Engineering of Fuzzing: A Survey*, IEEE TSE, 2021. [Algorithm 1 / paper](https://arxiv.org/pdf/1812.00140)")
    st.markdown("[2] O. Nourry et al., *The Human Side of Fuzzing: Challenges Faced by Developers During Fuzzing Activities*, ACM TOSEM, online 2023 / volume 2024. [Paper / Fig. 2](https://www.inf.usi.ch/lanza/PUBS/J/Nour2024a.pdf)")

st.divider()
st.caption("Fuzzing Lab · Interactive local dashboard and controlled run archive · The deliberately faulty targets are educational examples, not industrial benchmarks.")
