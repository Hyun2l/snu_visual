# 2번 시간표·막차 수집

이슈 #2 · 먼저 읽기: [00-start](00-start.md), [데이터 계약](../data-contract.md)의 `last_trains.json`

## 한 줄로
서울시 API에서 **모든 역의 막차 시각**을 받아 `data/out/last_trains.json` 하나로 만든다.

## 왜 중요한가
이 파일이 없으면 지도가 아무것도 못 한다. MVP(1단계)의 핵심 데이터다.

## 미리 알아 둘 것
- API 주소 모양: `http://openapi.seoul.go.kr:8088/{키}/json/SearchLastTrainTimeByIDService/{시작}/{끝}/{역코드}/{요일}/{방향}/`
  - 역코드: `0222` (강남 2호선) 같은 4자리 `STATION_CD`
  - 요일 `WEEK_TAG`: 1 평일, 2 토요일, 3 휴일 → **우리는 1만**
  - 방향 `INOUT_TAG`: 1, 2 (상행·내선 / 하행·외선) → **둘 다**
- 시각은 `"24:46:30"` 처럼 24를 넘는다. 변환은 이미 있는 `to_min()` 을 쓴다 → `1486.5`
- 공통 호출 코드 `pipeline/seoul_api.py` 의 `call()`, `fetch_all()` 을 그대로 쓴다. 새로 짜지 않는다
- 역코드 목록은 `SearchInfoBySubwayNameService` 에서 받는다 (`LINE_NUM` 이 `01호선`~`08호선`인 것. `09호선`은 시간표가 오는지 확인 후 결정)
- sample 키는 5건만 준다. **꼭 개인 인증키**를 `.env` 에 넣고 돌린다

## 할 일
1. `python3 pipeline/check_sources.py` 로 API가 살아 있는지 확인
2. `pipeline/collect_timetable.py` 만들기
   - 역코드 목록 받기 → 역코드 × 방향(1,2) 마다 막차 API 호출
   - 원본은 `data/raw/last/역코드_방향.json` 에 저장 (이미 있으면 건너뛰기 → 중간에 끊겨도 이어서 돌릴 수 있음)
   - 행선지(`SUBWAYENAME`)마다 가장 늦은 `LEFTTIME` 한 줄만 남겨서 `data/out/last_trains.json`
3. 빠진 역 목록 출력 (응답이 비었거나 에러 난 역코드)

## AI에게 줄 말

```
나는 개발 처음이고 서울 지하철 막차 지도 프로젝트에서 시간표 수집 담당이야.
#file:pipeline/seoul_api.py #file:docs/data-contract.md #file:data/fixtures/last_trains.json
pipeline/collect_timetable.py 를 만들어 줘.
1) fetch_all("SearchInfoBySubwayNameService") 로 역 목록을 받아 LINE_NUM 이 01호선~08호선인 STATION_CD 만 고르기
2) 각 STATION_CD 와 INOUT_TAG 1, 2 에 대해 fetch_all("SearchLastTrainTimeByIDService", 코드, "1", 방향) 호출
3) 응답 원본을 data/raw/last/{코드}_{방향}.json 에 저장하고, 파일이 이미 있으면 호출하지 말고 읽기
4) 행선지(SUBWAYENAME)별로 to_min(LEFTTIME) 이 가장 큰 행만 남겨서
   계약 모양(station, line, code, week, dir, dest, t)으로 data/out/last_trains.json 저장
5) 실패하거나 빈 역코드는 마지막에 목록으로 출력
station 은 역 이름에서 괄호 부분을 뗀 이름, line 은 "02호선" → "2" 로.
표준 라이브러리만 쓰고, 줄마다 무슨 일을 하는지 초보자 말로 설명해 줘.
```

```
방금 코드를 처음엔 역 3개만 돌려 보고 싶어. 개수를 제한하는 옵션(--limit 3)을 넣어 줘.
```

## 확인 방법
```bash
python3 pipeline/collect_timetable.py --limit 3     # 먼저 3개만
python3 pipeline/collect_timetable.py               # 전체 (몇 분 걸림)
```
- `data/out/last_trains.json` 을 열어서 강남 2호선을 찾고, 카카오맵 막차와 비교
- 역 수가 3번 담당의 `stations.json` 과 비슷한지 (약 280개)

## 자주 막히는 곳
- **`ERROR-335`**: sample 키로 5건 넘게 요청함 → `.env` 에 개인 키 넣기
- **`INFO-200` 데이터 없음**: 그 역·방향에 열차가 없음 (종점 등). 정상일 수 있다. 목록에만 남기기
- **너무 오래 걸림**: 요청 사이 0.1초 쉬기가 이미 있다. 중간에 끊겨도 원본 저장 덕에 이어서 돈다
- `data/raw/` 는 커밋되지 않는다 (일부러 막아 둠). `data/out/` 만 커밋

## 발표 때 설명할 것
- 어떤 API를 몇 번 불렀고, 원본을 저장해 둔 이유 (재실행, 호출 제한)
- 자정 넘는 시각을 분으로 바꾼 방법
