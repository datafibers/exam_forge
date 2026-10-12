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

def generate_logo_svg(monogram="EXAM", color="#63ded0"):
    mono = (monogram or "EXAM")[:4].upper()
    font_size = "20" if len(mono) > 3 else "23"
    return f'''<svg class="exam-crest" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="crestGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#4db4eb" stop-opacity="0.6"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="glow"/>
      <feComposite in="SourceGraphic" in2="glow" operator="over"/>
    </filter>
  </defs>
  <circle cx="50" cy="50" r="46" fill="#0d1b33" stroke="url(#crestGrad)" stroke-width="3" filter="url(#glow)"/>
  <circle cx="50" cy="50" r="40" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="3,3" opacity="0.6"/>
  <polygon points="50,14 80,34 80,68 50,86 20,68 20,34" fill="none" stroke="{color}" stroke-width="1.5" opacity="0.4"/>
  <path d="M 30,38 Q 50,28 70,38" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  <path d="M 30,62 Q 50,72 70,62" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
  <text x="50" y="55" font-family="system-ui, -apple-system, sans-serif" font-weight="900" font-size="{font_size}" text-anchor="middle" dominant-baseline="middle" fill="#ffffff" letter-spacing="-0.5">{mono}</text>
  <polygon points="50,22 53,28 59,28 54,32 56,38 50,34 44,38 46,32 41,28 47,28" fill="{color}"/>
</svg>'''

HTML_PAGE = r'''<!doctype html>
<html lang="en" data-theme="__DEFAULT_THEME__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__EXAM_TITLE__ — Adaptive Mastery</title>
<style>
/* ================= THEME DEFINITIONS ================= */
:root[data-theme="cyber"] {
  --bg-main: #07101e;
  --bg-gradient: radial-gradient(ellipse at 8% 0%, #17325c 0%, transparent 50%), radial-gradient(ellipse at 92% 100%, #0e2942 0%, #07101e 60%);
  --panel-bg: rgba(16, 32, 58, 0.88);
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
}

:root[data-theme="light"] {
  --bg-main: #f4f7fb;
  --bg-gradient: radial-gradient(ellipse at 5% 0%, #e2ecfa 0%, transparent 55%), #f4f7fb;
  --panel-bg: rgba(255, 255, 255, 0.94);
  --panel-border: #cbd7e6;
  --panel-shadow: 0 12px 30px rgba(45, 75, 115, 0.08);
  --accent: #0f766e;
  --accent-alt: #0284c7;
  --accent-btn-text: #ffffff;
  --text-main: #132438;
  --text-muted: #4e6580;
  --chip-bg: #e6eef8;
  --chip-border: #b8cde3;
  --opt-bg: #f9fbfe;
  --opt-border: #c8d8ec;
  --opt-hover: #0f766e;
  --opt-sel: #e0f2fe;
  --opt-cor: #e6f9f0;
  --opt-cor-b: #10b981;
  --opt-wro: #feebe8;
  --opt-wro-b: #ef4444;
  --feedback-bg: #eaf6fa;
  --code-bg: #e9eef5;
}

:root[data-theme="navy"] {
  --bg-main: #0a1329;
  --bg-gradient: radial-gradient(ellipse at 10% 5%, #182a52 0%, transparent 50%), #0a1329;
  --panel-bg: rgba(17, 30, 61, 0.9);
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
}

:root[data-theme="forest"] {
  --bg-main: #071612;
  --bg-gradient: radial-gradient(ellipse at 15% 0%, #13392f 0%, transparent 50%), #071612;
  --panel-bg: rgba(13, 37, 30, 0.9);
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
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
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
  padding: 11px 18px;
  border: 0;
  border-radius: 12px;
  transition: transform 0.15s, opacity 0.15s, box-shadow 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.25);
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
  font-size: clamp(26px, 3.8vw, 36px);
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
  font-size: 20px;
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
  padding: 10px 0;
  font-size: 1.15em;
  color: var(--accent);
}
pre.code-block {
  background: var(--code-bg);
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  padding: 12px 16px;
  overflow-x: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.45;
  color: #a7e2ff;
  margin: 14px 0;
}
code.code-inline {
  background: var(--code-bg);
  border: 1px solid var(--panel-border);
  padding: 2px 6px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.9em;
  color: var(--accent);
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
  padding: 15px 18px;
  border-radius: 14px;
  margin: 10px 0;
  font-size: 16px;
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
  display: inline-block;
  min-width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 6px;
  background: var(--chip-bg);
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
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
  background: #ff5252;
  color: #fff;
  font-weight: 850;
  font-size: 15px;
  padding: 6px 14px;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 0 12px rgba(255, 82, 82, 0.4);
}

/* SCORECARD & RESULT */
.result-banner {
  text-align: center;
  padding: 30px 10px;
}
.result-score {
  font-size: 48px;
  font-weight: 900;
  letter-spacing: -1.5px;
  margin: 10px 0;
}
.verdict-stamp {
  display: inline-block;
  padding: 8px 24px;
  border-radius: 30px;
  font-weight: 900;
  font-size: 16px;
  letter-spacing: 1px;
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
  .q-stem { font-size: 18px; }
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
          <span class="pass-target-tag">🎯 Pass Benchmark: __PASS_BENCHMARK__%</span>
          <span>⏱ Official: __MOCK_DURATION__ mins</span>
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
      <button id="shuffleToggle" class="btn secondary sm" type="button" title="Randomize choice order to prevent memorizing position">🎲 Shuffle: ON</button>
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
        <button class="btn secondary" id="btnTimedMock">⏱ Official Mock (__MOCK_DURATION__m)</button>
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
const STORAGE_KEY = 'exam_forge_v3:' + (META.code || document.title);

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
    startPractice: '▶ Start Practice',
    timedMock: '⏱ Official Mock (' + META.mock_duration_mins + 'm)',
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
    finish: 'Finish Session',
    explanation: 'Detailed Concept Explanation',
    distractors: 'Why Distractors Fail (错因分析)',
    selectMulti: 'Select all correct options',
    multiPrompt: 'Multiple Choice: Select all matching answers and click Check.',
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
    noMistakes: 'No saved mistakes! Great job, continue practicing.'
  },
  zh: {
    startPractice: '▶ 开始综合练习',
    timedMock: '⏱ 官方限时模考 (' + META.mock_duration_mins + '分钟)',
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
    finish: '完成练习',
    explanation: '核心考点详细解析',
    distractors: '干扰项错因剖析 (Why Wrong)',
    selectMulti: '多选题（请勾选所有正确项）',
    multiPrompt: '多选题：请选择所有符合题意的选项，然后点击提交。',
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
    noMistakes: '当前暂无错题记录！非常棒，请继续保持。'
  }
};

const t = (k) => (I18N[state.lang] && I18N[state.lang][k]) || k;
const $ = (id) => document.getElementById(id);

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

  // Block math $$...$$
  escaped = escaped.replace(/\$\$([\s\S]+?)\$\$/g, function(m, formula) {
    return '<div class="math-block">' + formatMathString(formula) + '</div>';
  });

  // Inline math $...$
  escaped = escaped.replace(/\$([^\$\n]+?)\$/g, function(m, formula) {
    return '<span class="math-inline">' + formatMathString(formula) + '</span>';
  });

  // Newlines
  escaped = escaped.replace(/\n/g, '<br>');
  return escaped;
}

function formatMathString(f) {
  return f
    .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1 / $2)')
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
    .replace(/\^([0-9a-zA-Z]+)/g, '<sup>$1</sup>')
    .replace(/_([0-9a-zA-Z]+)/g, '<sub>$1</sub>');
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
    w += (lastResult === false ? 2.5 : 0.2);
  } else {
    w += 1.8;
  }
  if (q.difficulty === 3) w *= 1.2;
  return w;
}

function getWeightedSample(pool, n) {
  const ranked = pool.map(q => ({
    q: q,
    weight: computeQuestionWeight(q) * (0.7 + Math.random() * 0.6)
  })).sort((a, b) => b.weight - a.weight);

  const seen = new Set();
  const picked = [];
  for (const item of ranked) {
    if (picked.length >= n) break;
    if (!seen.has(item.q.id)) {
      picked.push(item.q);
      seen.add(item.q.id);
    }
  }
  return picked;
}

/* ================= SESSION RUNTIME ================= */
let activeSession = null;
let currentQuestionIndex = 0;
let userSelection = null;
let isQuestionChecked = false;
let sessionStartTime = 0;
let timerInterval = null;
let generatedPlans = [];

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
    correctCount: 0,
    answersLog: []
  };
  currentQuestionIndex = 0;
  sessionStartTime = Date.now();

  if (isTimed) {
    const mockMins = META.mock_duration_mins || 70;
    const mockTotal = META.mock_questions_count || 100;
    const totalSeconds = Math.ceil(mockMins * 60 * (questions.length / mockTotal));
    const duration = Math.max(60, totalSeconds);
    timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
      const remaining = Math.max(0, duration - elapsed);
      const clock = $('activeClock');
      if (clock) {
        const m = Math.floor(remaining / 60);
        const s = remaining % 60;
        clock.textContent = m + ':' + (s < 10 ? '0' : '') + s;
      }
      if (remaining === 0) {
        clearInterval(timerInterval);
        finishSession();
      }
    }, 1000);
  }

  renderCurrentQuestion();
}

function renderCurrentQuestion() {
  const work = $('workArea');
  work.innerHTML = '';
  if (!activeSession) return;

  const q = activeSession.questions[currentQuestionIndex];
  const qType = q.type || 'single';
  userSelection = qType === 'multiple' ? [] : null;
  isQuestionChecked = false;

  const header = document.createElement('div');
  header.className = 'q-header';
  
  const progressText = document.createElement('span');
  progressText.className = 'panel-eyebrow';
  progressText.textContent = (currentQuestionIndex + 1) + ' / ' + activeSession.total + ' · ' + activeSession.modeName;
  header.appendChild(progressText);

  if (activeSession.isTimed) {
    const clockBadge = document.createElement('div');
    clockBadge.className = 'timer-pill';
    clockBadge.innerHTML = '⏱ <span id="activeClock">--:--</span>';
    header.appendChild(clockBadge);
  }
  work.appendChild(header);

  const barWrap = document.createElement('div');
  barWrap.className = 'progress-bar-wrap';
  const barFill = document.createElement('div');
  barFill.className = 'progress-fill';
  barFill.style.width = ((currentQuestionIndex / activeSession.total) * 100) + '%';
  barWrap.appendChild(barFill);
  work.appendChild(barWrap);

  const chips = document.createElement('div');
  chips.className = 'chips-row';
  chips.innerHTML = '<span class="chip">' + q.topic + '</span>' +
    '<span class="chip">' + '★'.repeat(q.difficulty) + ' Level ' + q.difficulty + '</span>' +
    '<span class="chip qtype">' + qType.toUpperCase() + '</span>' +
    (q.concept_id ? '<span class="chip">ID: ' + q.concept_id + '</span>' : '');
  work.appendChild(chips);

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
    tip.textContent = t('multiPrompt');
    work.appendChild(tip);
  }

  let rawChoices = state.lang === 'zh' ? q.choices_zh : q.choices_en;
  let optionIndices = rawChoices.map((_, i) => i);
  if (state.shuffleChoices && qType !== 'boolean') {
    optionIndices.sort(() => Math.random() - 0.5);
  }

  const choicesContainer = document.createElement('div');
  const optionButtons = [];

  optionIndices.forEach((origIdx, displayIdx) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'opt-btn';
    const letter = String.fromCharCode(65 + displayIdx);
    const choiceText = rawChoices[origIdx];

    btn.innerHTML = '<span class="opt-tag">' + letter + '</span> <div style="flex:1;">' + renderRichText(choiceText) + '</div>';

    btn.onclick = () => {
      if (isQuestionChecked) return;
      if (qType === 'single' || qType === 'boolean') {
        userSelection = origIdx;
        optionButtons.forEach(b => b.btn.classList.remove('selected'));
        btn.classList.add('selected');
      } else if (qType === 'multiple') {
        const pos = userSelection.indexOf(origIdx);
        if (pos > -1) {
          userSelection.splice(pos, 1);
          btn.classList.remove('selected');
        } else {
          userSelection.push(origIdx);
          btn.classList.add('selected');
        }
      }
    };

    optionButtons.push({ btn: btn, origIdx: origIdx, displayIdx: displayIdx });
    choicesContainer.appendChild(btn);
  });
  work.appendChild(choicesContainer);

  const actionsRow = document.createElement('div');
  actionsRow.style.marginTop = '20px';
  actionsRow.style.display = 'flex';
  actionsRow.style.gap = '10px';

  const submitBtn = document.createElement('button');
  submitBtn.className = 'btn';
  submitBtn.textContent = t('checkAnswer');

  submitBtn.onclick = () => {
    if (qType === 'single' || qType === 'boolean') {
      if (userSelection === null) return;
    } else if (qType === 'multiple') {
      if (!userSelection || userSelection.length === 0) return;
    }

    isQuestionChecked = true;
    submitBtn.remove();

    let isCorrect = false;
    if (qType === 'single' || qType === 'boolean') {
      isCorrect = (userSelection === q.answer);
    } else if (qType === 'multiple') {
      const targetSet = new Set(q.answer);
      const userSet = new Set(userSelection);
      isCorrect = (targetSet.size === userSet.size && [...targetSet].every(x => userSet.has(x)));
    }

    if (isCorrect) activeSession.correctCount++;
    activeSession.answersLog.push({ id: q.id, correct: isCorrect });

    state.records[q.id] = [...(state.records[q.id] || []), isCorrect].slice(-30);
    if (!isCorrect && !state.mistakes.includes(q.id)) {
      state.mistakes.push(q.id);
    } else if (isCorrect && state.mistakes.includes(q.id)) {
      state.mistakes = state.mistakes.filter(x => x !== q.id);
    }
    saveState();

    optionButtons.forEach(item => {
      item.btn.disabled = true;
      const isAns = (qType === 'multiple') ? q.answer.includes(item.origIdx) : (item.origIdx === q.answer);
      const isChosen = (qType === 'multiple') ? userSelection.includes(item.origIdx) : (item.origIdx === userSelection);

      if (isAns) {
        item.btn.classList.add('correct');
      } else if (isChosen && !isAns) {
        item.btn.classList.add('wrong');
      }
    });

    if (!activeSession.isTimed) {
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
    }

    const isLast = (currentQuestionIndex === activeSession.total - 1);
    const nextBtn = document.createElement('button');
    nextBtn.className = 'btn';
    nextBtn.textContent = isLast ? t('finish') : t('next');
    nextBtn.onclick = () => {
      currentQuestionIndex++;
      if (currentQuestionIndex >= activeSession.total) {
        finishSession();
      } else {
        renderCurrentQuestion();
      }
    };
    actionsRow.appendChild(nextBtn);
    renderDashboardStats();
  };

  actionsRow.appendChild(submitBtn);
  work.appendChild(actionsRow);
}

function finishSession() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;

  const s = activeSession;
  if (!s) return;
  activeSession = null;

  const work = $('workArea');
  work.innerHTML = '';

  const accuracyPct = Math.round((s.correctCount / s.total) * 100);
  const isPassed = accuracyPct >= (META.passing_score || 75);

  const banner = document.createElement('div');
  banner.className = 'result-banner';
  banner.innerHTML = '<div class="panel-eyebrow">' + s.modeName.toUpperCase() + ' RESULTS</div>' +
    '<div class="result-score">' + s.correctCount + ' / ' + s.total + ' (' + accuracyPct + '%)</div>' +
    '<div class="verdict-stamp ' + (isPassed ? 'pass' : 'fail') + '">' +
      (isPassed ? t('verdictPassed') : t('verdictFailed')) +
    '</div>' +
    '<p style="color:var(--text-muted);max-width:540px;margin:0 auto 24px;">' +
      (isPassed
        ? (state.lang === 'zh' ? '恭喜达到官方达标线！可进入阶段五进行高阶自适应冲刺。' : 'Outstanding work! You met the benchmark. Proceed to Stage 5 adaptive drills.')
        : (state.lang === 'zh' ? '目前得分暂未达到及格线（' + META.passing_score + '%）。建议通过阶段二专题精练或阶段三错题攻坚补强。' : 'Score is below benchmark (' + META.passing_score + '%). Target weak areas in Stage 2 or 3.')) +
    '</p>';

  if (s.isTimed) {
    const missed = s.answersLog.filter(a => !a.correct);
    if (missed.length) {
      const missedHeader = document.createElement('h3');
      missedHeader.style.marginTop = '24px';
      missedHeader.textContent = state.lang === 'zh' ? '考后错题复盘与深度解析' : 'Missed Questions Review';
      banner.appendChild(missedHeader);

      missed.forEach(m => {
        const q = BANK.find(x => x.id === m.id);
        if (q) {
          const itemDiv = document.createElement('div');
          itemDiv.className = 'feedback-card';
          itemDiv.style.textAlign = 'left';
          itemDiv.innerHTML = '<strong>' + q.topic + ' [' + q.id + ']</strong>: ' + renderRichText(state.lang === 'zh' ? q.zh : q.en) +
            '<p style="margin:8px 0 0;color:var(--text-muted);">' + renderRichText(state.lang === 'zh' ? q.explanation_zh : q.explanation_en) + '</p>';
          banner.appendChild(itemDiv);
        }
      });
    }
  }

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
      state.currentStage = stg.id;
      document.querySelectorAll('.stage-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      triggerStageAction(stg.id);
    };
    grid.appendChild(card);
  });
}

function triggerStageAction(stageId) {
  if (stageId === 'diagnostic') {
    const sample = getWeightedSample(BANK, Math.min(20, BANK.length));
    startSession(sample, false, 'Diagnostic Baseline');
  } else if (stageId === 'drilling') {
    const top = $('selTopic').value;
    const pool = top === 'all' ? BANK : BANK.filter(q => q.topic === top);
    startSession(pool.slice(0, 20), false, 'Topic Drilling');
  } else if (stageId === 'mistakes') {
    const pool = BANK.filter(q => state.mistakes.includes(q.id));
    if (!pool.length) {
      alert(t('noMistakes'));
      return;
    }
    startSession(pool, false, 'Mistake Elimination');
  } else if (stageId === 'mock') {
    const count = META.mock_questions_count || 100;
    const pool = [...BANK].sort(() => Math.random() - 0.5).slice(0, count);
    startSession(pool, true, 'Official Timed Mock');
  } else if (stageId === 'sprint') {
    renderAdaptivePlansHub();
  }
}

function renderAdaptivePlansHub() {
  const work = $('workArea');
  work.innerHTML = '';

  const n = 6;
  const size = Number($('selSize').value) || 20;
  generatedPlans = Array.from({ length: n }, () => getWeightedSample(BANK, size));

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

  generatedPlans.forEach((plan, i) => {
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
      $('selTopic').value = tp;
      const pool = BANK.filter(q => q.topic === tp);
      startSession(pool.slice(0, Number($('selSize').value)), false, 'Topic: ' + tp);
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

/* ================= GLOBAL CONTROLS & BINDINGS ================= */
$('langBtn').onclick = () => {
  state.lang = state.lang === 'en' ? 'zh' : 'en';
  $('langBtn').textContent = state.lang === 'en' ? '🇨🇳 中文' : '🇬🇧 English';
  saveState();
  renderRoadmap();
  renderDashboardStats();
  if (activeSession) {
    renderCurrentQuestion();
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
    renderDashboardStats();
    renderWelcomeState();
    alert(t('importedOk'));
  } catch(err) {
    alert(t('importedBad'));
  }
};

// Initial Render
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
    mock_duration_mins = args.mins if args.mins is not None else prof.get('exam_duration_mins', 70)
    mock_questions_count = prof.get('mock_questions_count', 100)
    logo_mono = prof.get('logo_monogram') or exam_code
    default_theme = prof.get('theme_default', 'cyber')
    
    stages = prof.get('stages', [
        {"id": "diagnostic", "name_en": "Stage 1: Diagnostic Baseline", "name_zh": "阶段一：摸底诊断", "desc_en": "Establish topic baseline with sampled questions.", "desc_zh": "抽样摸底，测试初始知识短板。"},
        {"id": "drilling", "name_en": "Stage 2: Topic Drilling", "name_zh": "阶段二：专题精练", "desc_en": "Deep-dive into specific weak topics.", "desc_zh": "逐模块靶向练习并剖析错因。"},
        {"id": "mistakes", "name_en": "Stage 3: Mistake Elimination", "name_zh": "阶段三：错题清零", "desc_en": "Eliminate recurring pitfalls with Bayesian smoothing.", "desc_zh": "错题本贝叶斯加权攻坚直至清零。"},
        {"id": "mock", "name_en": "Stage 4: Real-world Timed Mock", "name_zh": "阶段四：全真模考", "desc_en": f"Official {mock_duration_mins}-min timed simulation ({passing_score}% pass benchmark).", "desc_zh": f"限时{mock_duration_mins}分钟仿真模考（{passing_score}%及格线）。"},
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

    official_link_html = f'<a href="{html.escape(official_url)}" target="_blank" rel="noopener" class="badge-link">🔗 Official Syllabus & Rules</a>' if official_url else ''

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
