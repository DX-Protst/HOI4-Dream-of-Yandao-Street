# Project: HOI4 YDS Political Routes & Core Variables Balance Reconstruction

## Architecture
This project refactors the four-dimensional variable dynamics (GPA, SA, BI, AF) and repeatable crisis management decision political power (PP) economy across the three political paths of Hearts of Iron IV mod 《盐道街之梦》 (YDS):
- **Jiang Guangping (教务统制线 / Communism)**: High bureau intervention, academic rigor, authoritarian discipline.
- **Tang Siyi / Deng Shuang (学生自治线 / Democratic & Neutrality)**: Student autonomy, club activities, power-balance (BOP) dynamic between student parliament and teacher faction.
- **Li Gang (老校复兴线 / Fascism)**: Alumni funds, meritocratic exam competition, elite restoration.
- **Universal Crisis Mission (`YDS_uc_spread_of_freedom`)**: 60-day recurring mission driving $\Delta\text{SA} = +10$ and $\Delta\text{GPA} = -5$ during peacetime (extended from 30d), requiring cyclical decision responses without triggering collapse or PP bankruptcy.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Jiang Route Decisions Rebalance | Rebalance `YDS_pb_forced_mock_exam`, `YDS_pb_dorm_sweep`, `YDS_pb_bureau_intervention` with 25-30 PP costs, 30-60d cooldowns, reduced stability hits, and sustainable GPA/SA/BI deltas | M1 | Survey |
| 2 | Tang/Deng Route Decisions & Category Fix | Rebalance `YDS_ps_voluntary_night_study`, `YDS_ps_official_clubs`, `YDS_ps_host_club_activities`, `YDS_ps_promote_autonomy`; fix `YDS_peacetime_student` category to allow `neutrality` (Deng Shuang); fix 0 PP BOP exploits | M2 | Survey |
| 3 | Li Gang Route Decisions & BI Control | Rebalance `YDS_pa_buy_rare_materials` (remove double PP charge), `YDS_pa_sponsorship_drive` (reduce PP and mitigate BI increase), add/adjust BI alleviation to prevent Liu Yan death trap | M3 | Survey |
| 4 | README.md Synchronization & Verification | Update Chapters 3 and 5 in `README.md` with new mathematical models, decision values, and cooldowns; verify 100% pass on `verify_mod.py` | M4 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Jiang Guangping Decisions Rebalance | `common/decisions/YDS_decisions.txt` (Bureau decisions) | none | **DONE** (0 lockout days, safe BI/SA/GPA, PP surplus +28~38/mo) |
| M2 | Tang/Deng Route & BOP Decisions Rebalance | `common/decisions/YDS_decisions.txt`, `common/decisions/YDS_bop_decisions.txt`, `common/decisions/categories/YDS_decision_categories.txt` | none | **DONE** (Deng neutrality unlocked, BOP 15 PP cost, BI clamped >= 0) |
| M3 | Li Gang Route Decisions & BI Alleviation | `common/decisions/YDS_decisions.txt` (Alumni decisions) | none | **DONE** (AF supply +28, demand -8, net drift +0.1601/day, zero collapse) |
| M4 | Documentation Sync & E2E Engine Verification | `README.md`, run `verify_mod.py`, simulation verification | M1, M2, M3 | **DONE** (100% verify_mod PASS, 24/24 simulation scenarios PASS, Gate PASS) |

## Interface Contracts
### Variables & Threshold Boundaries
- `YDS_gpa_score`: Safe range $[60, 80]$, Warning $<60$ (`YDS_gpa_low_debuff`), Terminal $<40$ (`yds_event.1003`). Verified empirical range: $[66.0, 103.0]$.
- `YDS_student_autonomy`: Safe range $[30, 70]$, Warning $<30$ (`YDS_autonomy_low_debuff`), Terminal $>90$ (`yds_event.1000`). Verified empirical range: $[15.0, 58.0]$.
- `YDS_bureau_intervention`: Safe range $[0, 85]$, Terminal $\ge 100$ (`yds_event.1004`). Verified empirical range: $[0.0, 43.0]$.
- `YDS_alumni_funds`: Safe range $[15, 100]$, Warning $<15$ (blocks tutoring decisions). Verified empirical range: $[20.0, 76.0]$.

### Decision Economy Standards
- Single crisis decision base cost: $20 \sim 35\text{ PP}$.
- Execution duration (`days_remove`): $14 \sim 30\text{ days}$.
- Cooldown period (`days_re_enable`): $30 \sim 60\text{ days}$ (emergency entertainment: 21d).
- Monthly maintenance PP expenditure: strictly bounded within $30 \sim 50\text{ PP/month}$ (against $57 \sim 75\text{ PP/month}$ player generation), leaving $>16 \sim 42\text{ PP/month}$ surplus for strategic freedom.

## Code Layout
- `common/decisions/YDS_decisions.txt`: Route-specific crisis management decisions.
- `common/decisions/YDS_bop_decisions.txt`: Class 1 BOP balance decisions.
- `common/decisions/categories/YDS_decision_categories.txt`: Category definitions and ideological `allowed` gates.
- `common/scripted_variables/YDS_variables.txt`: Mod scripted variables and cost constants.
- `localisation/simp_chinese/YDS_core_l_simp_chinese.yml`: Core tooltips (UTF-8 BOM mandatory).
- `localisation/simp_chinese/YDS_decisions_l_simp_chinese.yml`: Chinese localisation (UTF-8 BOM mandatory).
- `README.md`: Documentation chapters 3 (Variables & Mechanics) and 5 (Decisions).
- `.agents/skills/hoi4-fast-modifier/scripts/verify_mod.py`: Syntax and compliance verification script.
