# 모션 이코노미 쇼츠 제작 도구

`spec.json`(장면별 대본·헤드라인·그래픽)을 넣으면 **30초 내외 9:16 쇼츠 영상 + 썸네일**을 만든다.

```bash
pip install gTTS pillow          # ffmpeg 필요
python3 shorts.py specs/example_seoulsemi.json --check   # TTS 길이만 확인 (목표 28~32초)
python3 shorts.py specs/example_seoulsemi.json           # 렌더: <out>/video.mp4, <out>/thumbnail.png
```

## 고정 규칙 (사용자 지시 · 모든 쇼츠에 적용)
- **내레이션 1.5배속** (`tempo` 1.5, 바꾸지 말 것). 길이 약 30초 → 원본 TTS는 합계 약 42~45초 분량의 대본.
- 1080×1920, 30fps. 채널명 "모션 이코노미" + "투자 판단과 책임은 본인에게 있습니다" 문구.
- 스타일: 회색 그라데이션 배경, 상단 2줄 헤드라인(1줄 **노랑**, 2줄 **흰색**, 검정 외곽선), 흰 정보 카드, 하단 큰 자막.
- 첫 장면은 썸네일로도 쓰인다(hook). 특정 기업 주제면 **공식 로고**를 첫 장면(`stat_card.logo`)과 썸네일에 넣는다.
  로고는 `assets/`에 둔다(상표 · 기업 식별 용도로만 사용).
- 한국 증시 색: 상승 빨강 / 하락 파랑.
- 숫자는 **확인된 출처만** 사용. 장중 수치는 "장 초반" 등 기준 시각 표기. `line` 그래픽에는 실제 시계열만. 기사 날짜 확인(옛 기사 제외).
- TTS는 gTTS(`lang="ko"`). edge-tts는 샌드박스 프록시에서 TLS 오류 → 사용 금지(TLS 검증 끄지 말 것).

## spec 형식
```json
{"out": "out/<이름>", "thumb": {"line1": "노랑 줄", "line2": "흰 줄", "tag": "#태그"},
 "scenes": [{"head": ["노랑 줄", "흰 줄"], "narration": "대본(쉼표 단위로 자막 분할)",
             "graphic": {"type": "stat_card|stat_grid|bars|bullets|big_text|line", ...}}]}
```
| type | 파라미터 |
|---|---|
| `stat_card` | `name, logo?, from, to, decimals?, unit?, badge?, note?` (가격 카운트업, 등락률 자동 계산) |
| `stat_grid` | `title?, tiles:[{label, value, change, dir: up/down/flat}]` 최대 5행 (지수·환율 등) |
| `bars` | `title, rows:[{label, value, text, color: up/down/gray}], note?` 최대 4행 |
| `bullets` | `title?, items:[문장]` 최대 4개 |
| `big_text` | `big, sub?, color?` |
| `line` | `title?, values:[실제 데이터], start_label?, end_label?, note?` |

장면은 5~7개, 장면당 대본 한 문장 안팎. 헤드라인은 짧게(한 줄 12자 안팎).

## 매일 2회 정기 제작 (한국 거래일만)
휴장일(주말·공휴일·임시휴장)에는 만들지 않는다. 먼저 "오늘 한국거래소 휴장" 검색으로 확인.
1. **장전 영상** (예: 08:30 업로드용, 07:50 시작): 간밤 미국 증시 마감(나스닥·S&P500·다우), 환율·유가 등 변수,
   오늘 장 전 핵심 이슈·테마. 주목 종목은 근거 기사가 있는 것만.
2. **장마감 영상** (15:30 마감 후 시작): 코스피·코스닥 마감 요약(`stat_grid`), 오늘 상한가/급등 종목과 **이유**(`stat_card`+`bullets`), 내일 체크포인트.
각 영상은 `video.mp4`와 `thumbnail.png`를 만든 뒤 프레임을 꺼내 육안 검수하고 사용자에게 전달한다.
