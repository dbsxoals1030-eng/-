# MBTI Shorts template (minimal editorial style)

40s, 1080x1920, 30fps. HTML motion graphics -> Playwright frames -> ffmpeg, with synthesized BGM and Korean TTS voice-over.

## Style rules (keep for every MBTI short)
- Palette: warm greige `#ECE8E1` + charcoal `#1B1A19` + ONE accent terracotta `#D4573B`. No gradients, no emoji, no particles.
- Type: Pretendard (fonts/), huge tight-tracked Black headlines, small letter-spaced captions, left-aligned editorial layout (margin 90px).
- Characters: ivory fill, 6px charcoal outline, dot eyes, one accent prop per type (see `M` in index.html).
- Motion: masked text reveals (RV), hairlines that draw, count-up gauge, bottom-to-top wipe between scenes. #1 scene uses the dark theme.
- Keep content between y=150 and y=1580 (Shorts UI safe zone). Progress line at the top.
- Voice: ko-KR-SunHiNeural, rate +24%, MBTI spoken colloquially (잇티제, 잇팁, 인프제, 인팁, 인티제, 엔팁...). BGM ducks under voice.
- Beat grid: 96 BPM (0.625s). Intro 3.75s, 5 ranks x 6.25s, outro 5s.

## Episode modes (episodes/*.json)
- `ranking` — TOP5 of types with a gauge (`pct`, `gauge_label`). Example: `hard-to-get-top5.json`, `09-crush-behavior-top5.json`.
- `types` — 5 types in the given order, no ranking/gauge, up to 3 traits + a one-line summary (`tip_label`). Examples: `01-weekend-by-type.json`, `10-breakup-by-type.json`.
- `list` — one subject (usually ISTP, the channel mascot) with N items (5 or 7, 4–7 supported): `title`, `desc`, `icon`, `mood`, `short`, optional `chip`, voice [title, desc]. Examples: `02`–`08`.
- Optional `intro` {cap,l1,l2,l3,mood} (text auto-shrinks to fit); `<b>word</b>` = accent color. ISTP moods: normal sleepy annoyed shock smirk sweat. Icons: see `ICON` in mascots.js.

## Files
- `mascots.js` (all 16 types), `index.html` (scenes; data from `episode.js`), `episodes/*.json` (content + voice lines), `audio.py` (BGM/SFX), `vo_build.py`+`tts.py` (voice, ducking), `build.sh`, `topics.json` + `DAILY.md` (daily automation), `channel/` (profile 800px + banner 2560x1440 for channel 잇팁인데요).

## To make a new episode
1. Copy `episodes/hard-to-get-top5.json`, edit the content (see DAILY.md for the rules).
2. `./build.sh episodes/<slug>.json out.mp4`
Notes: edge-tts needs network; tts.py points certifi at /root/.ccr/ca-bundle.crt for the sandbox proxy (remove that line elsewhere).
