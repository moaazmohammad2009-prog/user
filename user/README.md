# Lucky48 Lottery & Settlement System

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![PWA Ready](https://img.shields.io/badge/PWA-Offline--First-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

An enterprise-grade, offline-first dual-tier lottery betting, draw control, and payout settlement system engineered for a **48-number** and **12-Zodiac** matrix gaming architecture.

---

## 1. System Architecture & Components

The architecture isolates core business domain logic from presentation layers, enabling full offline sync across multiple client types:

                                                  │   Core Engine (core.py)     │
                                                  │   Math, Rules, Payout Calc  │
                                                  └──────────────┬──────────────┘
                                                                 │
                                ┌────────────────────────────────┼────────────────────────────────┐
                                ▼                                ▼                                ▼
                            ┌───────────────────────┐    ┌───────────────────────┐    ┌───────────────────────┐
                            │ Desktop GUI (Tkinter) │    │ Mobile Client (PWA)   │    │  Web Dashboard Host   │
                            │ app_gui.py            │    │ index.html + sw.js    │    │  host.html            │
                            └───────────────────────┘    └───────────────────────┘    └───────────────────────┘


1. **Core Domain Engine (`core.py`)**: Pure Python module handling data models, combinatorial probability math, dynamic payout adjustments, and settlement evaluation algorithms.
2. **Desktop Operator GUI (`app_gui.py`)**: Multi-tab management host built on Tkinter. Features realtime draw optimization, risk management sliders, batch file management, and audit export.
3. **Mobile Client App (`index.html` / PWA)**: Lightweight single-page Web App using Service Worker (`sw.js`) for 100% offline functionality, local storage persistence, device UUID tagging, and line-item settlement visualization.
4. **Offline Host Dashboard (`host.html`)**: Portable HTML/JS interface for browser-based operations on mobile tablets or PCs without Python runtime dependencies.

---

## 2. Game Matrix & Mathematical Model

The engine operates on a 48-number matrix mapped cyclically across 12 Zodiac categories, drawing 7 unique balls per session.

### A. Zodiac Mapping Formula
Each number $n \in [1, 48]$ maps to a Zodiac $Z_k$ ($k \in [1, 12]$) using modular arithmetic:

$$k = ((n - 1) \pmod{12}) + 1$$

* **$Z_1$ (Rat)**: `01, 13, 25, 37`
* **$Z_2$ (Ox)**: `02, 14, 26, 38`
* **$Z_3$ (Tiger)**: `03, 15, 27, 39`
* **$Z_4$ (Rabbit)**: `04, 16, 28, 40`
* **$Z_5$ (Dragon)**: `05, 17, 29, 41`
* **$Z_6$ (Snake)**: `06, 18, 30, 42`
* **$Z_7$ (Horse)**: `07, 19, 31, 43`
* **$Z_8$ (Goat)**: `08, 20, 32, 44`
* **$Z_9$ (Monkey)**: `09, 21, 33, 45`
* **$Z_{10}$ (Rooster)**: `10, 22, 34, 46`
* **$Z_{11}$ (Dog)**: `11, 23, 35, 47`
* **$Z_{12}$ (Pig)**: `12, 24, 36, 48`

### B. Draw Structure
* **Regular Numbers ($N_1 \dots N_6$)**: 6 balls drawn without replacement from $\{1 \dots 48\}$.
* **Main Number ($M_n$)**: The 7th ball drawn. Special multiplier rules apply.

---

## 3. Bet Classifications & Payout Matrix

| Bet Code | Name | Target Scope | Selection Criteria | Default Odds | Hit Prob. |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `TM` | Main Number | $M_n$ (7th Ball) | Pick exact 1 number | **1:50** | ~2.08% |
| `TX` | Main Zodiac | $M_n$ (7th Ball) | Pick exact 1 Zodiac | **1:50** | ~8.33% |
| `TMDS` | Main Parity | $M_n$ (7th Ball) | Odd / Even selection | **1:1** | 50.00% |
| `DX` | Main Range | $M_n$ (7th Ball) | High (25-48) / Low (1-24) | **1:1** | 50.00% |
| `PTYX` | Single Zodiac | Any 7 Balls | At least 1 ball matches selected Zodiac | **1:1** | ~46.00% |
| `2LX` | 2-Zodiac Link | Any 7 Balls | All 2 selected Zodiacs appear in draw | **1:3** | ~18.00% |
| `3LX` | 3-Zodiac Link | Any 7 Balls | All 3 selected Zodiacs appear in draw | **1:10** | ~6.00% |
| `4LX` | 4-Zodiac Link | Any 7 Balls | All 4 selected Zodiacs appear in draw | **1:300** | ~1.50% |
| `2Z2` | 2 of 2 Combination | First 6 Balls | Both selected numbers appear in $N_1..N_6$ | **1:60** | ~1.30% |
| `3Z3` | 3 of 3 Combination | First 6 Balls | All 3 selected numbers appear in $N_1..N_6$ | **1:600** | ~0.10% |
| `DP` | Regular Single | First 6 Balls | Selected number appears in $N_1..N_6$ | **1:6** | ~12.50% |

---

## 4. Execution & Setup Guide

### Prerequisites
* **Python**: 3.9 or higher (standard library dependencies only: `tkinter`, `json`, `csv`, `random`).
* **Web Browser**: Any modern browser supporting Service Workers (Chrome, Safari, Edge).

### Importing Client Bets into the Host Dashboard
Client data is stored locally in each browser and is not synchronized between devices. Export a JSON or CSV file from each client, then use the host dashboard's batch import control to load those files and include every client in the settlement preview.

### Running the Desktop Host GUI
Execute via launcher script or CLI:
```bash
# Windows
run_host_gui.bat

# Universal CLI
python app_gui.py