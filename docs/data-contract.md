# 데이터 계약

파이프라인(Python)이 `data/out/*.json` 을 만들고, 웹은 그 파일만 읽는다.
실데이터가 나오기 전에는 `data/fixtures/` 의 가짜 파일로 개발한다. **모양은 둘이 같아야 한다.**
형식을 바꾸려면 리드에게 먼저 말하고 이 문서부터 고친다.

## 공통 규칙

1. **역 ID = 정규화한 역 이름** (`"서울역"`, `"강남"`). 괄호 표기는 뗀다: `"군자(능동)"` → `"군자"`.
   노선별 코드는 `lines` 안에 따로 둔다. 같은 이름의 다른 역(예: 5호선 양평 vs 경의중앙 양평)은 범위 밖이라 지금은 무시한다.
2. **시각 = 운행일 00:00부터 센 분(float)**. 자정을 넘기면 1440 이상: `24:46:30` → `1486.5`.
   변환은 `pipeline/seoul_api.py` 의 `to_min()` 하나만 쓴다.
3. **범위**: 서울교통공사 운영 1~8호선 + 9호선 2·3단계. 평일(`week: "1"`)부터 하고 토·휴일은 나중에 한다.
4. 노선 ID는 문자열 `"1"`~`"9"`.
5. 원본은 `data/raw/`(git 제외), 결과는 `data/out/`(git 포함, 작게 유지).

## stations.json — 담당: 역 마스터

```json
[{ "id": "강남", "name": "강남", "lat": 37.4979, "lon": 127.0276, "lines": { "2": "0222" } }]
```
- 출처: `subwayStationMaster`(좌표, BLDN_ID), `SearchInfoBySubwayNameService`(STATION_CD)
- BLDN_ID 와 STATION_CD 는 같은 코드 체계다 (서울역 1호선 = `0150`, 둘 다 확인함).

## last_trains.json — 담당: 시간표 수집 → 리드 검증

```json
[{ "station": "강남", "line": "2", "code": "0222", "week": "1", "dir": "1", "dest": "서울대입구", "t": 1486.5 }]
```
- 출처: `SearchLastTrainTimeByIDService/{STATION_CD}/{WEEK_TAG}/{INOUT_TAG}`
- **행선지(dest)마다 한 줄.** 같은 강남·내선이라도 신도림행 24:00, 서울대입구행 24:46처럼 다르다.
  화면에서 "이 역 막차"는 리드가 정한 규칙(예: 그 방면 가장 늦은 열차)으로 고른다.

## ridership.json — 담당: 역 마스터

```json
{ "month": "202610", "days": 31, "rows": [{ "station": "강남", "line": "2", "on_23": 0, "on_0": 0, "on_1": 0 }] }
```
- 출처: `CardSubwayTime/{YYYYMM}` (OA-12252)
- 값은 **월 합계**다. 하루 평균은 웹에서 `/ days` 로 나눈다.
- 환승역은 개찰구 기준이라 한 노선에 몰려 잡힐 수 있다 (충무로 3호선 23시 = 2명처럼). 역 단위로 합쳐서 쓴다.

## nbus.json — 담당: 심야버스

```json
[{ "station": "강남", "routes": [{ "no": "N13", "stop_id": "122000123", "stop_name": "강남역", "walk_m": 140 }] }]
```
- 정류장 좌표: `busStopLocationXyInfo` (확인함)
- **노선↔정류장 연결은 아직 출처 미확정.** 후보: 서울 버스 노선정보 API(OA-1095, 공공데이터포털 키 필요).
  키 발급이 막혀 있으면 주요 역 20곳만 직접 조사해 `data/manual/nbus.csv` 로 넣는다.
- 도착 시간(분)은 실시간 API가 필요해서 보너스. 기본은 노선 번호와 걷는 거리만 보여 준다.

## 채팅 (Supabase) — 담당: 채팅·배포

- 표: `messages(id, uid, station, line, kind, text, created_at)`, `members(uid, is_admin)`, `settings(key, value)`
- 전체 정의와 권한 규칙은 [`supabase/schema.sql`](../supabase/schema.sql), 설정 순서는 [`supabase/README.md`](../supabase/README.md)
- 웹 쪽 연결은 [`web/chat.js`](../web/chat.js) 의 `connectChat()`. 화면이 받는 메시지 모양:
  ```js
  { id, uid, station: "강남", line: "2", kind: "text" | "preset", text: "탔어요", at: 1763380000000 }
  ```
- 입장은 익명 로그인 + 입장 코드. 이메일은 받지 않는다.
- 프론트에는 anon 키만 넣는다. service_role 키는 절대 커밋하지 않는다.
