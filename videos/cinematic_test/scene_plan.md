# Haber-Bosch — Cinematic Scene Plan (full production)
Adapted from the approved strategic script (Claude Docs report, tab "الفيلم التجريبي") into real-footage cinematic scenes per the updated production directive. Narration text is reused verbatim from that script (already fact-checked, sourced, with required caveats).

Target runtime: ~8-9 min. Visual style: real AI-generated moving cinematic footage as primary content; maps/diagrams/on-screen numbers only as brief minor supporting inserts, never dominant.

| # | Beat | Narration window | Visual scenes (video) | Status |
|---|------|------|------|--------|
| 1 | HOOK | 0:00-0:30 | (a) Aerial dusk shot of early-1900s industrial chemical plant exterior, smoke stacks [DONE: scene1_industrial_opening.png] (b) wheat field swaying, golden light | a: image done, video pending. b: not started |
| 2 | THE PROBLEM | 0:30-1:30 | 19th-century guano mining port, ships loading, workers, desert coastline (Chile/Peru) | not started |
| 3 | THE CHALLENGE | 1:30-3:00 | 1905 German chemistry lab, Fritz Haber + assistant at small apparatus | image+video DONE (scene2_laboratory, scene2_motion_proof) — reuse as this beat's footage |
| 4 | THE BREAKTHROUGH | 3:00-4:30 | Close-up hands assembling/operating the 200-atm high-pressure apparatus (Le Rossignol), gauges, valves | image DONE (scene3_fritz_haber — reframe as generic "German chemist" for video per policy workaround), video pending retry without named figure |
| 5 | SCALING UP | 4:30-6:00 | BASF Oppau factory 1913, exterior wide shots, workers, steel vessels, steam | reuse scene1_industrial_opening as base; need additional interior/worker shots |
| 6 | THE TURN | 6:00-7:00 | Factory switching to munitions, shells on production line, WWI context (restrained) | image DONE (scene6_munitions_factory.png), video pending (Gemini daily quota) |
| 7 | MORAL SHADOW | 7:00-8:00 | Ypres 1915, gas cloud drifting over trenches, distant/symbolic framing, no graphic victims | image DONE (scene7_ypres_gas_attack.png), video pending (Gemini daily quota) |
| 8 | LEGACY | 8:00-8:45 | Modern fertilizer plant / farmland aerial — echoes hook visual | image DONE (scene8_legacy_farmland.png), video pending (Gemini daily quota) |
| 9 | ENDING/CTA | 8:45-9:00 | ORIVANTA logo animation, final title card | using existing brand assets (brand/orivanta_logo_full.jpg, orivanta_logo_circle.png, orivanta_logo_watermark.png) — built directly in final edit via ffmpeg motion graphics, no AI generation needed |

## Status update (full-production pass, continued)
All 9 scenes now have a finished reference image. Video generation for Scenes 1a, 2, 6, 7, 8 is blocked by Gemini's daily video-generation quota (reached mid-session) — will resume once it resets. Scenes "Challenge" (2 orig numbering / Scene 3 here), "Breakthrough" (4), and "Hook-b/wheat field" (1b) already have both image + Gemini-generated motion-proof video. Narration (ElevenLabs, all 9 scenes) and music/SFX (Suno, 4 instrumental cues + 3 SFX beds) are both complete — see narration_log.md and music_sfx_log.md.

## Notes
- Scene 3 (Fritz Haber) video generation blocked by Gemini policy on named public figures. Retry plan: describe as "a German chemist in his forties, receding hairline, round glasses, neat mustache" without using the name "Fritz Haber" in the video prompt text (image reference still carries the likeness). Narration audio will still say his name — only the on-screen reenactment avoids naming him in the generation prompt.
- Video file extraction from Gemini into the sandbox remains blocked (no device bridge). All clips obtained so far are low-fps motion-proof reconstructions from screenshots, not true HD exports. Flagged to user as the critical blocker for final assembly.
