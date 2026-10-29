# Daily run: make today's "잇팁인데요" MBTI Short (finish before 11:00 KST)

Channel: **잇팁인데요** (YouTube Shorts, MBTI rankings). Style is fixed — see README.md. Never publish/upload anything; just deliver the files.

## Steps
1. `TZ=Asia/Seoul date +%F`. Topic index = (days since 2026-10-30) mod `len(topics.json)`; take that entry from `topics.json` (title_prefix, caption, gauge_label, gauge_unit). If the previous day's topic is unknown, that's fine: the rotation never repeats within 40 days.
2. `pip install -q edge-tts`; `which ffmpeg node`; Playwright + Chromium are preinstalled (never run `playwright install`).
3. Write `episodes/<YYYYMMDD>.json` (copy `episodes/hard-to-get-top5.json` as the schema). Fill TOP 5 for the topic. Entries are ordered 5th → 1st.
   - 5 DISTINCT types; pick whichever 5 fit the topic best (any of the 16; mascots exist for all).
   - `pct` increases from 5th to 1st, ending at 95–99 (e.g. 72,80,87,93,98). Stay playful, not insulting; it's an opinion ranking, so the disclaimer stays.
   - `nick` ≤ 9 chars. Each `traits` ≤ 15 chars, wrap 1 keyword in `<b>`. `tip` ≤ 14 chars, wrap 1 keyword in `<b>`.
   - `intro_q`: ["과연 ","1위","는?"] (or another short teaser in 3 parts). `intro_voice` reads the title; spell "엠비티아이" and "탑 파이브".
   - `voice` per rank = [rank+type, nickname + one trait (≤ 20 chars), tip]. Rank words: 오 위/사 위/삼 위/이 위/대망의 일 위. Spoken types: ISTJ 잇티제, ISFJ 잇프제, INFJ 인프제, INTJ 인티제, ISTP 잇팁, ISFP 잇프피, INFP 인프피, INTP 인팁, ESTP 엣팁, ESFP 엣프피, ENFP 엔프피, ENTP 엔팁, ESTJ 엣티제, ESFJ 엣프제, ENFJ 엔프제, ENTJ 엔티제.
   - `outro`: keep the same CTA/disclaimer (title like ["내 MBTI는 ","몇 위","?"]).
4. `./build.sh episodes/<YYYYMMDD>.json /home/user/out_<YYYYMMDD>.mp4` (≈ 5 min). If vo_build prints `WARN too long` or a tempo above ~x1.3, shorten that voice line / re-run. Do not disable TLS verification (tts.py already trusts the sandbox CA).
5. QA: extract frames with ffmpeg at ~1s, 5s, 17s, 30s, 37s and LOOK at them: no text overflow/overlap, correct types on the right ranks, 40.0s duration, audio stream present. Fix and rebuild if needed.
6. Deliver with SendUserFile (status proactive, display render): the MP4 and `_thumb.jpg`. Final message in Korean: ranking summary (5→1, one line each), suggested YouTube title (≤ 40 chars, hook first), description (2 lines) and hashtags (#Shorts #MBTI #잇팁인데요 + topic tags). Mention that the ranking is for fun.
