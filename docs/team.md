# 팀 분담과 브랜치

## 규칙

- `main` 은 항상 열리는 상태로 둔다. 직접 푸시하지 말고 **각자 이름 브랜치 → PR → 리드가 머지**한다.
- 이름 브랜치: `hyun`(리드), `LEE`, `Min`, `Walnut`, `jun`, `kdkook`. 모두 지금 `main` 과 같은 상태에서 시작한다.
- 작업 전에 `git pull origin main` 으로 최신을 받는다. PR은 작게, 자주.
- 남의 폴더는 고치지 않는다. 고쳐야 하면 PR 설명에 쓰고 담당자를 태그한다.
- 데이터 형식은 [데이터 계약](data-contract.md)이 기준이다. 바꾸려면 리드와 먼저 얘기한다.
- API 키는 `.env` 에만 넣는다 (`.env.example` 참고). 키가 들어간 커밋은 바로 리드에게 알린다.
- **평가에 "구현 이해"가 있다.** Copilot이 짠 코드도 담당자가 한 줄씩 설명할 수 있어야 머지한다.

## 처음 할 일 (누구나)

```bash
git clone https://github.com/Hyun2l/snu_visual.git
cd snu_visual
cp .env.example .env          # 키가 있으면 넣기, 없으면 sample 키로 5건만 돈다
python3 pipeline/check_sources.py
git switch <내 이름 브랜치>   # 예: git switch Min
```

서울 열린데이터광장 인증키는 각자 발급받는다 (data.seoul.go.kr → 인증키 신청).

## 6명 분담

| # | 역할 | 담당 (이름 브랜치) | 폴더 | 결과물 | 끝났다는 기준 |
|---|---|---|---|---|---|
| 1 | 리드: 계약·막차 계산·머지 | `hyun` | `pipeline/build_*.py` | `data/out/last_trains.json` 검증, 역별 대표 막차 규칙 | 역 20곳을 카카오맵 막차 조회와 대조해 ±1분 |
| 2 | 시간표 수집 | 정해지면 적기 | `pipeline/collect_timetable.py` | 범위 안 모든 역·방면의 막차 원본 → `last_trains.json` | 1~9호선 역 수가 역 마스터와 일치, 누락 역 목록 0 |
| 3 | 역 마스터·승하차 | 정해지면 적기 | `pipeline/collect_stations.py`, `collect_ridership.py` | `stations.json`, `ridership.json` | 세 데이터의 역 이름이 전부 매칭(못 맞춘 이름 목록 0) |
| 4 | 심야버스 | 정해지면 적기 | `pipeline/collect_nbus.py`, `data/manual/` | `nbus.json` | 출처 확정, 주요 역 20곳 이상 N버스 정류장 연결 |
| 5 | 지도 화면 | 정해지면 적기 | `web/` | 프로토타입을 모듈로 나누고 JSON 읽기 | fixtures → out 으로 경로만 바꿔도 동작, 휴대폰 폭 확인 |
| 6 | 채팅·배포 | 정해지면 적기 | `web/chat.js`, `supabase/` | Supabase 테이블·RLS, 실시간 말풍선, GitHub Pages | 배포 주소에서 팀원 2명이 서로 한마디 확인 |

발표자료와 시연 영상은 각자 맡은 부분을 한 장씩 쓴다. 정리는 6번이 한다.

역할은 GitHub 이슈 6개로 올라가 있다. 맡을 사람이 이슈에 본인을 Assignee로 걸고 위 표에 이름을 적는다.

## 순서

1. **1단계 (MVP)**: 실제 역 좌표 + 실제 막차 + 시간 슬라이더 + 배포 주소. 2·3·5번이 핵심이다.
2. **2단계**: 승객 점(실데이터), 채팅, N버스 정적 안내.
3. **보너스**: 도달 범위(환승 포함), N버스 실시간 도착, "놓쳤어요" 집계.

1단계가 늦어지면 보너스는 통째로 버리고, 채팅은 예시 말풍선으로만 시연한다.

## 이미 확인한 것 (`pipeline/check_sources.py`)

- 시간표 API에 열차번호가 온다 → 도달 범위 계산이 가능하다
- 막차 API는 행선지마다 따로 준다 (`24:46:30` 식 자정 넘김 표기)
- 승하차 데이터에 23·0·1시 칸이 있고, 값은 월 합계다
- 역 좌표와 시간표 역 코드는 같은 체계다
- 버스 정류장 좌표는 있다. **N버스 노선↔정류장 연결은 출처 미확정** (4번 첫 과제)
- sample 키는 한 번에 5건까지만 준다. 전체 수집에는 개인 키가 필요하다
