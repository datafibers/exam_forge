#!/usr/bin/env python3
"""Generate a standalone bilingual, multi-theme, progressive adaptive study website from validated question JSON and exam profile."""
import argparse, html, json, sys
from pathlib import Path
from validate_bank import normalize_question, validate

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
.btn.danger-hover:hover { border-color: #ef4444; color: #ef4444; }
.btn-bookmark {
  background: var(--opt-bg);
  border: 1px solid var(--panel-border);
  color: var(--text-muted);
  border-radius: 12px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-bookmark:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}
.btn-bookmark.active {
  background: rgba(245, 158, 11, 0.15);
  border-color: #f59e0b;
  color: #f59e0b;
}

.actions-row {
  margin-top: 24px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

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
.q-figure {
  margin: 14px 0 18px;
  padding: 12px;
  background: var(--opt-bg);
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  text-align: center;
  max-width: 100%;
  overflow-x: auto;
}
.q-figure svg {
  max-width: 100%;
  height: auto;
  display: inline-block;
}
.q-figure img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  display: inline-block;
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
.rev-choice-item {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--panel-border);
  background: var(--opt-bg);
  margin: 6px 0;
  font-size: 14px;
}
.rev-choice-item.rev-correct {
  border-color: var(--opt-cor-b);
  background: var(--opt-cor);
}
.rev-choice-item.rev-wrong {
  border-color: var(--opt-wro-b);
  background: var(--opt-wro);
}
.rev-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 6px;
  margin-left: 8px;
  text-transform: uppercase;
}
.rev-badge.user-ans {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}
.rev-badge.correct-ans {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

@media print {
  body {
    background: #fff !important;
    color: #000 !important;
  }
  .header-bar, .top-controls, .roadmap-container, .hero-layout, .sidebar-panel, .footer-bar, .q-nav-grid, .progress-bar-wrap, .timer-pill, button.btn, .btn-bookmark {
    display: none !important;
  }
  .shell {
    max-width: 100% !important;
    padding: 0 !important;
  }
  .content-grid {
    display: block !important;
  }
  .work-panel, .panel {
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    background: transparent !important;
  }
  .q-stem {
    color: #000 !important;
    font-size: 16px !important;
  }
  .opt-btn {
    border: 1px solid #ccc !important;
    background: #fff !important;
    color: #000 !important;
    break-inside: avoid;
  }
  .print-page-break {
    page-break-before: always;
  }
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
      <!-- Paper Exam Print Button -->
      <button id="btnPrint" class="btn secondary sm" type="button" title="Print paper exam or save to PDF">🖨️ <span id="lblBtnPrint">Print</span></button>
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
          <button class="btn secondary sm danger-hover" id="btnReset">Reset</button>
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
      <button class="btn secondary" id="btnReviewBookmarks" style="width:100%;margin-top:6px;">
        ⭐ Bookmarked (<span id="bookmarkBadge">0</span>)
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
    writeAnswer: 'Please type your answer first.',
    fillTag: 'FILL IN THE BLANK',
    fillPlaceholder: 'Enter your answer (number or expression)...',
    correctAnswerLabel: 'Accepted Answer',
    shortTag: 'SHORT ANSWER',
    shortPlaceholder: 'Type your answer here...',
    refAnswer: 'Reference Answer',
    rubric: 'Key Points',
    selfGradePrompt: 'Compare with the reference. How did you do?',
    selfGotIt: 'I got it',
    selfMissed: 'Needs work',
    yourAnswer: 'Your Answer',
    noAnswer: '(no answer)',
    selfAssess: 'Self-assess',
    shortNotScored: '{n} short-answer question(s) awaiting self-grading below — click "I got it" / "Needs work" on each card to include in score.',
    mistakeGraduated: '✓ 2/2 consecutive mastery — graduated from Mistake Bank!',
    mistakeNeedOneMore: '✦ 1/2 mastery streak — answer correctly 1 more time to graduate from Mistake Bank.',
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
    inMistakes: 'In Mistake Bank',
    printExam: 'Print Paper Exam',
    reset: 'Reset Records',
    confirmReset: 'Are you sure you want to reset all learning records, mistakes, and bookmarks on this device? This action cannot be undone.',
    resetOk: 'All local learning progress has been reset.',
    bookmark: 'Bookmark',
    bookmarked: 'Bookmarked',
    noBookmarks: 'No bookmarked questions yet! Bookmark key questions during practice.',
    drillWeakest: '🎯 Drill Weakest Domain: ',
    attackMistakes: '🔥 Clear Mistakes (',
    practiceAgain: '🔄 Practice Again',
    paperExamTitle: 'Paper Mock Exam',
    paperCandidateName: 'Candidate: __________________   Date: ____________   Score: ______ / ______',
    printInstructions: 'Use your browser print dialog (Cmd+P / Ctrl+P) to save as PDF or print paper copies. An answer key is provided at the bottom.',
    answerKey: 'Answer Key & Concept Explanations'
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
    writeAnswer: '请先输入你的答案。',
    fillTag: '填空题',
    fillPlaceholder: '在此输入答案（数值或表达式）……',
    correctAnswerLabel: '标准答案',
    shortTag: '问答题',
    shortPlaceholder: '在此输入你的答案……',
    refAnswer: '参考答案',
    rubric: '得分要点',
    selfGradePrompt: '对照参考答案，你答得如何？',
    selfGotIt: '答对了',
    selfMissed: '需加强',
    yourAnswer: '你的答案',
    noAnswer: '（未作答）',
    selfAssess: '自评',
    shortNotScored: '{n} 道问答题待自评——在下方复盘卡片点击「答对了 / 需加强」即可动态计入模考总分。',
    mistakeGraduated: '✓ 已连续答对 2 次，彻底掌握并移出错题本！',
    mistakeNeedOneMore: '✦ 连对进度 1/2 —— 再答对 1 次即可从错题本毕业。',
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
    inMistakes: '已在错题本',
    printExam: '打印试卷 / PDF',
    reset: '清空重置',
    confirmReset: '确定要清空此设备上的所有做题记录、错题本和收藏夹吗？此操作无法撤销。',
    resetOk: '所有本地学习记录已重置。',
    bookmark: '收藏',
    bookmarked: '已收藏',
    noBookmarks: '当前暂无收藏题目！答题时点击“收藏”即可收录重点难点。',
    drillWeakest: '🎯 针对最薄弱模块专项攻坚: ',
    attackMistakes: '🔥 错题攻坚清零 (',
    practiceAgain: '🔄 再次练习',
    paperExamTitle: '纸质模拟试卷',
    paperCandidateName: '考生姓名: __________________   考试日期: ____________   成绩: ______ / ______',
    printInstructions: '可直接调用浏览器打印功能（Cmd+P / Ctrl+P）保存为 PDF 或纸质打印。卷尾附参考答案及错因精讲。',
    answerKey: '参考答案与核心考点解析'
  }
};

const TOPIC_I18N = {
  'Finance': '财务金融与核算',
  'Marketing': '市场营销与获客',
  'Strategy': '战略与商业模式',
  'Operations': '运营流程与算法',
  'STEM Math': '数理统计与模型',
  'Algebra': '代数 (Algebra)',
  'Geometry': '几何 (Geometry)',
  'Number Theory': '数论 (Number Theory)',
  'Combinatorics': '组合与概率 (Combinatorics)',
  'Business Law': '商业法规与合规',
  'Economics': '经济学原理',
  'Accounting': '财务会计',
  'Management': '组织与管理'
};

function getTopicDisplayName(topic) {
  if (state.lang === 'zh') {
    if (META.topic_i18n && META.topic_i18n[topic]) return META.topic_i18n[topic];
    if (TOPIC_I18N[topic]) return TOPIC_I18N[topic];
  }
  return topic;
}

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

function html_escape(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* ================= LATEX & CODE FORMATTER ================= */
function renderRichText(text) {
  if (!text) return '';
  let escaped = String(text)
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
  let s = String(f);
  // Strip sizing prefixes like \left and \right
  s = s.replace(/\\left\b/g, '').replace(/\\right\b/g, '');
  // Matrices: \begin{pmatrix} a & b \\ c & d \end{pmatrix}
  s = s.replace(/\\begin\{(p|b|v|V)?matrix\}([\s\S]*?)\\end\{\1?matrix\}/g, function(_, kind, body) {
    const open = kind === 'p' ? '(' : (kind === 'b' ? '[' : (kind === 'v' ? '|' : ''));
    const close = kind === 'p' ? ')' : (kind === 'b' ? ']' : (kind === 'v' ? '|' : ''));
    const rows = body.trim().split(/\\\\/).map(r => r.trim().split('&').map(c => c.trim()).join(', ')).join(' ; ');
    return open + rows + close;
  });
  // Text & font wrappers (resolve inner-most braces iteratively)
  for (let depth = 0; depth < 4; depth++) {
    s = s.replace(/\\(?:text|mathrm|textrm|operatorname)\{([^{}]*)\}/g, '<span style="font-style:normal;">$1</span>');
    s = s.replace(/\\(?:mathbf|boldsymbol)\{([^{}]*)\}/g, '<strong>$1</strong>');
    s = s.replace(/\\(?:mathit|emph)\{([^{}]*)\}/g, '<em>$1</em>');
    s = s.replace(/\\(?:vec|overrightarrow)\{([^{}]*)\}/g, '$1⃗');
    s = s.replace(/\\(?:bar|overline)\{([^{}]*)\}/g, '<span style="text-decoration:overline;">$1</span>');
    s = s.replace(/\\hat\{([^{}]*)\}/g, '$1̂');
  }
  // Resolve nested \frac{a}{b}, \sqrt[n]{x}, \sqrt{x}, ^{...}, _{...} from inner-most braces outward
  for (let depth = 0; depth < 6; depth++) {
    const prev = s;
    s = s
      .replace(/\\(?:d|t)?frac\{([^{}]*)\}\{([^{}]*)\}/g, '<span class="math-frac"><span class="num">$1</span><span class="denom">$2</span></span>')
      .replace(/\\sqrt\[([^\[\]]*)\]\{([^{}]*)\}/g, '<sup>$1</sup>√($2)')
      .replace(/\\sqrt\{([^{}]*)\}/g, '√($1)')
      .replace(/\^\{([^{}]*)\}/g, '<sup>$1</sup>')
      .replace(/_\{([^{}]*)\}/g, '<sub>$1</sub>');
    if (s === prev) break;
  }
  // Single-character superscripts and subscripts
  s = s
    .replace(/\^([0-9a-zA-Z+\-])/g, '<sup>$1</sup>')
    .replace(/_([0-9a-zA-Z+\-])/g, '<sub>$1</sub>');

  // Mathematical operators & Greek symbols
  const symMap = [
    [/\\Delta/g, 'Δ'], [/\\Gamma/g, 'Γ'], [/\\Lambda/g, 'Λ'], [/\\Omega/g, 'Ω'],
    [/\\Phi/g, 'Φ'], [/\\Pi/g, 'Π'], [/\\Sigma/g, 'Σ'], [/\\Theta/g, 'Θ'],
    [/\\alpha/g, 'α'], [/\\beta/g, 'β'], [/\\gamma/g, 'γ'], [/\\delta/g, 'δ'],
    [/\\epsilon/g, 'ε'], [/\\varepsilon/g, 'ε'], [/\\zeta/g, 'ζ'], [/\\eta/g, 'η'],
    [/\\theta/g, 'θ'], [/\\iota/g, 'ι'], [/\\kappa/g, 'κ'], [/\\lambda/g, 'λ'],
    [/\\mu/g, 'μ'], [/\\nu/g, 'ν'], [/\\xi/g, 'ξ'], [/\\pi/g, 'π'],
    [/\\rho/g, 'ρ'], [/\\sigma/g, 'σ'], [/\\tau/g, 'τ'], [/\\phi/g, 'φ'],
    [/\\varphi/g, 'φ'], [/\\chi/g, 'χ'], [/\\psi/g, 'ψ'], [/\\omega/g, 'ω'],
    [/\\sum/g, '∑'], [/\\prod/g, '∏'], [/\\int/g, '∫'], [/\\oint/g, '∮'],
    [/\\infty/g, '∞'], [/\\partial/g, '∂'], [/\\nabla/g, '∇'],
    [/\\times/g, '×'], [/\\div/g, '÷'], [/\\cdot/g, '·'], [/\\pm/g, '±'], [/\\mp/g, '∓'],
    [/\\le\b|\\leq\b/g, '≤'], [/\\ge\b|\\geq\b/g, '≥'], [/\\neq\b|\\ne\b/g, '≠'],
    [/\\approx/g, '≈'], [/\\equiv/g, '≡'], [/\\sim/g, '∼'], [/\\propto/g, '∝'],
    [/\\in\b/g, '∈'], [/\\notin\b/g, '∉'], [/\\subset/g, '⊂'], [/\\subseteq/g, '⊆'],
    [/\\cup/g, '∪'], [/\\cap/g, '∩'], [/\\emptyset|\\varnothing/g, '∅'],
    [/\\forall/g, '∀'], [/\\exists/g, '∃'], [/\\neg/g, '¬'],
    [/\\Leftrightarrow|\\iff/g, '⇔'], [/\\Rightarrow|\\implies/g, '⇒'],
    [/\\leftrightarrow/g, '↔'], [/\\rightarrow|\\to\b/g, '→'], [/\\leftarrow/g, '←'],
    [/\\ldots|\\dots|\\cdots/g, '…'], [/\\,/g, ' '], [/\\;/g, ' '], [/\\quad/g, '  ']
  ];
  symMap.forEach(([re, rep]) => { s = s.replace(re, rep); });
  return s;
}

/* ================= FILL-IN ANSWER CHECKER & MISTAKE GRADUATION ================= */
function parseNumericOrFraction(str) {
  const s = String(str).trim().replace(/,/g, '');
  if (!s) return NaN;
  if (s.endsWith('%')) {
    const v = Number(s.slice(0, -1));
    return Number.isFinite(v) ? v / 100 : NaN;
  }
  const fracMatch = s.match(/^([+-]?\d+(?:\.\d+)?)\s*\/\s*([+-]?\d+(?:\.\d+)?)$/);
  if (fracMatch) {
    const denom = Number(fracMatch[2]);
    return denom !== 0 ? Number(fracMatch[1]) / denom : NaN;
  }
  const n = Number(s);
  return Number.isFinite(n) ? n : NaN;
}

function formatAcceptedFillAnswer(q) {
  if (state.lang === 'zh' && q.answer_zh !== undefined) return String(q.answer_zh);
  if (state.lang === 'en' && q.answer_en !== undefined) return String(q.answer_en);
  return Array.isArray(q.answer) ? q.answer.join(' / ') : String(q.answer);
}

function checkFillAnswer(q, userRaw) {
  if (userRaw === undefined || userRaw === null) return false;
  const userStr = String(userRaw).trim();
  if (!userStr) return false;

  const rawTargets = [];
  if (Array.isArray(q.answer)) rawTargets.push(...q.answer);
  else if (q.answer !== undefined) rawTargets.push(q.answer);
  if (q.answer_en !== undefined) rawTargets.push(q.answer_en);
  if (q.answer_zh !== undefined) rawTargets.push(q.answer_zh);

  const norm = (x) => String(x).trim().toLowerCase().replace(/\s+/g, ' ');
  const userNorm = norm(userStr);
  const userNum = parseNumericOrFraction(userStr);
  const tol = (typeof q.tolerance === 'number' && q.tolerance >= 0) ? q.tolerance : 1e-6;

  for (const tgt of rawTargets) {
    if (norm(tgt) === userNorm) return true;
    const tgtNum = parseNumericOrFraction(tgt);
    if (Number.isFinite(userNum) && Number.isFinite(tgtNum)) {
      if (Math.abs(userNum - tgtNum) <= tol) return true;
      // Also match if target is written as e.g. 75 and user wrote 75, or percent equivalence
      if (String(tgt).trim().endsWith('%') && Math.abs(userNum - Number(String(tgt).trim().slice(0, -1))) <= tol) return true;
    }
  }
  return false;
}

// Record attempt and enforce 2-consecutive-correct requirement to graduate from Mistake Bank
function recordAttempt(qid, isCorrect) {
  const prevInMistakes = state.mistakes.includes(qid);
  const rec = [...(state.records[qid] || []), Boolean(isCorrect)].slice(-30);
  state.records[qid] = rec;

  if (!isCorrect) {
    if (!prevInMistakes) state.mistakes.push(qid);
    return 'added';
  }
  if (prevInMistakes) {
    // Require 2 consecutive correct answers to graduate out of mistakes
    if (rec.length >= 2 && rec[rec.length - 1] === true && rec[rec.length - 2] === true) {
      state.mistakes = state.mistakes.filter(x => x !== qid);
      return 'graduated';
    }
    return 'one_more';
  }
  return 'none';
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
  if (state.mistakes.includes(q.id)) w += 2.5;
  if (rec.length > 0) {
    const lastResult = rec[rec.length - 1];
    w += (lastResult === false ? 3.0 : 0.2);
  } else {
    w += 2.0;
  }
  if (q.difficulty === 3) w *= 1.2;
  return Math.max(0.1, w);
}

// Weighted random sampling without replacement using computeQuestionWeight(q)
function weightedSample(pool, n) {
  const items = [...pool];
  const picked = [];
  const target = Math.min(n, items.length);
  while (picked.length < target && items.length > 0) {
    const weights = items.map(q => computeQuestionWeight(q));
    const totalW = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * totalW;
    let chosenIdx = items.length - 1;
    for (let i = 0; i < items.length; i++) {
      r -= weights[i];
      if (r <= 0) {
        chosenIdx = i;
        break;
      }
    }
    picked.push(items.splice(chosenIdx, 1)[0]);
  }
  return picked;
}

function getStratifiedSample(pool, n) {
  const byTopic = {};
  getUniqueTopics().forEach(tp => { byTopic[tp] = []; });
  pool.forEach(q => {
    if (!byTopic[q.topic]) byTopic[q.topic] = [];
    byTopic[q.topic].push(q);
  });
  Object.keys(byTopic).forEach(tp => { byTopic[tp] = shuffle(byTopic[tp]); });

  const picked = [];
  const topics = Object.keys(byTopic).filter(tp => byTopic[tp].length > 0);
  const weights = META.domain_weights || {};
  const hasWeights = topics.some(tp => typeof weights[tp] === 'number' && weights[tp] > 0);

  if (hasWeights) {
    const totalW = topics.reduce((acc, tp) => acc + (Number(weights[tp]) || 1), 0);
    topics.forEach(tp => {
      const w = Number(weights[tp]) || 1;
      const quota = Math.min(byTopic[tp].length, Math.round((w / totalW) * n));
      for (let k = 0; k < quota && picked.length < n; k++) {
        picked.push(byTopic[tp].shift());
      }
    });
  }

  let idx = 0;
  let guard = 0;
  while (picked.length < n && picked.length < pool.length && guard < pool.length * 4) {
    const tp = topics[idx % topics.length];
    if (byTopic[tp] && byTopic[tp].length > 0) {
      picked.push(byTopic[tp].shift());
    }
    idx++;
    guard++;
  }
  return shuffle(picked);
}

function getAdaptiveSample(pool, n) {
  // Rank topics by smoothed accuracy ascending to identify weak domains
  const topicsRanked = getUniqueTopics()
    .map(tp => ({ tp, smoothed: getTopicStats(tp).smoothed }))
    .sort((a, b) => a.smoothed - b.smoothed);
  const weakTopicCount = Math.max(1, Math.ceil(topicsRanked.length / 2));
  const weakTopics = new Set(
    topicsRanked
      .filter((x, idx) => idx < weakTopicCount || x.smoothed < 0.75)
      .map(x => x.tp)
  );

  // 1. Weak domains + active mistakes (target 60%)
  const weakPool = pool.filter(q => state.mistakes.includes(q.id) || weakTopics.has(q.topic));
  const countWeak = Math.min(weakPool.length, Math.ceil(n * 0.6));
  const pickedWeak = weightedSample(weakPool, countWeak);
  const pickedIds = new Set(pickedWeak.map(q => q.id));

  // 2. Unattempted items (target 25%)
  const unattempted = pool.filter(q => !pickedIds.has(q.id) && !(state.records[q.id] && state.records[q.id].length));
  const countUnattempted = Math.min(unattempted.length, Math.ceil(n * 0.25));
  const pickedUnattempted = weightedSample(unattempted, countUnattempted);
  pickedUnattempted.forEach(q => pickedIds.add(q.id));

  // 3. Spaced retention review from previously attempted items (target 15%)
  const retentionPool = pool.filter(q => !pickedIds.has(q.id) && (state.records[q.id] && state.records[q.id].length));
  const remaining = Math.max(0, n - pickedWeak.length - pickedUnattempted.length);
  const pickedRetention = weightedSample(retentionPool, remaining);
  pickedRetention.forEach(q => pickedIds.add(q.id));

  const picked = [...pickedWeak, ...pickedUnattempted, ...pickedRetention];

  if (picked.length < n) {
    const remainingPool = pool.filter(q => !pickedIds.has(q.id));
    picked.push(...weightedSample(remainingPool, n - picked.length));
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

function toggleBookmark(qid, btnElem) {
  const idx = state.bookmarks.indexOf(qid);
  if (idx > -1) {
    state.bookmarks.splice(idx, 1);
  } else {
    state.bookmarks.push(qid);
  }
  saveState();
  const badge = $('bookmarkBadge');
  if (badge) badge.textContent = state.bookmarks.length;

  if (btnElem) {
    const isNow = state.bookmarks.includes(qid);
    btnElem.className = 'btn-bookmark' + (isNow ? ' active' : '');
    btnElem.innerHTML = isNow ? '★ ' + t('bookmarked') : '☆ ' + t('bookmark');
  }
}

function syncTimedMockSessionStorage() {
  if (!activeSession || !activeSession.isTimed) return;
  try {
    sessionStorage.setItem('exam_forge_mock_session', JSON.stringify({
      questionIds: activeSession.questions.map(q => q.id),
      modeName: activeSession.modeName,
      startTime: sessionStartTime,
      durationMins: META.mock_duration_mins || 60,
      userAnswers: userAnswers,
      currentQuestionIndex: currentQuestionIndex
    }));
  } catch(e) {}
}

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
    isSubmitted: false,
    practiceLogs: []
  };
  currentQuestionIndex = 0;
  userAnswers = {};
  questionOptionPermutations = {};
  sessionStartTime = Date.now();

  // Pre-generate choice permutations
  questions.forEach((q, idx) => {
    const rawLen = ((state.lang === 'zh' ? q.choices_zh : q.choices_en) || []).length;
    let indices = Array.from({ length: rawLen }, (_, i) => i);
    if (state.shuffleChoices && q.type !== 'boolean') {
      indices = shuffle(indices);
    }
    questionOptionPermutations[idx] = indices;
  });

  if (isTimed) {
    syncTimedMockSessionStorage();
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
        syncTimedMockSessionStorage();
        renderQuestionView();
      };
      navGrid.appendChild(dot);
    });
    work.appendChild(navGrid);
  }

  // Chips Row with Bookmark Toggle
  const chips = document.createElement('div');
  chips.className = 'chips-row';
  const qTypeLabel = qType === 'multiple' ? 'MULTIPLE CHOICE'
    : (qType === 'boolean' ? 'TRUE / FALSE'
    : (qType === 'short' ? t('shortTag')
    : (qType === 'fill' ? t('fillTag') : 'SINGLE CHOICE')));
  chips.innerHTML = '<span class="chip">' + getTopicDisplayName(q.topic) + '</span>' +
    '<span class="chip">' + '★'.repeat(q.difficulty) + ' Level ' + q.difficulty + '</span>' +
    '<span class="chip qtype">' + qTypeLabel + '</span>';

  const isBm = state.bookmarks.includes(q.id);
  const bmBtn = document.createElement('button');
  bmBtn.type = 'button';
  bmBtn.className = 'btn-bookmark' + (isBm ? ' active' : '');
  bmBtn.innerHTML = isBm ? '★ ' + t('bookmarked') : '☆ ' + t('bookmark');
  bmBtn.onclick = () => toggleBookmark(q.id, bmBtn);
  chips.appendChild(bmBtn);

  work.appendChild(chips);

  // Question Stem
  const stem = document.createElement('div');
  stem.className = 'q-stem';
  const stemText = state.lang === 'zh' ? q.zh : q.en;
  stem.innerHTML = renderRichText(stemText);
  work.appendChild(stem);

  // Question Figure / Diagram (if present)
  if (q.figure_svg) {
    const fig = document.createElement('div');
    fig.className = 'q-figure';
    fig.innerHTML = q.figure_svg;
    work.appendChild(fig);
  } else if (q.image_url) {
    const fig = document.createElement('div');
    fig.className = 'q-figure';
    fig.innerHTML = '<img src="' + q.image_url + '" alt="Figure">';
    work.appendChild(fig);
  }

  if (qType === 'multiple') {
    const tip = document.createElement('p');
    tip.style.fontSize = '12px';
    tip.style.color = 'var(--accent)';
    tip.style.margin = '-8px 0 14px';
    tip.textContent = t('selectMulti');
    work.appendChild(tip);
  }

  // Choices Handling
  const rawChoices = (state.lang === 'zh' ? q.choices_zh : q.choices_en) || [];
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
      if (isTimed) syncTimedMockSessionStorage();
    };

    optionButtons.push({ btn: btn, origIdx: origIdx, displayIdx: displayIdx });
    choicesContainer.appendChild(btn);
  });
  work.appendChild(choicesContainer);

  if (qType === 'fill') {
    const inp = document.createElement('input');
    inp.type = 'text';
    inp.id = 'fillAnswerInput';
    inp.placeholder = t('fillPlaceholder');
    inp.value = (typeof userAnswers[currentQuestionIndex] === 'string') ? userAnswers[currentQuestionIndex] : '';
    inp.style.cssText = 'width:100%;box-sizing:border-box;padding:12px 14px;border-radius:10px;border:1px solid var(--panel-border);background:var(--opt-bg);color:inherit;font:inherit;font-size:15px;margin-bottom:14px;';
    inp.oninput = () => {
      if (inp.value.trim()) userAnswers[currentQuestionIndex] = inp.value;
      else delete userAnswers[currentQuestionIndex];
      if (isTimed) syncTimedMockSessionStorage();
    };
    inp.onkeydown = (ev) => {
      if (ev.key === 'Enter') {
        ev.preventDefault();
        const primaryBtn = $('actionPrimaryBtn');
        if (primaryBtn) primaryBtn.click();
      }
    };
    work.appendChild(inp);
  } else if (qType === 'short') {
    const ta = document.createElement('textarea');
    ta.id = 'shortAnswerInput';
    ta.rows = 6;
    ta.placeholder = t('shortPlaceholder');
    ta.value = (typeof userAnswers[currentQuestionIndex] === 'string') ? userAnswers[currentQuestionIndex] : '';
    ta.style.cssText = 'width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid var(--panel-border);background:var(--opt-bg);color:inherit;font:inherit;line-height:1.5;resize:vertical;margin-bottom:14px;';
    ta.oninput = () => {
      if (ta.value.trim()) userAnswers[currentQuestionIndex] = ta.value;
      else delete userAnswers[currentQuestionIndex];
      if (isTimed) syncTimedMockSessionStorage();
    };
    work.appendChild(ta);
  }

  // Footer Actions
  const actionsRow = document.createElement('div');
  actionsRow.className = 'actions-row';

  if (isTimed) {
    // Timed Mock Controls: Prev, Next, Submit
    if (currentQuestionIndex > 0) {
      const prevBtn = document.createElement('button');
      prevBtn.className = 'btn secondary';
      prevBtn.textContent = t('prev');
      prevBtn.onclick = () => {
        currentQuestionIndex--;
        syncTimedMockSessionStorage();
        renderQuestionView();
      };
      actionsRow.appendChild(prevBtn);
    }

    if (currentQuestionIndex < activeSession.total - 1) {
      const nextBtn = document.createElement('button');
      nextBtn.className = 'btn';
      nextBtn.id = 'actionPrimaryBtn';
      nextBtn.textContent = t('next');
      nextBtn.onclick = () => {
        currentQuestionIndex++;
        syncTimedMockSessionStorage();
        renderQuestionView();
      };
      actionsRow.appendChild(nextBtn);
    }

    const submitExamBtn = document.createElement('button');
    submitExamBtn.className = 'btn secondary';
    if (currentQuestionIndex === activeSession.total - 1) {
      submitExamBtn.id = 'actionPrimaryBtn';
    }
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
    checkBtn.id = 'actionPrimaryBtn';
    checkBtn.textContent = t('checkAnswer');

    checkBtn.onclick = () => {
      const selected = userAnswers[currentQuestionIndex];
      if (qType === 'short' || qType === 'fill') {
        if (typeof selected !== 'string' || !selected.trim()) {
          alert(t('writeAnswer'));
          return;
        }
      } else if (selected === undefined || (qType === 'multiple' && (!selected || selected.length === 0))) {
        alert(t('selectMulti'));
        return;
      }

      activeSession.isChecked = true;
      checkBtn.remove();

      const finalize = (isCorrect) => {
        // Log in session
        activeSession.practiceLogs.push({
          q: q,
          isCorrect: isCorrect,
          chosen: selected,
          origPerm: questionOptionPermutations[currentQuestionIndex]
        });

        // Record result with 2-consecutive-correct mistake graduation
        const mistakeStatus = recordAttempt(q.id, isCorrect);
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

        if (qType === 'fill') {
          const inp = document.getElementById('fillAnswerInput');
          if (inp) {
            inp.disabled = true;
            inp.style.borderColor = isCorrect ? 'var(--ok)' : 'var(--danger)';
          }
        }

        // Show Feedback
        const feedback = document.createElement('div');
        feedback.className = 'feedback-card';
        const expText = state.lang === 'zh' ? q.explanation_zh : q.explanation_en;
        let fbHtml = '';
        if (qType === 'fill') {
          fbHtml += '<div style="margin-bottom:10px;padding:8px 12px;border-radius:8px;background:var(--opt-bg);border:1px solid ' + (isCorrect ? 'var(--ok)' : 'var(--danger)') + ';">' +
            '<strong>' + (isCorrect ? '✓ ' + (state.lang === 'zh' ? '回答正确' : 'Correct') : '✗ ' + (state.lang === 'zh' ? '回答错误' : 'Incorrect')) + '</strong> · ' +
            t('correctAnswerLabel') + ': <code>' + html_escape(formatAcceptedFillAnswer(q)) + '</code></div>';
        }
        if (mistakeStatus === 'graduated') {
          fbHtml += '<div style="margin-bottom:10px;font-size:12px;color:var(--ok);font-weight:700;">' + t('mistakeGraduated') + '</div>';
        } else if (mistakeStatus === 'one_more') {
          fbHtml += '<div style="margin-bottom:10px;font-size:12px;color:var(--accent);font-weight:600;">' + t('mistakeNeedOneMore') + '</div>';
        }
        fbHtml += '<h3>✦ ' + t('explanation') + '</h3>' +
          '<p style="margin:0 0 12px;line-height:1.5;">' + renderRichText(expText) + '</p>';
        feedback.innerHTML = fbHtml;

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
        nextBtn.id = 'actionPrimaryBtn';
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

      if (qType === 'short') {
        // Self-grading: reveal reference answer, then let the learner judge their own answer
        const ta = document.getElementById('shortAnswerInput');
        if (ta) ta.disabled = true;
        const refText = state.lang === 'zh' ? q.answer_zh : q.answer_en;
        const refCard = document.createElement('div');
        refCard.className = 'feedback-card';
        refCard.innerHTML = '<h3>✦ ' + t('refAnswer') + '</h3>' +
          '<div style="line-height:1.5;">' + renderRichText(refText) + '</div>';
        const rubric = state.lang === 'zh' ? q.rubric_zh : q.rubric_en;
        if (Array.isArray(rubric) && rubric.length) {
          refCard.innerHTML += '<h4 style="margin:12px 0 6px;font-size:14px;color:var(--text-muted);">' + t('rubric') + '</h4><ul style="margin:0;padding-left:20px;">' +
            rubric.map(r => '<li>' + renderRichText(r) + '</li>').join('') + '</ul>';
        }
        refCard.innerHTML += '<p style="margin:14px 0 8px;font-weight:600;">' + t('selfGradePrompt') + '</p>';
        const gradeRow = document.createElement('div');
        gradeRow.className = 'actions-row';
        const gotBtn = document.createElement('button');
        gotBtn.className = 'btn';
        gotBtn.textContent = '✓ ' + t('selfGotIt');
        const missBtn = document.createElement('button');
        missBtn.className = 'btn secondary';
        missBtn.textContent = '✗ ' + t('selfMissed');
        const onGrade = (ok) => { gradeRow.remove(); finalize(ok); };
        gotBtn.onclick = () => onGrade(true);
        missBtn.onclick = () => onGrade(false);
        gradeRow.appendChild(gotBtn);
        gradeRow.appendChild(missBtn);
        refCard.appendChild(gradeRow);
        work.appendChild(refCard);
      } else {
        // Check correctness
        let isCorrect = false;
        if (qType === 'single' || qType === 'boolean') {
          isCorrect = (selected === q.answer);
        } else if (qType === 'multiple') {
          const targetSet = new Set(q.answer);
          const userSet = new Set(selected);
          isCorrect = (targetSet.size === userSet.size && [...targetSet].every(x => userSet.has(x)));
        } else if (qType === 'fill') {
          isCorrect = checkFillAnswer(q, selected);
        }
        finalize(isCorrect);
      }
    };

    actionsRow.appendChild(checkBtn);
  }

  work.appendChild(actionsRow);
}

// Complete Timed Mock Examination
function finishTimedMock() {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = null;
  try { sessionStorage.removeItem('exam_forge_mock_session'); } catch(e) {}

  const s = activeSession;
  if (!s) return;
  activeSession = null;

  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  let correctCount = 0;
  const topicStats = {};
  const questionLogs = [];
  let ungradedShortCount = 0;

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
      } else if (qType === 'fill') {
        isCorrect = checkFillAnswer(q, chosen);
      }
    }

    if (qType === 'short') {
      ungradedShortCount++;
      questionLogs.push({ q: q, chosen: chosen, isCorrect: false, selfGraded: false, origPerm: [] });
      return;
    }

    if (isCorrect) correctCount++;

    // Update records & mistakes with 2-streak graduation
    recordAttempt(q.id, isCorrect);

    // Topic aggregation
    if (!topicStats[q.topic]) topicStats[q.topic] = { total: 0, correct: 0 };
    topicStats[q.topic].total++;
    if (isCorrect) topicStats[q.topic].correct++;

    questionLogs.push({ q: q, chosen: chosen, isCorrect: isCorrect, origPerm: questionOptionPermutations[idx] });
  });

  saveState();

  const banner = document.createElement('div');
  banner.className = 'result-banner';
  const scoreHeader = document.createElement('div');
  banner.appendChild(scoreHeader);

  const renderScoreHeader = () => {
    const gradedTotal = Math.max(1, s.total - ungradedShortCount);
    const accuracyPct = Math.round((correctCount / gradedTotal) * 100);
    const isPassed = accuracyPct >= (META.passing_score || 75);
    scoreHeader.innerHTML = '<div class="panel-eyebrow">' + s.modeName.toUpperCase() + ' SCORECARD</div>' +
      '<div class="result-score">' + correctCount + ' / ' + (s.total - ungradedShortCount) + ' (' + accuracyPct + '%)</div>' +
      (ungradedShortCount ? '<div style="font-size:12px;color:var(--text-muted);">' + t('shortNotScored').replace('{n}', ungradedShortCount) + '</div>' : '') +
      '<div class="verdict-stamp ' + (isPassed ? 'pass' : 'fail') + '">' +
        (isPassed ? t('verdictPassed') : t('verdictFailed')) +
      '</div>';
  };
  renderScoreHeader();

  // Topic Matrix Table
  const tableHeader = document.createElement('h3');
  tableHeader.style.marginTop = '20px';
  tableHeader.textContent = t('scoreMatrixHeader');
  banner.appendChild(tableHeader);

  const table = document.createElement('table');
  table.className = 'table-matrix';
  const renderTopicTable = () => {
    table.innerHTML = '<thead><tr><th>Domain</th><th>Correct</th><th>Accuracy</th></tr></thead><tbody>' +
      Object.keys(topicStats).map(tp => {
        const st = topicStats[tp];
        const rate = Math.round((st.correct / st.total) * 100);
        return '<tr><td>' + getTopicDisplayName(tp) + '</td><td>' + st.correct + ' / ' + st.total + '</td><td>' + rate + '%</td></tr>';
      }).join('') + '</tbody>';
  };
  renderTopicTable();
  banner.appendChild(table);

  // Full Question Review with Options, Distractor Reasoning, and Bookmarking
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
    const choices = (state.lang === 'zh' ? q.choices_zh : q.choices_en) || [];
    const distList = state.lang === 'zh' ? q.why_wrong_zh : q.why_wrong_en;
    const qType = q.type || 'single';
    const isBookmarked = state.bookmarks.includes(q.id);

    let cardHtml = '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">' +
      '<div><strong>#' + (idx + 1) + ' [' + getTopicDisplayName(q.topic) + ']</strong> ' +
      '<span id="revChip_' + idx + '" class="chip ' + (qType === 'short' ? '' : (item.isCorrect ? 'correct' : 'wrong')) + '">' + (qType === 'short' ? t('selfAssess') : (item.isCorrect ? '✓ ' + (state.lang === 'zh' ? '回答正确' : 'Correct') : '✗ ' + (state.lang === 'zh' ? '回答错误' : 'Incorrect'))) + '</span></div>' +
      '<button type="button" class="btn-bookmark' + (isBookmarked ? ' active' : '') + '" onclick="toggleBookmark(\'' + q.id + '\', this)">' +
      (isBookmarked ? '★ ' + t('bookmarked') : '☆ ' + t('bookmark')) + '</button>' +
      '</div>' +
      '<p style="margin:10px 0 14px;font-weight:600;font-size:15px;">' + renderRichText(stemText) + '</p>' +
      (q.figure_svg ? '<div class="q-figure">' + q.figure_svg + '</div>' : (q.image_url ? '<div class="q-figure"><img src="' + q.image_url + '" alt="Figure"></div>' : '')) +
      '<div style="margin:10px 0;">';

    const perm = item.origPerm || choices.map((_, i) => i);
    perm.forEach((origIdx, displayIdx) => {
      const letter = String.fromCharCode(65 + displayIdx);
      const choiceTxt = choices[origIdx];
      const isAns = (qType === 'multiple') ? q.answer.includes(origIdx) : (origIdx === q.answer);
      const isChosen = (qType === 'multiple') ? (Array.isArray(item.chosen) && item.chosen.includes(origIdx)) : (item.chosen === origIdx);

      let itemCls = 'rev-choice-item';
      let tagHtml = '';
      if (isAns) {
        itemCls += ' rev-correct';
        tagHtml += '<span class="rev-badge correct-ans">✓ ' + t('correctChoice') + '</span>';
      }
      if (isChosen) {
        if (!isAns) itemCls += ' rev-wrong';
        tagHtml += '<span class="rev-badge ' + (isAns ? 'correct-ans' : 'user-ans') + '">' + (isAns ? '✓ ' : '✗ ') + t('yourChoice') + '</span>';
      }

      cardHtml += '<div class="' + itemCls + '">' +
        '<div style="display:flex;align-items:flex-start;gap:8px;">' +
        '<strong>' + letter + '.</strong>' +
        '<div style="flex:1;">' + renderRichText(choiceTxt) + '</div>' +
        tagHtml +
        '</div>';

      if (distList && distList[origIdx]) {
        cardHtml += '<div class="why-wrong-item" style="margin-top:6px;">' +
          '<strong>' + t('distractors') + ':</strong> ' + renderRichText(distList[origIdx]) +
          '</div>';
      }
      cardHtml += '</div>';
    });

    if (qType === 'fill') {
      const mine = (typeof item.chosen === 'string' && item.chosen.trim()) ? item.chosen : t('noAnswer');
      cardHtml += '<div class="rev-choice-item ' + (item.isCorrect ? 'rev-correct' : 'rev-wrong') + '"><strong>' + t('yourAnswer') + ':</strong> <code>' + html_escape(mine) + '</code></div>' +
        '<div class="rev-choice-item rev-correct"><strong>' + t('correctAnswerLabel') + ':</strong> <code>' + html_escape(formatAcceptedFillAnswer(q)) + '</code></div>';
    } else if (qType === 'short') {
      const refText = state.lang === 'zh' ? q.answer_zh : q.answer_en;
      const mine = (typeof item.chosen === 'string' && item.chosen.trim()) ? item.chosen : t('noAnswer');
      cardHtml += '<div class="rev-choice-item"><strong>' + t('yourAnswer') + ':</strong><div style="white-space:pre-wrap;">' + html_escape(mine) + '</div></div>' +
        '<div class="rev-choice-item rev-correct"><strong>' + t('refAnswer') + ':</strong> ' + renderRichText(refText) + '</div>';
      const rubric = state.lang === 'zh' ? q.rubric_zh : q.rubric_en;
      if (Array.isArray(rubric) && rubric.length) {
        cardHtml += '<div class="rev-choice-item"><strong>' + t('rubric') + ':</strong><ul style="margin:4px 0 0;padding-left:18px;">' +
          rubric.map(r => '<li>' + renderRichText(r) + '</li>').join('') + '</ul></div>';
      }
      cardHtml += '<div id="shortGradeBox_' + idx + '" style="margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">' +
        '<span style="font-size:13px;font-weight:600;">' + t('selfGradePrompt') + '</span>' +
        '<button type="button" class="btn sm" id="btnShortGot_' + idx + '">✓ ' + t('selfGotIt') + '</button>' +
        '<button type="button" class="btn secondary sm" id="btnShortMiss_' + idx + '">✗ ' + t('selfMissed') + '</button>' +
        '</div>';
    }

    cardHtml += '</div>' +
      '<div style="font-size:13px;background:var(--opt-bg);border:1px solid var(--panel-border);border-radius:10px;padding:12px;margin-top:10px;">' +
      '<p style="margin:0;"><strong>' + t('explanation') + ':</strong> ' + renderRichText(expText) + '</p>' +
      '</div>';

    card.innerHTML = cardHtml;
    banner.appendChild(card);

    if (qType === 'short') {
      setTimeout(() => {
        const gotB = $('btnShortGot_' + idx);
        const missB = $('btnShortMiss_' + idx);
        const box = $('shortGradeBox_' + idx);
        const chipEl = $('revChip_' + idx);
        const applyShortGrade = (ok) => {
          if (item.selfGraded) return;
          item.selfGraded = true;
          item.isCorrect = ok;
          ungradedShortCount = Math.max(0, ungradedShortCount - 1);
          if (ok) correctCount++;
          if (!topicStats[q.topic]) topicStats[q.topic] = { total: 0, correct: 0 };
          topicStats[q.topic].total++;
          if (ok) topicStats[q.topic].correct++;
          recordAttempt(q.id, ok);
          saveState();
          if (chipEl) {
            chipEl.className = 'chip ' + (ok ? 'correct' : 'wrong');
            chipEl.textContent = ok ? '✓ ' + (state.lang === 'zh' ? '回答正确' : 'Correct') : '✗ ' + (state.lang === 'zh' ? '回答错误' : 'Incorrect');
          }
          if (box) box.remove();
          renderScoreHeader();
          renderTopicTable();
          renderDashboardStats();
        };
        if (gotB) gotB.onclick = () => applyShortGrade(true);
        if (missB) missB.onclick = () => applyShortGrade(false);
      }, 0);
    }
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
  if (!s) return;
  activeSession = null;
  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const logs = s.practiceLogs || [];
  const total = logs.length || s.total;
  const correctCount = logs.filter(item => item.isCorrect).length;
  const accuracyPct = total ? Math.round((correctCount / total) * 100) : 0;

  const topicStats = {};
  logs.forEach(item => {
    const tp = item.q.topic;
    if (!topicStats[tp]) topicStats[tp] = { total: 0, correct: 0 };
    topicStats[tp].total++;
    if (item.isCorrect) topicStats[tp].correct++;
  });

  // Identify lowest performing topic
  let weakestTopic = null;
  let lowestRate = 101;
  Object.keys(topicStats).forEach(tp => {
    const rate = Math.round((topicStats[tp].correct / topicStats[tp].total) * 100);
    if (rate < lowestRate) {
      lowestRate = rate;
      weakestTopic = tp;
    }
  });

  const banner = document.createElement('div');
  banner.className = 'result-banner';
  banner.innerHTML = '<div class="panel-eyebrow">' + s.modeName.toUpperCase() + ' SUMMARY</div>' +
    '<h2 style="margin:8px 0;">' + (state.lang === 'zh' ? '本轮练习已完成' : 'Session Completed') + '</h2>' +
    '<div class="result-score">' + correctCount + ' / ' + total + ' (' + accuracyPct + '%)</div>' +
    '<p style="color:var(--text-muted);margin-bottom:20px;">' +
      (state.lang === 'zh' ? '答题记录已更新，自适应算法已动态调整薄弱点权重。' : 'Performance recorded and local mastery weights updated.') +
    '</p>';

  if (Object.keys(topicStats).length > 0) {
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
        return '<tr><td>' + getTopicDisplayName(tp) + '</td><td>' + st.correct + ' / ' + st.total + '</td><td>' + rate + '%</td></tr>';
      }).join('') + '</tbody>';
    banner.appendChild(table);
  }

  // Next steps recommendation
  const recBox = document.createElement('div');
  recBox.style.margin = '24px 0';
  recBox.style.padding = '18px';
  recBox.style.borderRadius = '14px';
  recBox.style.background = 'var(--chip-bg)';
  recBox.style.border = '1px solid var(--chip-border)';
  recBox.style.textAlign = 'left';

  let recHtml = '<div class="panel-eyebrow">✦ ' + (state.lang === 'zh' ? '下一步智能备考建议' : 'Recommended Next Step') + '</div>';
  if (weakestTopic && lowestRate < 80) {
    recHtml += '<p style="margin:6px 0 14px;font-size:14px;">' +
      (state.lang === 'zh'
        ? '在本次测试中，您在 <strong>' + getTopicDisplayName(weakestTopic) + '</strong> 模块正确率为 ' + lowestRate + '%。建议立即开展专项突破！'
        : 'Your accuracy was lowest in <strong>' + weakestTopic + '</strong> (' + lowestRate + '%). We recommend a targeted topic drill.') +
      '</p>';
  } else {
    recHtml += '<p style="margin:6px 0 14px;font-size:14px;">' +
      (state.lang === 'zh'
        ? '知识掌握扎实！建议继续挑战全真限时模考或清空剩余错题。'
        : 'Strong performance! Proceed to a full Timed Mock or eliminate remaining mistakes.') +
      '</p>';
  }

  recHtml += '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;">';
  if (weakestTopic) {
    recHtml += '<button class="btn sm" id="btnRecDrill">' + t('drillWeakest') + getTopicDisplayName(weakestTopic) + '</button>';
  }
  if (state.mistakes.length > 0) {
    recHtml += '<button class="btn secondary sm" id="btnRecMistakes">' + t('attackMistakes') + state.mistakes.length + ')</button>';
  }
  recHtml += '<button class="btn secondary sm" id="btnRecAgain">' + t('practiceAgain') + '</button>';
  recHtml += '</div>';

  recBox.innerHTML = recHtml;
  banner.appendChild(recBox);

  const backBtn = document.createElement('button');
  backBtn.className = 'btn';
  backBtn.style.marginTop = '14px';
  backBtn.textContent = t('backHome');
  backBtn.onclick = () => { renderWelcomeState(); };
  banner.appendChild(backBtn);

  work.appendChild(banner);
  renderDashboardStats();

  // Bind recommendation buttons
  if ($('btnRecDrill') && weakestTopic) {
    $('btnRecDrill').onclick = () => {
      $('selTopic').value = weakestTopic;
      const pool = BANK.filter(q => q.topic === weakestTopic);
      startSession(weightedSample(pool, Number($('selSize').value) || 20), false, 'Topic: ' + weakestTopic);
    };
  }
  if ($('btnRecMistakes')) {
    $('btnRecMistakes').onclick = () => triggerStageAction('mistakes');
  }
  if ($('btnRecAgain')) {
    $('btnRecAgain').onclick = () => {
      startSession(s.questions, false, s.modeName);
    };
  }
}

/* ================= PAPER EXAM PRINT MODE ================= */
function renderPrintablePaperExam() {
  const work = $('workArea');
  work.innerHTML = '';
  work.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const container = document.createElement('div');
  container.className = 'paper-exam-wrapper';

  const titleText = META.title + ' - ' + t('paperExamTitle');
  container.innerHTML = '<div style="border-bottom:2px solid #444;padding-bottom:14px;margin-bottom:20px;">' +
    '<h1 style="margin:0 0 8px;font-size:24px;">' + titleText + '</h1>' +
    '<p style="margin:4px 0;font-size:13px;color:var(--text-muted);">' + t('paperCandidateName') + '</p>' +
    '<p style="margin:4px 0;font-size:12px;color:var(--text-muted);">' + t('durationTag') + ' · ' + t('passBenchmark') + '</p>' +
    '<p style="margin:6px 0 0;font-size:12px;font-style:italic;">' + t('printInstructions') + '</p>' +
    '</div>';

  BANK.forEach((q, idx) => {
    const qDiv = document.createElement('div');
    qDiv.style.marginBottom = '22px';
    qDiv.style.breakInside = 'avoid';

    const stemText = state.lang === 'zh' ? q.zh : q.en;
    const choices = (state.lang === 'zh' ? q.choices_zh : q.choices_en) || [];

    qDiv.innerHTML = '<div style="font-weight:700;margin-bottom:8px;font-size:15px;line-height:1.45;">' +
      (idx + 1) + '. [' + getTopicDisplayName(q.topic) + '] ' + renderRichText(stemText) +
      '</div>' +
      (q.figure_svg ? '<div class="q-figure">' + q.figure_svg + '</div>' : (q.image_url ? '<div class="q-figure"><img src="' + q.image_url + '" alt="Figure"></div>' : ''));

    const optsDiv = document.createElement('div');
    optsDiv.style.paddingLeft = '14px';
    choices.forEach((ch, cIdx) => {
      const letter = String.fromCharCode(65 + cIdx);
      const row = document.createElement('div');
      row.style.margin = '4px 0';
      row.style.fontSize = '14px';
      row.innerHTML = '<strong>(' + letter + ')</strong> [ &nbsp; ] ' + renderRichText(ch);
      optsDiv.appendChild(row);
    });
    qDiv.appendChild(optsDiv);
    const qType = q.type || 'single';
    if (qType === 'fill') {
      const blank = document.createElement('div');
      blank.style.paddingLeft = '14px';
      blank.style.marginTop = '8px';
      blank.innerHTML = '<strong>' + t('yourAnswer') + ':</strong> ________________________';
      qDiv.appendChild(blank);
    } else if (qType === 'short') {
      const lines = document.createElement('div');
      lines.style.paddingLeft = '14px';
      for (let li = 0; li < 5; li++) {
        const ln = document.createElement('div');
        ln.style.borderBottom = '1px solid #888';
        ln.style.height = '26px';
        lines.appendChild(ln);
      }
      qDiv.appendChild(lines);
    }
    container.appendChild(qDiv);
  });

  // Appendix: Answer Key & Explanations with print page break
  const keySection = document.createElement('div');
  keySection.className = 'print-page-break';
  keySection.style.marginTop = '40px';
  keySection.style.borderTop = '2px dashed #888';
  keySection.style.paddingTop = '24px';

  keySection.innerHTML = '<h2 style="margin-bottom:16px;">✦ ' + t('answerKey') + '</h2>';
  BANK.forEach((q, idx) => {
    const expText = state.lang === 'zh' ? q.explanation_zh : q.explanation_en;
    const qType = q.type || 'single';

    let ansLetters = '';
    let refHtml = '';
    if (qType === 'short') {
      ansLetters = t('shortTag');
      const refText = state.lang === 'zh' ? q.answer_zh : q.answer_en;
      refHtml = '<div style="margin:4px 0;"><strong>' + t('refAnswer') + ':</strong> ' + renderRichText(refText) + '</div>';
    } else if (qType === 'fill') {
      ansLetters = formatAcceptedFillAnswer(q);
    } else if (qType === 'multiple') {
      ansLetters = q.answer.map(i => String.fromCharCode(65 + i)).join(', ');
    } else {
      ansLetters = String.fromCharCode(65 + q.answer);
    }

    const row = document.createElement('div');
    row.style.marginBottom = '12px';
    row.style.fontSize = '13px';
    row.style.breakInside = 'avoid';
    row.innerHTML = '<strong>#' + (idx + 1) + ' [' + html_escape(ansLetters) + ']:</strong> ' +
      refHtml + renderRichText(expText);
    keySection.appendChild(row);
  });
  container.appendChild(keySection);

  work.appendChild(container);

  setTimeout(() => {
    window.print();
  }, 300);
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
    startSession(weightedSample(pool, size), false, 'Topic Drilling');
  } else if (stageId === 'mistakes') {
    const pool = BANK.filter(q => state.mistakes.includes(q.id));
    if (!pool.length) {
      alert(t('noMistakes'));
      return;
    }
    startSession(weightedSample(pool, pool.length), false, 'Mistake Elimination');
  } else if (stageId === 'mock') {
    const count = META.mock_questions_count || 20;
    const pool = getStratifiedSample(BANK, count);
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
  if ($('bookmarkBadge')) $('bookmarkBadge').textContent = state.bookmarks.length;

  const list = $('topicList');
  list.innerHTML = '';
  getUniqueTopics().forEach(tp => {
    const stat = getTopicStats(tp);
    const item = document.createElement('div');
    item.className = 'topic-item';
    item.innerHTML = '<span>' + getTopicDisplayName(tp) + '</span><span class="topic-rate">' + (stat.rawRate !== null ? stat.rawRate + '%' : '—') + '</span>';
    item.onclick = () => {
      if (activeSession && !confirm(t('confirmExit'))) return;
      $('selTopic').value = tp;
      const pool = BANK.filter(q => q.topic === tp);
      startSession(weightedSample(pool, Number($('selSize').value) || 20), false, 'Topic: ' + getTopicDisplayName(tp));
    };
    list.appendChild(item);
  });

  const currentSel = $('selTopic').value;
  $('selTopic').innerHTML = '<option value="all">' + t('allTopics') + '</option>';
  getUniqueTopics().forEach(tp => {
    const opt = document.createElement('option');
    opt.value = tp;
    opt.textContent = getTopicDisplayName(tp);
    $('selTopic').appendChild(opt);
  });
  if (currentSel) $('selTopic').value = currentSel;
}

function renderWelcomeState() {
  const work = $('workArea');
  const isZh = state.lang === 'zh';

  let stagesVisualHtml = '<div style="margin:20px 0;padding:16px;background:var(--opt-bg);border:1px solid var(--panel-border);border-radius:16px;">' +
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:6px;">' +
      '<span class="panel-eyebrow" style="margin:0;">✦ ' + (isZh ? '五阶闯关备考路线' : '5-Stage Learning Progression') + '</span>' +
      '<span style="font-size:11px;color:var(--text-muted);">' + (isZh ? '点击任意阶段直接进入' : 'Click any milestone to launch') + '</span>' +
    '</div>' +
    '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));gap:10px;">';

  const stagesData = [
    { id: 'diagnostic', idx: '01', icon: '🎯', name: isZh ? '摸底诊断' : 'Diagnostic', tag: isZh ? '抽样摸底' : 'Sample 20' },
    { id: 'drilling',   idx: '02', icon: '📚', name: isZh ? '专题精练' : 'Topic Drill', tag: isZh ? '分项突破' : 'Domain Drills' },
    { id: 'mistakes',   idx: '03', icon: '🔥', name: isZh ? '错题清零' : 'Mistake Killer', tag: isZh ? '贝叶斯加权' : 'Zero Pitfalls' },
    { id: 'mock',       idx: '04', icon: '⏱️', name: isZh ? '全真模考' : 'Timed Mock', tag: isZh ? '限时及格线' : 'Pass Verdict' },
    { id: 'sprint',     idx: '05', icon: '🏆', name: isZh ? '冲刺达标' : 'Adaptive Sprint', tag: isZh ? '5套强化卷' : 'Mastery Ready' }
  ];

  stagesData.forEach(st => {
    stagesVisualHtml += '<div style="background:var(--chip-bg);border:1px solid var(--chip-border);border-radius:12px;padding:12px;text-align:center;cursor:pointer;transition:transform 0.15s,border-color 0.15s;" ' +
      'onmouseover="this.style.borderColor=\'var(--accent)\';this.style.transform=\'translateY(-2px)\'" ' +
      'onmouseout="this.style.borderColor=\'var(--chip-border)\';this.style.transform=\'none\'" ' +
      'onclick="triggerStageAction(\'' + st.id + '\')">' +
      '<div style="font-size:10px;font-weight:800;color:var(--accent);letter-spacing:1px;">STAGE ' + st.idx + '</div>' +
      '<div style="font-size:22px;margin:4px 0;">' + st.icon + '</div>' +
      '<div style="font-weight:750;font-size:13px;color:var(--text-main);">' + st.name + '</div>' +
      '<div style="font-size:10px;color:var(--text-muted);margin-top:2px;">' + st.tag + '</div>' +
      '</div>';
  });

  stagesVisualHtml += '</div></div>';

  work.innerHTML = '<div class="panel-eyebrow">READY</div>' +
    '<h2 style="margin:10px 0 6px;" id="lblWelcome">' + t('backHome') + '</h2>' +
    '<p style="color:var(--text-muted);" id="lblWelcomeHelp">' +
      (isZh
        ? '请在下方备考路线中选择阶段，或从侧边栏按模块开展专项精练。支持公式渲染、图表展示、选项乱序、错因剖析与本地离线持久化。'
        : 'Choose a stage from the progression roadmap below or launch a topic drill from the sidebar.') +
    '</p>' +
    stagesVisualHtml;
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
  if ($('btnReset')) $('btnReset').textContent = t('reset');
  if ($('lblBtnPrint')) $('lblBtnPrint').textContent = t('printExam');
  $('btnReviewMistakes').innerHTML = '🎯 ' + (state.lang === 'zh' ? '错题攻坚清零' : 'Mistake Killer') + ' (<span id="mistakeBadge">' + state.mistakes.length + '</span>)';
  if ($('btnReviewBookmarks')) {
    $('btnReviewBookmarks').innerHTML = '⭐ ' + (state.lang === 'zh' ? '重点收藏夹' : 'Bookmarked') + ' (<span id="bookmarkBadge">' + state.bookmarks.length + '</span>)';
  }
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
  if (['A', 'B', 'C', 'D', 'E'].includes(key)) {
    optIndex = key.charCodeAt(0) - 65;
  } else if (['1', '2', '3', '4', '5'].includes(key)) {
    optIndex = parseInt(key, 10) - 1;
  }

  const optionBtns = document.querySelectorAll('#workArea .opt-btn');
  if (optIndex >= 0 && optIndex < optionBtns.length) {
    optionBtns[optIndex].click();
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const primaryBtn = $('actionPrimaryBtn') || document.querySelector('#workArea .actions-row .btn, #workArea button.btn');
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

if ($('btnPrint')) {
  $('btnPrint').onclick = () => renderPrintablePaperExam();
}

$('btnStartPractice').onclick = () => triggerStageAction('drilling');
$('btnTimedMock').onclick = () => triggerStageAction('mock');
$('btnAdaptivePlans').onclick = () => triggerStageAction('sprint');
$('btnReviewMistakes').onclick = () => triggerStageAction('mistakes');
if ($('btnReviewBookmarks')) {
  $('btnReviewBookmarks').onclick = () => {
    const pool = BANK.filter(q => state.bookmarks.includes(q.id));
    if (!pool.length) {
      alert(t('noBookmarks'));
      return;
    }
    startSession(shuffle(pool), false, state.lang === 'zh' ? '重点收藏题目' : 'Bookmarked Questions');
  };
}

// Reset Learning Progress
if ($('btnReset')) {
  $('btnReset').onclick = () => {
    if (confirm(t('confirmReset'))) {
      state.records = {};
      state.qStats = {};
      state.mistakes = [];
      state.bookmarks = [];
      saveState();
      updateUILanguage();
      renderDashboardStats();
      renderWelcomeState();
      alert(t('resetOk'));
    }
  };
}

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

function checkPendingTimedMock() {
  try {
    const raw = sessionStorage.getItem('exam_forge_mock_session');
    if (!raw) return;
    const data = JSON.parse(raw);
    if (!data.questionIds || !data.questionIds.length) return;
    const elapsed = Math.floor((Date.now() - data.startTime) / 1000);
    const totalSecs = (data.durationMins || 60) * 60;
    if (elapsed >= totalSecs) {
      sessionStorage.removeItem('exam_forge_mock_session');
      return;
    }
    const msg = state.lang === 'zh'
      ? '检测到您刚才有一场未完成的全真限时模考，是否恢复作答？'
      : 'An ongoing timed mock exam was detected. Would you like to resume where you left off?';
    if (confirm(msg)) {
      const qs = data.questionIds.map(id => BANK.find(q => q.id === id)).filter(Boolean);
      if (qs.length) {
        startSession(qs, true, data.modeName);
        userAnswers = data.userAnswers || {};
        currentQuestionIndex = data.currentQuestionIndex || 0;
        sessionStartTime = data.startTime;
        renderQuestionView();
      }
    } else {
      sessionStorage.removeItem('exam_forge_mock_session');
    }
  } catch(e) {}
}

// Initial Render
updateUILanguage();
renderRoadmap();
renderDashboardStats();
renderWelcomeState();
checkPendingTimedMock();
</script>
</body>
</html>'''

def main():
    args = get_args()
    if not validate(args.bank, args.profile):
        sys.exit(1)

    raw_bank_data = json.loads(Path(args.bank).read_text(encoding='utf-8'))
    bank_data = [normalize_question(q) for q in raw_bank_data]
    
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
    domain_weights = prof.get('domain_weights') if isinstance(prof.get('domain_weights'), dict) else {}
    
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
        "domain_weights": domain_weights,
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
