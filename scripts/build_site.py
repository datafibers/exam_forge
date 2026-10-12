#!/usr/bin/env python3
"""Generate a standalone bilingual, multi-theme, progressive adaptive study website from validated question JSON and exam profile."""
import argparse, html, json, sys
from pathlib import Path
from validate_bank import validate

def get_args():
    p = argparse.ArgumentParser(description="Build offline adaptive study website.")
    p.add_argument('bank', help="Path to questions.json")
    p.add_argument('--profile', help="Path to optional exam_profile.json", default=None)
    p.add_argument('--out', default='practice.html', help="Output HTML file path")
    p.add_argument('--title', default=None, help="Override site/exam title")
    p.add_argument('--pass-score', type=int, default=None, help="Override passing score percentage (0-100)")
    p.add_argument('--mins', type=int, default=None, help="Override mock duration minutes")
    p.add_argument('--url', default=None, help="Override official URL")
    return p.parse_args()

def generate_logo_svg(monogram="EXAM"):
    mono = (monogram or "EXAM")[:4].upper()
    font_size = "19" if len(mono) > 3 else "22"
    return f'''<svg class="exam-crest" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="crestGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="var(--accent-alt)" stop-opacity="0.6"/>
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="46" fill="var(--panel-bg)" stroke="url(#crestGrad)" stroke-width="2.5"/>
  <circle cx="50" cy="50" r="40" fill="none" stroke="var(--accent)" stroke-width="1" stroke-dasharray="3,3" opacity="0.6"/>
  <polygon points="50,14 80,34 80,68 50,86 20,68 20,34" fill="none" stroke="var(--accent)" stroke-width="1.5" opacity="0.4"/>
  <path d="M 30,38 Q 50,28 70,38" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>
  <path d="M 30,62 Q 50,72 70,62" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>
  <text x="50" y="55" font-family="system-ui, -apple-system, sans-serif" font-weight="900" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" fill="var(--text-main)" letter-spacing="-0.5">{mono}</text>
  <polygon points="50,22 53,28 59,28 54,32 56,38 50,34 44,38 46,32 41,28 47,28" fill="var(--accent)"/>
</svg>'''

HTML_PAGE = r'''<!doctype html>
<html lang="en" data-theme="__DEFAULT_THEME__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__EXAM_TITLE__ — Adaptive Practice Engine</title>
<style>
/* ================= THEME DEFINITIONS ================= */
:root[data-theme="cyber"] {
  --bg-main: #07101e;
  --bg-gradient: radial-gradient(ellipse at 8% 0%, #17325c 0%, transparent 50%), radial-gradient(ellipse at 92% 100%, #0e2942 0%, #07101e 60%);
  --panel-bg: rgba(16, 32, 58, 0.9);
  --panel-border: #24426b;
  --panel-shadow: 0 16px 40px rgba(0, 4, 15, 0.45);
  --accent: #64e8d3;
  --accent-alt: #4eb6ed;
  --accent-btn-text: #051424;
  --text-main: #e8f2ff;
  --text-muted: #9ab4d6;
  --chip-bg: #153352;
  --chip-border: #315882;
  --opt-bg: #132742;
  --opt-border: #29486e;
  --opt-hover: #5ecad4;
  --opt-sel: #1b4b69;
  --opt-cor: #14493a;
  --opt-cor-b: #3edca2;
  --opt-wro: #59253c;
  --opt-wro-b: #ff7f7f;
  --feedback-bg: #12374e;
  --code-bg: #091525;
  --code-text: #a7e2ff;
  --code-border: #1e395b;
}

:root[data-theme="light"] {
  --bg-main: #f8fafc;
  --bg-gradient: radial-gradient(ellipse at 5% 0%, #e2ecfa 0%, transparent 55%), #f8fafc;
  --panel-bg: rgba(255, 255, 255, 0.96);
  --panel-border: #cbd5e1;
  --panel-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
  --accent: #0f766e;
  --accent-alt: #0284c7;
  --accent-btn-text: #ffffff;
  --text-main: #0f172a;
  --text-muted: #475569;
  --chip-bg: #f1f5f9;
  --chip-border: #cbd5e1;
  --opt-bg: #ffffff;
  --opt-border: #cbd5e1;
  --opt-hover: #0f766e;
  --opt-sel: #e0f2fe;
  --opt-cor: #ecfdf5;
  --opt-cor-b: #10b981;
  --opt-wro: #fef2f2;
  --opt-wro-b: #ef4444;
  --feedback-bg: #f0fdf4;
  --code-bg: #f1f5f9;
  --code-text: #0f172a;
  --code-border: #cbd5e1;
}

:root[data-theme="navy"] {
  --bg-main: #0a1329;
  --bg-gradient: radial-gradient(ellipse at 10% 5%, #182a52 0%, transparent 50%), #0a1329;
  --panel-bg: rgba(17, 30, 61, 0.92);
  --panel-border: #2c4780;
  --panel-shadow: 0 16px 45px rgba(0, 0, 0, 0.5);
  --accent: #f59e0b;
  --accent-alt: #fbbf24;
  --accent-btn-text: #111e3d;
  --text-main: #f0f4ff;
  --text-muted: #a6b7db;
  --chip-bg: #1b2f5b;
  --chip-border: #3b5a9b;
  --opt-bg: #14244a;
  --opt-border: #2b457c;
  --opt-hover: #f59e0b;
  --opt-sel: #284277;
  --opt-cor: #14493d;
  --opt-cor-b: #10b981;
  --opt-wro: #59253d;
  --opt-wro-b: #f87171;
  --feedback-bg: #17375a;
  --code-bg: #0d1936;
  --code-text: #fed7aa;
  --code-border: #2a4175;
}

:root[data-theme="forest"] {
  --bg-main: #071612;
  --bg-gradient: radial-gradient(ellipse at 15% 0%, #13392f 0%, transparent 50%), #071612;
  --panel-bg: rgba(13, 37, 30, 0.92);
  --panel-border: #215545;
  --panel-shadow: 0 16px 45px rgba(0, 0, 0, 0.5);
  --accent: #34d399;
  --accent-alt: #10b981;
  --accent-btn-text: #051a14;
  --text-main: #e8f9f2;
  --text-muted: #8ebfae;
  --chip-bg: #133c30;
  --chip-border: #246552;
  --opt-bg: #11342a;
  --opt-border: #235848;
  --opt-hover: #34d399;
  --opt-sel: #1b5343;
  --opt-cor: #144a33;
  --opt-cor-b: #34d399;
  --opt-wro: #4d232a;
  --opt-wro-b: #f87171;
  --feedback-bg: #144336;
  --code-bg: #091f19;
  --code-text: #a7f3d0;
  --code-border: #1a4d3e;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--text-main);
  background: var(--bg-gradient);
  min-height: 100vh;
  line-height: 1.5;
  transition: background 0.3s ease, color 0.3s ease;
}

.shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* ================= HEADER & CREST ================= */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--panel-border);
  flex-wrap: wrap;
}
.identity {
  display: flex;
  align-items: center;
  gap: 16px;
}
.exam-crest {
  width: 58px;
  height: 58px;
  flex-shrink: 0;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.25));
}
.title-group h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.title-group p {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-muted);
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.badge-link {
  color: var(--accent);
  text-decoration: none;
  border: 1px solid var(--panel-border);
  background: var(--chip-bg);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  transition: all 0.2s;
}
.badge-link:hover {
  border-color: var(--accent);
  text-decoration: underline;
}
.top-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

button, select {
  font: inherit;
  cursor: pointer;
}
.btn {
  background: linear-gradient(135deg, var(--accent), var(--accent-alt));
  color: var(--accent-btn-text);
  font-weight: 750;
  padding: 10px 18px;
  border: 0;
  border-radius: 12px;
  transition: transform 0.15s, opacity 0.15s, box-shadow 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.2);
}
.btn:hover { transform: translateY(-1px); opacity: 0.94; }
.btn:active { transform: translateY(0); }
.btn.secondary {
  background: var(--opt-bg);
  color: var(--text-main);
  border: 1px solid var(--panel-border);
  box-shadow: none;
}
.btn.secondary:hover { border-color: var(--accent); }
.btn.sm { padding: 6px 12px; font-size: 12px; border-radius: 8px; }
.btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }

.select-pill {
  background: var(--opt-bg);
  color: var(--text-main);
  border: 1px solid var(--panel-border);
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px;
}

/* ================= 5-STAGE PROGRESSIVE ROADMAP ================= */
.roadmap-container {
  margin: 22px 0 28px;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 16px 20px;
  box-shadow: var(--panel-shadow);
}
.roadmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.roadmap-title {
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--accent);
}
.roadmap-target {
  font-size: 12px;
  color: var(--text-muted);
}
.stages-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}
.stage-card {
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}
.stage-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}
.stage-card.active {
  border-color: var(--accent);
  background: var(--opt-sel);
  box-shadow: 0 0 12px rgba(100, 232, 211, 0.2);
}
.stage-idx {
  font-size: 10px;
  font-weight: 800;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.stage-name {
  font-size: 13px;
  font-weight: 700;
  margin: 2px 0 4px;
}
.stage-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ================= HERO & DASHBOARD ================= */
.hero-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.panel {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--panel-shadow);
  backdrop-filter: blur(12px);
}
.panel-eyebrow {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 6px;
}
.hero-title {
  font-size: clamp(24px, 3.6vw, 34px);
  font-weight: 850;
  letter-spacing: -1.2px;
  line-height: 1.15;
  margin: 8px 0 14px;
}
.stats-line {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 16px 0;
}
.stat-box {
  background: var(--opt-bg);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  padding: 12px 14px;
  text-align: center;
}
.stat-val {
  font-size: 24px;
  font-weight: 850;
  display: block;
}
.stat-lbl {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.pass-target-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
}

/* ================= MAIN CONTENT LAYOUT ================= */
.content-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}
.sidebar-panel {
  align-self: start;
}
.topic-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--opt-bg);
  border: 1px solid var(--panel-border);
  margin-top: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.topic-item:hover {
  border-color: var(--accent);
  background: var(--opt-sel);
}
.topic-rate {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent);
}

/* ================= PRACTICE CARD & QUESTION ================= */
.work-panel {
  min-height: 480px;
}
.q-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 10px;
}
.progress-bar-wrap {
  height: 8px;
  background: var(--panel-border);
  border-radius: 6px;
  overflow: hidden;
  margin: 12px 0 18px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-alt));
  transition: width 0.25s ease;
}
.chips-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.chip {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
  color: var(--text-main);
  font-weight: 600;
}
.chip.qtype {
  color: var(--accent);
}

.q-stem {
  font-size: 19px;
  font-weight: 650;
  line-height: 1.55;
  margin: 18px 0;
}

/* MATH FORMULAS & CODE BLOCKS */
.math-inline {
  display: inline-block;
  font-family: "Cambria Math", "Latin Modern Math", KaTeX_Math, STIX, "Times New Roman", serif;
  font-style: italic;
  padding: 0 3px;
  color: var(--accent);
  letter-spacing: 0.2px;
}
.math-block {
  display: block;
  text-align: center;
  font-family: "Cambria Math", "Latin Modern Math", KaTeX_Math, STIX, "Times New Roman", serif;
  font-style: italic;
  padding: 12px 0;
  font-size: 1.15em;
  color: var(--accent);
}
.math-frac {
  display: inline-flex;
  flex-direction: column;
  vertical-align: middle;
  text-align: center;
  font-size: 0.9em;
  padding: 0 2px;
}
.math-frac .num {
  border-bottom: 1.5px solid currentColor;
  padding-bottom: 1px;
}
.math-frac .denom {
  padding-top: 1px;
}

pre.code-block {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  color: var(--code-text);
  border-radius: 10px;
  padding: 12px 16px;
  overflow-x: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.45;
  margin: 14px 0;
}
code.code-inline {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  color: var(--code-text);
  padding: 2px 6px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.9em;
}

/* OPTIONS */
.opt-btn {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  text-align: left;
  background: var(--opt-bg);
  border: 1.5px solid var(--opt-border);
  color: var(--text-main);
  padding: 14px 18px;
  border-radius: 14px;
  margin: 10px 0;
  font-size: 15px;
  line-height: 1.45;
  transition: all 0.15s;
}
.opt-btn:hover:not(:disabled) {
  border-color: var(--opt-hover);
  background: var(--chip-bg);
}
.opt-btn.selected {
  border-color: var(--accent);
  background: var(--opt-sel);
  box-shadow: 0 0 10px rgba(100, 232, 211, 0.15);
}
.opt-btn.correct {
  border-color: var(--opt-cor-b) !important;
  background: var(--opt-cor) !important;
}
.opt-btn.wrong {
  border-color: var(--opt-wro-b) !important;
  background: var(--opt-wro) !important;
}
.opt-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--chip-bg);
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
}
.opt-indicator {
  font-size: 15px;
  margin-right: 2px;
}

/* QUESTION NAVIGATOR GRID (MOCK MODE) */
.q-nav-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 14px 0 20px;
}
.q-nav-dot {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--panel-border);
  background: var(--opt-bg);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.q-nav-dot.answered {
  background: var(--chip-bg);
  color: var(--accent);
  border-color: var(--accent);
}
.q-nav-dot.current {
  outline: 2px solid var(--accent);
  color: #fff;
}

.feedback-card {
  margin-top: 22px;
  background: var(--feedback-bg);
  border: 1.5px solid var(--panel-border);
  border-radius: 16px;
  padding: 20px;
  animation: fadeIn 0.25s ease-out;
}
.feedback-card h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: var(--accent);
}
.why-wrong-item {
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.4;
  padding-left: 12px;
  border-left: 2px solid var(--panel-border);
  color: var(--text-muted);
}
.why-wrong-item strong {
  color: var(--text-main);
}

/* TIMED CLOCK */
.timer-pill {
  background: #ef4444;
  color: #fff;
  font-weight: 850;
  font-size: 14px;
  padding: 5px 12px;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.35);
}

/* SCORECARD & RESULT */
.result-banner {
  text-align: center;
  padding: 24px 10px;
}
.result-score {
  font-size: 44px;
  font-weight: 900;
  letter-spacing: -1.5px;
  margin: 10px 0;
}
.verdict-stamp {
  display: inline-block;
  padding: 8px 24px;
  border-radius: 30px;
  font-weight: 900;
  font-size: 15px;
  letter-spacing: 0.5px;
  margin-bottom: 20px;
}
.verdict-stamp.pass {
  background: #10b981;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
}
.verdict-stamp.fail {
  background: #ef4444;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
}

.table-matrix {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  text-align: left;
  font-size: 13px;
}
.table-matrix th, .table-matrix td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--panel-border);
}
.table-matrix th {
  color: var(--text-muted);
  text-transform: uppercase;
  font-size: 11px;
}

.footer-bar {
  margin-top: 36px;
  padding-top: 20px;
  border-top: 1px solid var(--panel-border);
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .hero-layout, .content-grid { grid-template-columns: 1fr; }
  .stages-grid { grid-template-columns: repeat(2, 1fr); }
  .shell { padding: 16px; }
  .q-stem { font-size: 17px; }
}
@media (max-width: 600px) {
  .stages-grid { grid-template-columns: 1fr; }
  .stats-line { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="shell">

  <!-- TOP HEADER & BRAND -->
  <header class="header-bar">
    <div class="identity">
      __LOGO_SVG__
      <div class="title-group">
        <h1 id="examTitle">__EXAM_TITLE__</h1>
        <p>
          <span class="pass-target-tag" id="headerBenchmarkTag">🎯 Pass Benchmark: __PASS_BENCHMARK__%</span>
          <span id="headerDurationTag">⏱ Duration: __MOCK_DURATION__ mins</span>
          __OFFICIAL_LINK_HTML__
        </p>
      </div>
    </div>
    <div class="top-controls">
      <!-- Theme Switcher -->
      <select id="themeSelect" class="select-pill" title="Choose color theme">
        <option value="cyber">⚡ Cyber Dark</option>
        <option value="light">☀️ Academic Light</option>
        <option value="navy">🌌 Midnight Navy</option>
        <option value="forest">🌲 Forest Green</option>
      </select>
      <!-- Option Shuffle Toggle -->
      <button id="shuffleToggle" class="btn secondary sm" type="button" title="Randomize choice order">🎲 Shuffle: ON</button>
      <!-- Language Switcher -->
      <button id="langBtn" class="btn secondary sm" type="button">🇨🇳 中文</button>
    </div>
  </header>

  <!-- 5-STAGE PROGRESSIVE ROADMAP -->
  <section class="roadmap-container">
    <div class="roadmap-header">
      <span class="roadmap-title" id="lblRoadmapTitle">5-Stage Mastery Journey (循序渐进备考体系)</span>
      <span class="roadmap-target" id="lblRoadmapGoal">Step-by-step from diagnostic to exam-ready certification</span>
    </div>
    <div class="stages-grid" id="stagesGrid"></div>
  </section>

  <!-- HERO ACTIONS & LEARNING SNAPSHOT -->
  <section class="hero-layout">
    <div class="panel">
      <div class="panel-eyebrow" id="lblHeroEyebrow">Autonomous Adaptive Engine</div>
      <h2 class="hero-title" id="lblHeroTitle">Master Concepts. Pass with Confidence.</h2>
      <p id="lblHeroDesc" style="color:var(--text-muted);margin:0 0 20px;">
        __EXAM_DESC__
      </p>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn" id="btnStartPractice">▶ Start Practice</button>
        <button class="btn secondary" id="btnTimedMock">⏱ Timed Mock (__MOCK_DURATION__m)</button>
        <button class="btn secondary" id="btnAdaptivePlans">✦ Adaptive Tests</button>
      </div>
    </div>

    <div class="panel">
      <div class="panel-eyebrow" id="lblSnapshotEyebrow">Your Study Snapshot</div>
      <div class="stats-line">
        <div class="stat-box">
          <span class="stat-val" id="statBank">0</span>
          <span class="stat-lbl" id="lblStatBank">Bank Size</span>
        </div>
        <div class="stat-box">
          <span class="stat-val" id="statAttempts">0</span>
          <span class="stat-lbl" id="lblStatAttempts">Answered</span>
        </div>
        <div class="stat-box">
          <span class="stat-val" id="statAccuracy">—</span>
          <span class="stat-lbl" id="lblStatAccuracy">Accuracy</span>
        </div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;flex-wrap:wrap;gap:8px;">
        <span style="font-size:12px;color:var(--text-muted);" id="lblPrivacyNote">Local progress · Safe & offline</span>
        <div style="display:flex;gap:8px;">
          <button class="btn secondary sm" id="btnExport">Export JSON</button>
          <button class="btn secondary sm" id="btnImport">Import</button>
          <input type="file" id="fileInput" accept="application/json" hidden>
        </div>
      </div>
    </div>
  </section>

  <!-- STUDY WORKSPACE -->
  <div class="content-grid">
    <!-- LEFT SIDEBAR: TOPICS & FILTERS -->
    <aside class="panel sidebar-panel">
      <div class="panel-eyebrow" id="lblTopicsHeader">Syllabus Domains</div>
      <div id="topicList"></div>
      
      <hr style="border:0;border-top:1px solid var(--panel-border);margin:20px 0;">
      
      <label class="panel-eyebrow" id="lblFilterTopic">Topic Filter</label>
      <div style="margin:6px 0 14px;">
        <select id="selTopic" class="select-pill" style="width:100%;"></select>
      </div>

      <label class="panel-eyebrow" id="lblBatchSize">Session Size</label>
      <div style="margin:6px 0 14px;">
        <select id="selSize" class="select-pill" style="width:100%;">
          <option value="10">10 Questions</option>
          <option value="20" selected>20 Questions</option>
          <option value="30">30 Questions</option>
          <option value="50">50 Questions</option>
          <option value="100">100 Questions</option>
        </select>
      </div>

      <button class="btn secondary" id="btnReviewMistakes" style="width:100%;margin-top:4px;">
        🎯 Mistake Killer (<span id="mistakeBadge">0</span>)
      </button>
    </aside>

    <!-- RIGHT: INTERACTIVE WORK AREA -->
    <main class="panel work-panel" id="workArea">
      <div class="panel-eyebrow">READY</div>
      <h2 style="margin:10px 0 6px;" id="lblWelcome">Select a study mode or stage above</h2>
      <p style="color:var(--text-muted);" id="lblWelcomeHelp">
        Begin with Stage 1 Diagnostic or choose a specific topic from the sidebar. You can review distractor explanations on every question.
      </p>
    </main>
  </div>

  <footer class="footer-bar">
    <span>✦ Exam Forge Adaptive Platform · Zero-dependency Offline Engine</span>
    <span id="lblCopyrightNotice">Original & licensed practice items. Built with exam-practice-builder skill.</span>
  </footer>

</div>

<!-- SCRIPT LOGIC -->
<script>
const BANK = __BANK_JSON__;
const META = __META_JSON__;
const STORAGE_KEY = 'exam_forge_v4:' + (META.code || document.title);

let state = {
  lang: 'en',
  theme: META.default_theme || 'cyber',
  shuffleChoices: true,
  currentStage: 'diagnostic',
  records: {},
  mistakes: [],
  bookmarks: []
};

// Load persisted state
try {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    const parsed = JSON.parse(raw);
    state = Object.assign({}, state, parsed);
  }
} catch (e) {}

function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) {}
}

// UI DICTIONARY
const I18N = {
  en: {
    heroTitle: 'Master Concepts. Pass with Confidence.',
    heroDesc: META.description || 'Bilingual adaptive practice with verified reasoning and realistic mocks.',
    startPractice: '▶ Start Practice',
    timedMock: '⏱ Timed Mock (' + META.mock_duration_mins + 'm)',
    adaptivePlans: '✦ Adaptive Tests',
    bankSize: 'Bank Size',
    answered: 'Answered',
    accuracy: 'Accuracy',
    privacy: 'Local progress · Safe & offline',
    export: 'Export JSON',
    import: 'Import',
    mistakeKiller: '🎯 Mistake Killer',
    checkAnswer: 'Check Answer',
    next: 'Next Question →',
    prev: '← Previous Question',
    submitExam: 'Submit Exam ✓',
    finish: 'Finish Session',
    explanation: 'Detailed Concept Explanation',
    distractors: 'Why Distractors Fail (错因分析)',
    selectMulti: 'Multiple Choice: Select all correct options, then click Check Answer.',
    verdictPassed: 'BENCHMARK PASSED 🏆',
    verdictFailed: 'BENCHMARK NOT YET MET ⚠️',
    timeRemaining: 'Remaining',
    backHome: 'Return to Hub',
    diagnosticStage: 'Stage 1: Diagnostic Baseline',
    drillingStage: 'Stage 2: Topic Drilling',
    mistakesStage: 'Stage 3: Mistake Elimination',
    mockStage: 'Stage 4: Real-world Timed Mock',
    sprintStage: 'Stage 5: Final Adaptive Sprint',
    roadmapTitle: '5-Stage Mastery Journey (循序渐进备考体系)',
    roadmapGoal: 'Step-by-step from diagnostic to exam-ready certification',
    allTopics: 'All Domains',
    importedOk: 'Learning progress imported successfully.',
    importedBad: 'Invalid progress data file.',
    noMistakes: 'No saved mistakes! Great job, continue practicing.',
    passBenchmark: 'Pass Benchmark: ' + META.passing_score + '%',
    durationTag: 'Duration: ' + META.mock_duration_mins + ' mins',
    confirmExit: 'An active session is in progress. Are you sure you want to exit and abandon current progress?',
    confirmSubmitUnfinished: 'You have unfinished questions. Are you sure you want to submit now?',
    scoreMatrixHeader: 'Performance Breakdown by Domain',
    reviewHeader: 'Comprehensive Post-Mock Review',
    yourChoice: 'Your Selection',
    correctChoice: 'Correct Answer',
    addToMistakes: 'Add to Mistakes',
    inMistakes: 'In Mistake Bank'
  },
  zh: {
    heroTitle: '更高效掌握考点，更从容通过考试。',
    heroDesc: META.description || '中英双语解析、全真模拟、薄弱点靶向攻坚，数据仅保留于本地。',
    startPractice: '▶ 开始综合练习',
    timedMock: '⏱ 限时全真模考 (' + META.mock_duration_mins + '分钟)',
    adaptivePlans: '✦ 自适应强化套卷',
    bankSize: '题库题量',
    answered: '已答题次',
    accuracy: '平均正确率',
    privacy: '进度仅保存在本设备 · 离线安全',
    export: '导出学习记录',
    import: '导入记录',
    mistakeKiller: '🎯 错题攻坚清零',
    checkAnswer: '提交并校验',
    next: '下一题 →',
    prev: '← 上一题',
    submitExam: '交卷并评估 ✓',
    finish: '完成练习',
    explanation: '核心考点详细解析',
    distractors: '干扰项错因剖析 (Why Wrong)',
    selectMulti: '多选题：请选择所有符合题意的选项，然后点击提交。',
    verdictPassed: '考核达标 🏆 (达到合格线)',
    verdictFailed: '尚未达标 ⚠️ (距离及格线仍需加强)',
    timeRemaining: '剩余时间',
    backHome: '返回主面板',
    diagnosticStage: '阶段一：摸底诊断',
    drillingStage: '阶段二：专题精练',
    mistakesStage: '阶段三：错题清零',
    mockStage: '阶段四：全真模考',
    sprintStage: '阶段五：冲刺达标',
    roadmapTitle: '循序渐进五阶备考体系',
    roadmapGoal: '从初始诊断摸底、分项精练，到全真模考达标认证',
    allTopics: '全部知识模块',
    importedOk: '学习进度导入成功！',
    importedBad: '导入文件格式不合法。',
    noMistakes: '当前暂无错题记录！非常棒，请继续保持。',
    passBenchmark: '及格达标线: ' + META.passing_score + '%',
    durationTag: '考试时长: ' + META.mock_duration_mins + ' 分钟',
    confirmExit: '当前测试正在进行中，确定要退出并放弃当前作答吗？',
    confirmSubmitUnfinished: '您还有尚未作答的题目，确定现在交卷吗？',
    scoreMatrixHeader: '各知识模块能力得分清单',
    reviewHeader: '考后全卷复盘与错因精讲',
    yourChoice: '您的作答',
    correctChoice: '正确答案',
    addToMistakes: '加入错题本',
    inMistakes: '已在错题本'
  }
};

const t = (k) => (I18N[state.lang] && I18N[state.lang][k]) || k;
const $ = (id) => document.getElementById(id);

// True Fisher-Yates shuffle
function shuffle(array) {
  const a = [...array];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* ================= LATEX & CODE FORMATTER ================= */
function renderRichText(text) {
  if (!text) return '';
  let escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Multiline code blocks
  escaped = escaped.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, function(m, lang, code) {
    return '<pre class="code-block"><code>' + code.trim() + '</code></pre>';
  });

  // Inline code
  escaped = escaped.replace(/`([^`]+)`/g, '<code class="code-inline">$1</code>');

  // Block math: \[ ... \] or $$ ... $$
  escaped = escaped.replace(/(?:\\\[([\s\S]+?)\\\]|\$\$([\s\S]+?)\$\$)/g, function(m, p1, p2) {
    return '<div class="math-block">' + formatMathString(p1 || p2) + '</div>';
  });

  // Protect escaped dollar signs: \$ -> &#36;
  escaped = escaped.replace(/\\\$/g, '&#36;');

  // Inline LaTeX \( ... \)
  escaped = escaped.replace(/\\\(([\s\S]+?)\\\)/g, function(m, formula) {
    return '<span class="math-inline">' + formatMathString(formula) + '</span>';
  });

  // Inline $...$ math: opening $ must not be followed by digit or whitespace
  escaped = escaped.replace(/\$([^\$\s\d][^\$\n]*?)\$/g, function(m, formula) {
    return '<span class="math-inline">' + formatMathString(formula) + '</span>';
  });

  // Newlines
  escaped = escaped.replace(/\n/g, '<br>');
  return escaped;
}

function formatMathString(f) {
  return f
    .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '<span class="math-frac"><span class="num">$1</span><span class="denom">$2</span></span>')
    .replace(/\\sqrt\{([^}]+)\}/g, '√($1)')
    .replace(/\\Delta/g, 'Δ')
    .replace(/\\alpha/g, 'α')
    .replace(/\\beta/g, 'β')
    .replace(/\\pi/g, 'π')
    .replace(/\\times/g, '×')
    .replace(/\\div/g, '÷')
    .replace(/\\pm/g, '±')
    .replace(/\\le/g, '≤')
    .replace(/\\ge/g, '≥')
    .replace(/\\neq/g, '≠')
    .replace(/\\in/g, '∈')
    .replace(/\^\{?([0-9a-zA-Z+\-]+)\}?/g, '<sup>$1</sup>')
    .replace(/_\{?([0-9a-zA-Z+\-]+)\}?/g, '<sub>$1</sub>');
}

/* ================= ADAPTIVE MASTERY ALGORITHM ================= */
function getUniqueTopics() {
  return [...new Set(BANK.map(q => q.topic))];
}

function getTopicStats(topic) {
  const qs = BANK.filter(q => q.topic === topic);
  let attempts = 0, correct = 0;
  qs.forEach(q => {
    const rec = state.records[q.id] || [];
    rec.forEach(v => { attempts++; if (v) correct++; });
  });
  const smoothed = (correct + 2) / (attempts + 4);
  const rawRate = attempts ? Math.round(correct / attempts * 100) : null;
  return { attempts, correct, smoothed, rawRate };
}

function computeQuestionWeight(q) {
  const rec = state.records[q.id] || [];
  const topStat = getTopicStats(q.topic);
  let w = 2.0;
  w += (1.0 - topStat.smoothed) * 3.0;
  if (rec.length > 0) {
    const lastResult = rec[rec.length - 1];
    w += (lastResult === false ? 3.0 : 0.2);
  } else {
    w += 2.0;
  }
  if (q.difficulty === 3) w *= 1.2;
  return w;
}

function getStratifiedSample(pool, n) {
  const byTopic = {};
  getUniqueTopics().forEach(tp => { byTopic[tp] = []; });
  pool.forEach(q => { if (byTopic[q.topic]) byTopic[q.topic].push(q); });

  const picked = [];
  const topics = Object.keys(byTopic);
  let idx = 0;
  while (picked.length < n && picked.length < pool.length) {
    const tp = topics[idx % topics.length];
    if (byTopic[tp] && byTopic[tp].length > 0) {
      picked.push(byTopic[tp].shift());
    }
    idx++;
  }
  return shuffle(picked);
}

function getAdaptiveSample(pool, n) {
  const mistakes = pool.filter(q => state.mistakes.includes(q.id));
  const unattempted = pool.filter(q => !(state.records[q.id] && state.records[q.id].length));
  const others = pool.filter(q => !state.mistakes.includes(q.id) && (state.records[q.id] && state.records[q.id].length));

  const countMistakes = Math.min(mistakes.length, Math.ceil(n * 0.6));
  const countUnattempted = Math.min(unattempted.length, Math.ceil(n * 0.25));
  const remaining = n - countMistakes - countUnattempted;

  const picked = [
    ...shuffle(mistakes).slice(0, countMistakes),
    ...shuffle(unattempted).slice(0, countUnattempted),
    ...shuffle(others).slice(0, remaining)
  ];

  if (picked.length < n) {
    const remainingPool = pool.filter(q => !picked.some(x => x.id === q.id));
    picked.push(...shuffle(remainingPool).slice(0, n - picked.length));
  }
  return shuffle(picked);
}

/* ================= SESSION RUNTIME ================= */
let activeSession = null;
let currentQuestionIndex = 0;
let sessionStartTime = 0;
let timerInterval = null;
let userAnswers = {}; // { question_index: selected_choice_index_or_array }
let questionOptionPermutations = {}; // cached randomized choice indices per question instance

function startSession(questions, isTimed, modeName) {
  if (!questions || !questions.length) {
    alert('No questions available for this selection.');
    return;
  }
  if (timerInterval) clearInterval(timerInterval);

  activeSession = {
    questions: questions,
    isTimed: isTimed,
    modeName: modeName || 'Practice',
    total: questions.length,
    isSubmitted: false
  };
  currentQuestionIndex = 0;
  userAnswers = {};
  questionOptionPermutations = {};
  sessionStartTime = Date.now();

  // Pre-generate choice permutations
  questions.forEach((q, idx) => {
    const rawLen = (state.lang === 'zh' ? q.choices_zh : q.choices_en).length;
    let indices = Array.from({ length: rawLen }, (_, i) => i);
    if (state.shuffleChoices && q.type !== 'boolean') {
      indices = shuffle(indices);
    }
    questionOptionPermutations[idx] = indices;
  });

  if (isTimed) {
    const mockMins = META.mock_duration_mins || 60;
    const mockTotal = META.mock_questions_count || questions.length;
    const totalSeconds = Math.max(60, Math.ceil(mockMins * 60 * (questions.length / Math.max(1, mockTotal))));
    timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
      const remaining = Math.max(0, totalSeconds - elapsed);
      const clock = $('activeClock');
      if (clock) {
        const m = Math.floor(remaining / 60);
        const s = remaining % 60;
        clock.textContent = m + ':' + (s < 10 ? '0' : '') + s;
      }
      if (remaining === 0) {
        clearInterval(timerInterval);
        finishTimedMock();
      }
    }, 1000);
  }

  renderQuestionView();
}

function renderQuestionView() {
  const work = $('workArea');
  work.innerHTML = '';
  if (!activeSession) return;

  const q = activeSession.questions[currentQuestionIndex];
  const qType = q.type || 'single';
  const isTimed = activeSession.isTimed;

  // Auto smooth scroll to work area
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Header row
  const header = document.createElement('div');
  header.className = 'q-header';
  
  const progressText = document.createElement('span');
  progressText.className = 'panel-eyebrow';
  progressText.textContent = (currentQuestionIndex + 1) + ' / ' + activeSession.total + ' · ' + activeSession.modeName;
  header.appendChild(progressText);

  if (isTimed) {
    const clockBadge = document.createElement('div');
    clockBadge.className = 'timer-pill';
    clockBadge.innerHTML = '⏱ <span id="activeClock">--:--</span>';
    header.appendChild(clockBadge);
  }
  work.appendChild(header);

  // Progress bar
  const barWrap = document.createElement('div');
  barWrap.className = 'progress-bar-wrap';
  const barFill = document.createElement('div');
  barFill.className = 'progress-fill';
  barFill.style.width = (((currentQuestionIndex + 1) / activeSession.total) * 100) + '%';
  barWrap.appendChild(barFill);
  work.appendChild(barWrap);

  // Mock Question Navigation Grid
  if (isTimed) {
    const navGrid = document.createElement('div');
    navGrid.className = 'q-nav-grid';
    activeSession.questions.forEach((_, idx) => {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'q-nav-dot' + (idx === currentQuestionIndex ? ' current' : '') + (userAnswers[idx] !== undefined ? ' answered' : '');
      dot.textContent = idx + 1;
      dot.onclick = () => {
        currentQuestionIndex = idx;
        renderQuestionView();
      };
      navGrid.appendChild(dot);
    });
    work.appendChild(navGrid);
  }

  // Chips
  const chips = document.createElement('div');
  chips.className = 'chips-row';
  chips.innerHTML = '<span class="chip">' + q.topic + '</span>' +
    '<span class="chip">' + '★'.repeat(q.difficulty) + ' Level ' + q.difficulty + '</span>' +
    '<span class="chip qtype">' + (qType === 'multiple' ? 'MULTIPLE CHOICE' : (qType === 'boolean' ? 'TRUE / FALSE' : 'SINGLE CHOICE')) + '</span>';
  work.appendChild(chips);

  // Question Stem
  const stem = document.createElement('div');
  stem.className = 'q-stem';
  const stemText = state.lang === 'zh' ? q.zh : q.en;
  stem.innerHTML = renderRichText(stemText);
  work.appendChild(stem);

  if (qType === 'multiple') {
    const tip = document.createElement('p');
    tip.style.fontSize = '12px';
    tip.style.color = 'var(--accent)';
    tip.style.margin = '-8px 0 14px';
    tip.textContent = t('selectMulti');
    work.appendChild(tip);
  }

  // Choices Handling
  const rawChoices = state.lang === 'zh' ? q.choices_zh : q.choices_en;
  const optionIndices = questionOptionPermutations[currentQuestionIndex] || rawChoices.map((_, i) => i);

  const choicesContainer = document.createElement('div');
  const optionButtons = [];

  let currentSelected = userAnswers[currentQuestionIndex];
  if (qType === 'multiple' && !Array.isArray(currentSelected)) {
    currentSelected = [];
  }

  optionIndices.forEach((origIdx, displayIdx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'opt-btn';
    const letter = String.fromCharCode(65 + displayIdx);
    const choiceText = rawChoices[origIdx];

    const isSelected = (qType === 'multiple')
      ? (Array.isArray(currentSelected) && currentSelected.includes(origIdx))
      : (currentSelected === origIdx);

    if (isSelected) btn.classList.add('selected');

    const indicator = (qType === 'multiple')
      ? (isSelected ? '☑' : '☐')
      : (isSelected ? '◉' : '○');

    btn.innerHTML = '<span class="opt-tag">' + letter + '</span>' +
      '<span class="opt-indicator">' + indicator + '</span>' +
      '<div style="flex:1;">' + renderRichText(choiceText) + '</div>';

    btn.onclick = () => {
      if (!isTimed && activeSession.isChecked) return;

      if (qType === 'single' || qType === 'boolean') {
        userAnswers[currentQuestionIndex] = origIdx;
        currentSelected = origIdx;
        optionButtons.forEach(b => {
          b.btn.classList.remove('selected');
          b.btn.querySelector('.opt-indicator').textContent = '○';
        });
        btn.classList.add('selected');
        btn.querySelector('.opt-indicator').textContent = '◉';
      } else if (qType === 'multiple') {
        if (!Array.isArray(userAnswers[currentQuestionIndex])) {
          userAnswers[currentQuestionIndex] = [];
        }
        const arr = userAnswers[currentQuestionIndex];
        const pos = arr.indexOf(origIdx);
        if (pos > -1) {
          arr.splice(pos, 1);
          btn.classList.remove('selected');
          btn.querySelector('.opt-indicator').textContent = '☐';
        } else {
          arr.push(origIdx);
          btn.classList.add('selected');
          btn.querySelector('.opt-indicator').textContent = '☑';
        }
      }
    };

    optionButtons.push({ btn: btn, origIdx: origIdx, displayIdx: displayIdx });
    choicesContainer.appendChild(btn);
  });
  work.appendChild(choicesContainer);

  // Footer Actions
  const actionsRow = document.createElement('div');
  actionsRow.style.marginTop = '24px';
  actionsRow.style.display = 'flex';
  actionsRow.style.gap = '10px';
  actionsRow.style.flexWrap = 'wrap';

  if (isTimed) {
    // Timed Mock Controls: Prev, Next, Submit
    if (currentQuestionIndex > 0) {
      const prevBtn = document.createElement('button');
      prevBtn.className = 'btn secondary';
      prevBtn.textContent = t('prev');
      prevBtn.onclick = () => {
        currentQuestionIndex--;
        renderQuestionView();
      };
      actionsRow.appendChild(prevBtn);
    }

    if (currentQuestionIndex < activeSession.total - 1) {
      const nextBtn = document.createElement('button');
      nextBtn.className = 'btn';
      nextBtn.textContent = t('next');
      nextBtn.onclick = () => {
        currentQuestionIndex++;
        renderQuestionView();
      };
      actionsRow.appendChild(nextBtn);
    }

    const submitExamBtn = document.createElement('button');
    submitExamBtn.className = 'btn secondary';
    submitExamBtn.textContent = t('submitExam');
    submitExamBtn.onclick = () => {
      const answeredCount = Object.keys(userAnswers).length;
      if (answeredCount < activeSession.total) {
        if (!confirm(t('confirmSubmitUnfinished'))) return;
      }
      finishTimedMock();
    };
    actionsRow.appendChild(submitExamBtn);

  } else {
    // Practice Mode Controls: Check Answer -> Next
    activeSession.isChecked = false;
    const checkBtn = document.createElement('button');
    checkBtn.className = 'btn';
    checkBtn.textContent = t('checkAnswer');

    checkBtn.onclick = () => {
      const selected = userAnswers[currentQuestionIndex];
      if (selected === undefined || (qType === 'multiple' && (!selected || selected.length === 0))) {
        alert(t('selectMulti'));
        return;
      }

      activeSession.isChecked = true;
      checkBtn.remove();

      // Check correctness
      let isCorrect = false;
      if (qType === 'single' || qType === 'boolean') {
        isCorrect = (selected === q.answer);
      } else if (qType === 'multiple') {
        const targetSet = new Set(q.answer);
        const userSet = new Set(selected);
        isCorrect = (targetSet.size === userSet.size && [...targetSet].every(x => userSet.has(x)));
      }

      // Record result
      state.records[q.id] = [...(state.records[q.id] || []), isCorrect].slice(-30);
      if (!isCorrect && !state.mistakes.includes(q.id)) {
        state.mistakes.push(q.id);
      } else if (isCorrect && state.mistakes.includes(q.id)) {
        state.mistakes = state.mistakes.filter(x => x !== q.id);
      }
      saveState();

      // Colorize options with accessible icons
      optionButtons.forEach(item => {
        item.btn.disabled = true;
        const isAns = (qType === 'multiple') ? q.answer.includes(item.origIdx) : (item.origIdx === q.answer);
        const isChosen = (qType === 'multiple') ? (selected && selected.includes(item.origIdx)) : (item.origIdx === selected);

        if (isAns) {
          item.btn.classList.add('correct');
          item.btn.querySelector('.opt-indicator').textContent = '✓';
        } else if (isChosen && !isAns) {
          item.btn.classList.add('wrong');
          item.btn.querySelector('.opt-indicator').textContent = '✗';
        }
      });

      // Show Feedback
      const feedback = document.createElement('div');
      feedback.className = 'feedback-card';
      const expText = state.lang === 'zh' ? q.explanation_zh : q.explanation_en;
      feedback.innerHTML = '<h3>✦ ' + t('explanation') + '</h3>' +
        '<p style="margin:0 0 12px;line-height:1.5;">' + renderRichText(expText) + '</p>';

      const distList = state.lang === 'zh' ? q.why_wrong_zh : q.why_wrong_en;
      if (Array.isArray(distList) && distList.length) {
        const distHeader = document.createElement('h4');
        distHeader.style.margin = '14px 0 6px';
        distHeader.style.fontSize = '14px';
        distHeader.style.color = 'var(--text-muted)';
        distHeader.textContent = t('distractors');
        feedback.appendChild(distHeader);

        optionButtons.forEach(optItem => {
          const note = distList[optItem.origIdx];
          if (note) {
            const div = document.createElement('div');
            div.className = 'why-wrong-item';
            const letter = String.fromCharCode(65 + optItem.displayIdx);
            div.innerHTML = '<strong>' + letter + '</strong>: ' + renderRichText(note);
            feedback.appendChild(div);
          }
        });
      }
      work.appendChild(feedback);

      // Next / Finish button
      const nextBtn = document.createElement('button');
      nextBtn.className = 'btn';
      const isLast = (currentQuestionIndex === activeSession.total - 1);
      nextBtn.textContent = isLast ? t('finish') : t('next');
      nextBtn.onclick = () => {
        currentQuestionIndex++;
        if (currentQuestionIndex >= activeSession.total) {
          finishPracticeSession();
        } else {
          renderQuestionView();
        }
      };
      actionsRow.appendChild(nextBtn);
      renderDashboardStats();
    };

    actionsRow.appendChild(checkBtn);
  }

  work.appendChild(actionsRow);
}

// Complete Timed Mock Examination
function finishTimedMock() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;

  const s = activeSession;
  if (!s) return;
  activeSession = null;

  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  let correctCount = 0;
  const topicStats = {};
  const questionLogs = [];

  s.questions.forEach((q, idx) => {
    const qType = q.type || 'single';
    const chosen = userAnswers[idx];
    let isCorrect = false;

    if (chosen !== undefined) {
      if (qType === 'single' || qType === 'boolean') {
        isCorrect = (chosen === q.answer);
      } else if (qType === 'multiple') {
        const targetSet = new Set(q.answer);
        const userSet = new Set(chosen);
        isCorrect = (targetSet.size === userSet.size && [...targetSet].every(x => userSet.has(x)));
      }
    }

    if (isCorrect) correctCount++;

    // Update records & mistakes
    state.records[q.id] = [...(state.records[q.id] || []), isCorrect].slice(-30);
    if (!isCorrect && !state.mistakes.includes(q.id)) {
      state.mistakes.push(q.id);
    } else if (isCorrect && state.mistakes.includes(q.id)) {
      state.mistakes = state.mistakes.filter(x => x !== q.id);
    }

    // Topic aggregation
    if (!topicStats[q.topic]) topicStats[q.topic] = { total: 0, correct: 0 };
    topicStats[q.topic].total++;
    if (isCorrect) topicStats[q.topic].correct++;

    questionLogs.push({ q: q, chosen: chosen, isCorrect: isCorrect, origPerm: questionOptionPermutations[idx] });
  });

  saveState();

  const accuracyPct = Math.round((correctCount / s.total) * 100);
  const isPassed = accuracyPct >= (META.passing_score || 75);

  const banner = document.createElement('div');
  banner.className = 'result-banner';
  banner.innerHTML = '<div class="panel-eyebrow">' + s.modeName.toUpperCase() + ' SCORECARD</div>' +
    '<div class="result-score">' + correctCount + ' / ' + s.total + ' (' + accuracyPct + '%)</div>' +
    '<div class="verdict-stamp ' + (isPassed ? 'pass' : 'fail') + '">' +
      (isPassed ? t('verdictPassed') : t('verdictFailed')) +
    '</div>';

  // Topic Matrix Table
  const tableHeader = document.createElement('h3');
  tableHeader.style.marginTop = '20px';
  tableHeader.textContent = t('scoreMatrixHeader');
  banner.appendChild(tableHeader);

  const table = document.createElement('table');
  table.className = 'table-matrix';
  table.innerHTML = '<thead><tr><th>Domain</th><th>Correct</th><th>Accuracy</th></tr></thead><tbody>' +
    Object.keys(topicStats).map(tp => {
      const st = topicStats[tp];
      const rate = Math.round((st.correct / st.total) * 100);
      return '<tr><td>' + tp + '</td><td>' + st.correct + ' / ' + st.total + '</td><td>' + rate + '%</td></tr>';
    }).join('') + '</tbody>';
  banner.appendChild(table);

  // Full Question Review
  const revHeader = document.createElement('h3');
  revHeader.style.marginTop = '28px';
  revHeader.textContent = t('reviewHeader');
  banner.appendChild(revHeader);

  questionLogs.forEach((item, idx) => {
    const q = item.q;
    const card = document.createElement('div');
    card.className = 'feedback-card';
    card.style.textAlign = 'left';

    const stemText = state.lang === 'zh' ? q.zh : q.en;
    const expText = state.lang === 'zh' ? q.explanation_zh : q.explanation_en;
    const choices = state.lang === 'zh' ? q.choices_zh : q.choices_en;

    card.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;">' +
      '<strong>#' + (idx + 1) + ' [' + q.topic + ']</strong>' +
      '<span class="chip ' + (item.isCorrect ? 'correct' : 'wrong') + '">' + (item.isCorrect ? '✓ Correct' : '✗ Incorrect') + '</span>' +
      '</div>' +
      '<p style="margin:8px 0;font-weight:600;">' + renderRichText(stemText) + '</p>' +
      '<div style="font-size:13px;color:var(--text-muted);">' +
      '<p><strong>' + t('explanation') + ':</strong> ' + renderRichText(expText) + '</p>' +
      '</div>';

    banner.appendChild(card);
  });

  const backBtn = document.createElement('button');
  backBtn.className = 'btn';
  backBtn.style.marginTop = '24px';
  backBtn.textContent = t('backHome');
  backBtn.onclick = () => { renderWelcomeState(); };
  banner.appendChild(backBtn);

  work.appendChild(banner);
  renderDashboardStats();
}

function finishPracticeSession() {
  const s = activeSession;
  activeSession = null;
  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const banner = document.createElement('div');
  banner.className = 'result-banner';
  banner.innerHTML = '<div class="panel-eyebrow">PRACTICE COMPLETED</div>' +
    '<h2>Session Finished</h2>' +
    '<p style="color:var(--text-muted);">Learning records and mistake bank updated on this device.</p>';

  const backBtn = document.createElement('button');
  backBtn.className = 'btn';
  backBtn.textContent = t('backHome');
  backBtn.onclick = () => { renderWelcomeState(); };
  banner.appendChild(backBtn);

  work.appendChild(banner);
  renderDashboardStats();
}

/* ================= 5-STAGE ROADMAP RENDERER ================= */
function renderRoadmap() {
  const grid = $('stagesGrid');
  grid.innerHTML = '';
  META.stages.forEach((stg, i) => {
    const card = document.createElement('div');
    card.className = 'stage-card ' + (state.currentStage === stg.id ? 'active' : '');
    const name = state.lang === 'zh' ? stg.name_zh : stg.name_en;
    const desc = state.lang === 'zh' ? stg.desc_zh : stg.desc_en;
    card.innerHTML = '<div class="stage-idx">Stage 0' + (i+1) + '</div>' +
      '<div class="stage-name">' + name + '</div>' +
      '<div class="stage-desc">' + desc + '</div>';
    card.onclick = () => {
      if (activeSession && !confirm(t('confirmExit'))) return;
      state.currentStage = stg.id;
      document.querySelectorAll('.stage-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      triggerStageAction(stg.id);
    };
    grid.appendChild(card);
  });
}

function triggerStageAction(stageId) {
  if (activeSession && !confirm(t('confirmExit'))) return;

  if (stageId === 'diagnostic') {
    const sample = getStratifiedSample(BANK, Math.min(20, BANK.length));
    startSession(sample, false, 'Diagnostic Baseline');
  } else if (stageId === 'drilling') {
    const top = $('selTopic').value;
    const pool = top === 'all' ? BANK : BANK.filter(q => q.topic === top);
    const size = Number($('selSize').value) || 20;
    startSession(shuffle(pool).slice(0, size), false, 'Topic Drilling');
  } else if (stageId === 'mistakes') {
    const pool = BANK.filter(q => state.mistakes.includes(q.id));
    if (!pool.length) {
      alert(t('noMistakes'));
      return;
    }
    startSession(shuffle(pool), false, 'Mistake Elimination');
  } else if (stageId === 'mock') {
    const count = META.mock_questions_count || 20;
    const pool = shuffle(BANK).slice(0, count);
    startSession(pool, true, 'Timed Simulation Mock');
  } else if (stageId === 'sprint') {
    renderAdaptivePlansHub();
  }
}

function renderAdaptivePlansHub() {
  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const n = 5;
  const size = Number($('selSize').value) || 20;
  const plans = Array.from({ length: n }, () => getAdaptiveSample(BANK, size));

  const eyebrow = document.createElement('div');
  eyebrow.className = 'panel-eyebrow';
  eyebrow.textContent = t('adaptivePlans');
  work.appendChild(eyebrow);

  const title = document.createElement('h2');
  title.style.margin = '8px 0 16px';
  title.textContent = state.lang === 'zh' ? '自适应冲刺规划（已生成 ' + n + ' 套个性化测试）' : 'Personalized Sprint Plans (' + n + ' Sets Ready)';
  work.appendChild(title);

  const desc = document.createElement('p');
  desc.style.color = 'var(--text-muted)';
  desc.textContent = state.lang === 'zh'
    ? '基于贝叶斯平滑算法动态配比：60% 历史薄弱考点 + 25% 未测试题目 + 15% 巩固复习。'
    : 'Engine-balanced ratio: 60% historically weak domains, 25% unattempted items, 15% retention review.';
  work.appendChild(desc);

  plans.forEach((plan, i) => {
    const row = document.createElement('div');
    row.className = 'topic-item';
    row.style.margin = '10px 0';
    row.innerHTML = '<div><strong>' + (state.lang === 'zh' ? '自适应测试' : 'Adaptive Test') + ' #' + (i+1) + '</strong>' +
      '<span style="color:var(--text-muted);font-size:12px;margin-left:8px;">' + plan.length + ' Questions</span></div>';
    const btn = document.createElement('button');
    btn.className = 'btn sm';
    btn.textContent = state.lang === 'zh' ? '开始此套测试 →' : 'Launch Test →';
    btn.onclick = () => { startSession(plan, false, 'Adaptive Test #' + (i+1)); };
    row.appendChild(btn);
    work.appendChild(row);
  });
}

/* ================= DASHBOARD & SIDEBAR STATS ================= */
function renderDashboardStats() {
  $('statBank').textContent = BANK.length;
  const attemptsFlat = Object.values(state.records).flat();
  $('statAttempts').textContent = attemptsFlat.length;
  if (attemptsFlat.length > 0) {
    const correctCount = attemptsFlat.filter(Boolean).length;
    $('statAccuracy').textContent = Math.round(correctCount / attemptsFlat.length * 100) + '%';
  } else {
    $('statAccuracy').textContent = '—';
  }
  $('mistakeBadge').textContent = state.mistakes.length;

  const list = $('topicList');
  list.innerHTML = '';
  getUniqueTopics().forEach(tp => {
    const stat = getTopicStats(tp);
    const item = document.createElement('div');
    item.className = 'topic-item';
    item.innerHTML = '<span>' + tp + '</span><span class="topic-rate">' + (stat.rawRate !== null ? stat.rawRate + '%' : '—') + '</span>';
    item.onclick = () => {
      if (activeSession && !confirm(t('confirmExit'))) return;
      $('selTopic').value = tp;
      const pool = BANK.filter(q => q.topic === tp);
      startSession(shuffle(pool).slice(0, Number($('selSize').value)), false, 'Topic: ' + tp);
    };
    list.appendChild(item);
  });

  const currentSel = $('selTopic').value;
  $('selTopic').innerHTML = '<option value="all">' + t('allTopics') + '</option>';
  getUniqueTopics().forEach(tp => {
    const opt = document.createElement('option');
    opt.value = tp;
    opt.textContent = tp;
    $('selTopic').appendChild(opt);
  });
  if (currentSel) $('selTopic').value = currentSel;
}

function renderWelcomeState() {
  const work = $('workArea');
  work.innerHTML = '<div class="panel-eyebrow">READY</div>' +
    '<h2 style="margin:10px 0 6px;" id="lblWelcome">' + t('backHome') + '</h2>' +
    '<p style="color:var(--text-muted);" id="lblWelcomeHelp">' +
      (state.lang === 'zh'
        ? '请在上方五阶路线中选择阶段，或从侧边栏按模块开展专项精练。支持公式渲染、选项乱序与离线记录。'
        : 'Choose a stage from the 5-Stage Roadmap above or launch a topic drill from the sidebar.') +
    '</p>';
}

function updateUILanguage() {
  document.documentElement.lang = state.lang;
  $('langBtn').textContent = state.lang === 'en' ? '🇨🇳 中文' : '🇬🇧 English';
  $('lblHeroTitle').textContent = t('heroTitle');
  $('lblHeroDesc').textContent = t('heroDesc');
  $('btnStartPractice').textContent = t('startPractice');
  $('btnTimedMock').textContent = t('timedMock');
  $('btnAdaptivePlans').textContent = t('adaptivePlans');
  $('lblRoadmapTitle').textContent = t('roadmapTitle');
  $('lblRoadmapGoal').textContent = t('roadmapGoal');
  $('headerBenchmarkTag').textContent = '🎯 ' + t('passBenchmark');
  $('headerDurationTag').textContent = '⏱ ' + t('durationTag');
  $('lblStatBank').textContent = t('bankSize');
  $('lblStatAttempts').textContent = t('answered');
  $('lblStatAccuracy').textContent = t('accuracy');
  $('lblPrivacyNote').textContent = t('privacy');
  $('btnExport').textContent = t('export');
  $('btnImport').textContent = t('import');
  $('btnReviewMistakes').innerHTML = '🎯 ' + (state.lang === 'zh' ? '错题攻坚清零' : 'Mistake Killer') + ' (<span id="mistakeBadge">' + state.mistakes.length + '</span>)';
  $('lblTopicsHeader').textContent = state.lang === 'zh' ? '考纲知识模块' : 'Syllabus Domains';
  $('lblFilterTopic').textContent = state.lang === 'zh' ? '模块筛选' : 'Topic Filter';
  $('lblBatchSize').textContent = state.lang === 'zh' ? '单次练习题量' : 'Session Size';
}

/* ================= KEYBOARD SHORTCUTS ================= */
document.addEventListener('keydown', (e) => {
  if (!activeSession) return;
  if (['input', 'textarea', 'select'].includes(document.activeElement.tagName.toLowerCase())) return;

  const key = e.key.toUpperCase();
  let optIndex = -1;
  if (['A', 'B', 'C', 'D'].includes(key)) {
    optIndex = key.charCodeAt(0) - 65;
  } else if (['1', '2', '3', '4'].includes(key)) {
    optIndex = parseInt(key, 10) - 1;
  }

  const optionBtns = document.querySelectorAll('#workArea .opt-btn');
  if (optIndex >= 0 && optIndex < optionBtns.length) {
    optionBtns[optIndex].click();
  } else if (e.key === 'Enter') {
    const primaryBtn = document.querySelector('#workArea .actionsRow .btn, #workArea button.btn');
    if (primaryBtn) primaryBtn.click();
  }
});

/* ================= GLOBAL CONTROLS & BINDINGS ================= */
$('langBtn').onclick = () => {
  state.lang = state.lang === 'en' ? 'zh' : 'en';
  saveState();
  updateUILanguage();
  renderRoadmap();
  renderDashboardStats();
  if (activeSession) {
    renderQuestionView();
  } else {
    renderWelcomeState();
  }
};

$('themeSelect').value = state.theme;
$('themeSelect').onchange = (e) => {
  state.theme = e.target.value;
  document.documentElement.setAttribute('data-theme', state.theme);
  saveState();
};
document.documentElement.setAttribute('data-theme', state.theme);

$('shuffleToggle').onclick = () => {
  state.shuffleChoices = !state.shuffleChoices;
  $('shuffleToggle').textContent = state.shuffleChoices ? '🎲 Shuffle: ON' : '🎲 Shuffle: OFF';
  saveState();
};
$('shuffleToggle').textContent = state.shuffleChoices ? '🎲 Shuffle: ON' : '🎲 Shuffle: OFF';

$('btnStartPractice').onclick = () => triggerStageAction('drilling');
$('btnTimedMock').onclick = () => triggerStageAction('mock');
$('btnAdaptivePlans').onclick = () => triggerStageAction('sprint');
$('btnReviewMistakes').onclick = () => triggerStageAction('mistakes');

// Export & Import Progress
$('btnExport').onclick = () => {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = (META.code || 'exam') + '-progress.json';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
};

$('btnImport').onclick = () => $('fileInput').click();
$('fileInput').onchange = async (e) => {
  try {
    const file = e.target.files[0];
    if (!file) return;
    const txt = await file.text();
    const data = JSON.parse(txt);
    if (!data.records || typeof data.records !== 'object') throw new Error();
    state = Object.assign({}, state, data);
    saveState();
    updateUILanguage();
    renderDashboardStats();
    renderWelcomeState();
    alert(t('importedOk'));
  } catch(err) {
    alert(t('importedBad'));
  }
};

// Initial Render
updateUILanguage();
renderRoadmap();
renderDashboardStats();
renderWelcomeState();
</script>
</body>
</html>'''

def main():
    args = get_args()
    if not validate(args.bank, args.profile):
        sys.exit(1)

    bank_data = json.loads(Path(args.bank).read_text(encoding='utf-8'))
    
    prof = {}
    if args.profile and Path(args.profile).exists():
        try:
            prof = json.loads(Path(args.profile).read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Warning: could not parse profile: {e}")

    exam_title = args.title or prof.get('exam_name') or 'Exam Practice Builder'
    exam_code = prof.get('exam_code') or 'EXAM'
    exam_category = prof.get('exam_category') or 'Adaptive Practice'
    exam_desc = prof.get('description') or 'Bilingual adaptive practice with verified reasoning and realistic mocks.'
    official_url = args.url or prof.get('official_url') or ''
    passing_score = args.pass_score if args.pass_score is not None else prof.get('passing_score_pct', 75)
    mock_duration_mins = args.mins if args.mins is not None else prof.get('exam_duration_mins', 60)
    mock_questions_count = prof.get('mock_questions_count', 20)
    logo_mono = prof.get('logo_monogram') or exam_code
    default_theme = prof.get('theme_default', 'cyber')
    
    stages = prof.get('stages', [
        {"id": "diagnostic", "name_en": "Stage 1: Diagnostic Baseline", "name_zh": "阶段一：摸底诊断", "desc_en": "Establish topic baseline with sampled questions.", "desc_zh": "抽样摸底，测试初始知识短板。"},
        {"id": "drilling", "name_en": "Stage 2: Topic Drilling", "name_zh": "阶段二：专题精练", "desc_en": "Deep-dive into specific weak topics.", "desc_zh": "逐模块靶向练习并剖析错因。"},
        {"id": "mistakes", "name_en": "Stage 3: Mistake Elimination", "name_zh": "阶段三：错题清零", "desc_en": "Eliminate recurring pitfalls with Bayesian smoothing.", "desc_zh": "错题本贝叶斯加权攻坚直至清零。"},
        {"id": "mock", "name_en": "Stage 4: Real-world Timed Mock", "name_zh": "阶段四：全真模考", "desc_en": f"Strict {mock_duration_mins}-min timed simulation ({passing_score}% pass benchmark).", "desc_zh": f"限时{mock_duration_mins}分钟仿真模考（{passing_score}%及格线）。"},
        {"id": "sprint", "name_en": "Stage 5: Final Adaptive Sprint", "name_zh": "阶段五：冲刺达标", "desc_en": "5-10 tailored adaptive test sets for mastery.", "desc_zh": "5-10套自适应个性化测试，冲刺达标。"}
    ])

    logo_svg = generate_logo_svg(logo_mono)

    bank_json = json.dumps(bank_data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    meta_json = json.dumps({
        "title": exam_title,
        "code": exam_code,
        "category": exam_category,
        "description": exam_desc,
        "official_url": official_url,
        "passing_score": passing_score,
        "mock_duration_mins": mock_duration_mins,
        "mock_questions_count": mock_questions_count,
        "default_theme": default_theme,
        "stages": stages
    }, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

    official_link_html = f'<a href="{html.escape(official_url)}" target="_blank" rel="noopener" class="badge-link">🔗 Syllabus & Rules</a>' if official_url else ''

    content = HTML_PAGE
    content = content.replace('__DEFAULT_THEME__', default_theme)
    content = content.replace('__EXAM_TITLE__', html.escape(exam_title))
    content = content.replace('__LOGO_SVG__', logo_svg)
    content = content.replace('__PASS_BENCHMARK__', str(passing_score))
    content = content.replace('__MOCK_DURATION__', str(mock_duration_mins))
    content = content.replace('__OFFICIAL_LINK_HTML__', official_link_html)
    content = content.replace('__EXAM_DESC__', html.escape(exam_desc))
    content = content.replace('__BANK_JSON__', bank_json)
    content = content.replace('__META_JSON__', meta_json)

    output_path = Path(args.out)
    output_path.write_text(content, encoding='utf-8')
    print(f"Successfully generated standalone practice website: {output_path} ({len(bank_data)} questions)")

if __name__ == '__main__':
    main()
