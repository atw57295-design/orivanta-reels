# Haber-Bosch — Music & SFX Log (Suno)

Generated on the user's Suno account (same account already used for prior ORIVANTA work), via the "Songs" and "Sounds" tabs, Advanced mode, v6, instrumental (lyrics left blank → instrumental output).

## Instrumental score cues (4, each with 2 takes)
| Cue | Covers beats | Style brief |
|---|---|---|
| "الإشارة الأولى" (The First Signal) | HOOK → PROBLEM → CHALLENGE | Mysterious, inquisitive orchestral opening, slow string swells, soft piano, subtle building tension |
| "Haber-Bosch — Breakthrough" | BREAKTHROUGH → SCALING UP | Triumphant, driving, industrial momentum, pulsing low brass/strings, rising to a climax |
| "Haber-Bosch — Moral Shadow" (title got garbled on-page to "HHaber-Bosch — Moral Shadowaber-Bosch — Breakthrough" due to a field-clearing glitch; audio content is correct — rename later if needed) | THE TURN → MORAL SHADOW | Dark, somber, low sustained strings, distant ominous brass, slow mournful tempo, restrained — no percussion climax |
| "هابر-بوش — الإرث" (Haber-Bosch — Legacy) | LEGACY → ENDING/CTA | Warm, hopeful, resolving orchestral strings, gentle rising piano, quiet satisfying resolution |

## Sound-effect beds (3)
1. **Laboratory ambience** (Scene "The Challenge" — 1905 lab): glass apparatus clinking, gas burner hiss, bubbling liquid, valve squeak, quiet ticking clock.
2. **WWI trench battlefield ambience, restrained** (Scene "Moral Shadow" — Ypres): distant low artillery rumble, wind, faint gas-canister hiss — no screaming, no explicit violence, kept deliberately understated per the research brief's caution on this scene.
3. **Factory ambience, 1913** (Scenes "Scaling Up" / "The Turn" — BASF Oppau): deep rhythmic machinery thrum, steam venting, metal clanging, pressure-vessel hum, muffled workers' voices.

## Next steps
- Pick the best take of each cue/SFX bed in Suno and bring the audio into the sandbox for the final mix.
- Rename the garbled "Moral Shadow" track title on the Suno side for clarity (cosmetic only, does not affect the audio).

## Audio-extraction note (this session)
Unlike ElevenLabs (whose generations have a direct signed CDN URL retrievable via `creative_get_generations`, so narration was downloaded cleanly with plain `curl`), Suno's audio plays from a page-created `blob:` URL that a content-script `fetch()`/`XMLHttpRequest` cannot resolve (isolated-world restriction), and Suno's real CDN URL (cloudfront) is outside the sandbox's network allowlist, so plain `curl` fails too.
A real-time capture workaround was prototyped and works in principle: connect the page's `<audio>` element to a Web Audio `ScriptProcessorNode`, record raw PCM while the track plays, downsample or encode to WAV, and export via chunked Base64 through the browser console (the same relay method used for the Gemini video frames). A first attempt produced a WAV, but Suno's player auto-advanced to the next queued track partway through the capture, so the result mixed two songs together and was discarded rather than used.
This path is viable but needs the player's autoplay/queue-advance disabled (or the capture loop capped strictly to one track's real duration) before it's used for real — not yet done. Narration audio did not need this workaround and is already fully downloaded (see narration_audio/ and narration_log.md). Music/SFX download remains the next step before final mixing.
