# V4 Shot-by-Shot Audit vs. the Permanent Production Standard

Nothing generated, nothing changed in v4. This is the requested audit + cost estimate only.

## 1. Per-scene breakdown: real footage vs. still+Ken Burns fill

| Scene | Narration length | Real video now | Info-card (compliant) | Still+KenBurns fill | Fill % of scene |
|---|---|---|---|---|---|
| 1 — Hook/Industrial | 23.6s | 13.0s (2 clips) | 0s | 10.5s | 45% |
| 2 — Guano Port | 47.1s | 8.0s (1 clip) | 4.0s | 35.1s | 75% |
| 3 — Lab/Haber process | 39.6s | 5.0s (1 clip) | 5.3s | 29.3s | 74% |
| 4 — Breakthrough | 37.6s | 5.0s (1 clip) | 0s | 32.6s | **87%** |
| 5 — Oppau factory | 52.8s | 8.0s (1 clip) | 5.0s | 39.8s | 75% |
| 6 — Munitions turn | 37.7s | 5.0s (1 clip) | 0s | 32.7s | **87%** |
| 7 — Ypres | 42.9s | 5.0s (1 clip) | 4.0s | 33.9s | 79% |
| 8 — Legacy/farmland | 30.1s | 8.0s (1 clip) | 0s | 22.1s | 73% |
| **Total (scenes 1–8)** | **311.4s** | **57.2s** | **18.3s** | **235.9s** | **76%** |

**Bottom line: only ~24% of the film's scene time is real moving footage; ~76% is a still
photo animated with a Ken Burns zoom/pan.** That ratio is exactly what the new standard's
rule 2 prohibits as a substitute for required cinematic footage, regardless of how varied the
zoom presets are. The info-cards (18.3s total, across scenes 2/3/5/7) are compliant as-is —
they're honest, static information graphics, not disguised as footage.

## 2. Which scenes genuinely need new moving footage

All 8 need some amount — none currently reaches a "mostly real footage, stills only as brief
intentional inserts" state. Ranked by how far they are from compliant, combining severity
(fill %) and absolute minutes affected:

1. **Scene 5** (Oppau factory) — worst in absolute terms: 39.8s to cover, 75% of the scene.
2. **Scene 7** (Ypres) — 33.9s, 79% of the scene.
3. **Scene 4** (Breakthrough) — 32.6s, 87% of the scene (worst ratio).
4. **Scene 6** (Munitions turn) — 32.7s, 87% of the scene (worst ratio).
5. **Scene 2** (Guano Port) — 35.1s, 75% of the scene.
6. **Scene 3** (Lab) — 29.3s, 74% of the scene.
7. **Scene 8** (Legacy/farmland) — 22.1s, 73% of the scene.
8. **Scene 1** (Hook) — least urgent: already 45% real footage from two clips (the strongest
   scene in the film today), only 10.5s short.

## 3. Existing assets that can be reused as-is

All 8 current real clips (listed in the table above, totaling 57.2s) are good footage already
paid for and generated — none need to be redone. They stay in the edit as the "anchor" shot
for each scene; new generation only needs to cover each scene's *remaining* time, not replace
what's already there. The 4 info-cards (War of the Pacific, Haber equation, Oppau, Ypres) also
stay as-is — they're compliant information graphics.

## 4. New-footage requirement and estimate

To fully replace all 235.9s of still+KenBurns fill with real moving footage:

| Scene | Fill to replace | Clips @ ~8s (Veo 3.1) | Clips @ ~5s (Kling 2.5 Turbo) |
|---|---|---|---|
| 1 | 10.5s | 2 | 3 |
| 2 | 35.1s | 5 | 8 |
| 3 | 29.3s | 4 | 6 |
| 4 | 32.6s | 5 | 7 |
| 5 | 39.8s | 5 | 8 |
| 6 | 32.7s | 5 | 7 |
| 7 | 33.9s | 5 | 7 |
| 8 | 22.1s | 3 | 5 |
| **Total** | **235.9s** | **~34 clips** | **~51 clips** |

Notes on cost/time, based on this session's actual history with these two tools:
- **Veo 3.1** (via the ElevenLabs creative connector) gives longer clips (fewer generations
  needed, 34 vs 51) but has hit a **daily generation cap** repeatedly in this project already
  (documented in `scene_plan.md`: capped after a handful of requests, with resets roughly a
  day later); one generation has also taken 15+ minutes. 34 Veo clips realistically means
  **several days** of capped, spaced-out generation, not one sitting.
- **Kling 2.5 Turbo** has not hit a cap in this project so far and has run reliably for
  scenes 3/4/6/7 already, but needs more individual generations (51) for the same coverage.
- I don't have visibility into a dollar cost per generation from here — these run against
  your existing connected subscriptions/credits, and availability is capped by quota, not
  by a price I can quote. Either way, **nothing will be generated or purchased without your
  go-ahead**, per your standing instruction.
- A realistic mixed plan (Veo where available, falling back to Kling when Veo caps) spread
  across **roughly 3–5 generation days** is the practical path, not a same-day turnaround.

## 5. What editing alone (no new generation) can and can't fix

Editing can improve pacing, variety and polish of what exists today — e.g., using more than
one still per scene, tighter crops, better-timed cuts into/out of the info-cards. **It cannot
fix the core compliance issue.** The standard's problem isn't that the Ken Burns moves look
bad (QA already confirmed they look clean and varied) — it's that a still-plus-zoom is not
real footage at all, by rule 2's own wording, however well executed. Reaching compliance
requires new real footage, not a better edit of the stills.

## 6. Recommendation

Given the "preserve resources, avoid another testing cycle" instruction and the realistic
multi-day generation pacing above, I'd suggest a **phased rollout rather than one 34-clip
batch**:

- **Phase 1** — the 4 worst scenes by combined severity: Scene 5, Scene 7, Scene 4, Scene 6
  (≈19 Veo-equivalent clips, ≈138s of new footage). This alone would take the film's overall
  real-footage ratio from 24% to roughly 55–60%, and directly fixes the two scenes (4, 6) that
  are 87% stills — the most severe violations.
- **Phase 2** — the remaining 4 scenes (Scene 2, 3, 8, and topping up Scene 1) — ≈15 more
  clips — once Phase 1 is generated, QA'd and approved.

This lets you review real progress and cost after Phase 1 before committing to the rest,
rather than spending multiple days of generation credits on a single unreviewed batch.

**Awaiting your decision before anything is generated or v4 is touched:** go ahead with
Phase 1 as scoped above, change the scope/order, or hold entirely.
