# 3번 역 마스터·노선 순서·승하차

이슈 #3 · 먼저 읽기: [00-start](00-start.md), [데이터 계약](../data-contract.md)의 `stations.json`, `lines.json`, `ridership.json`

## 한 줄로
**역 이름표(좌표)**, **노선별 역 순서**, **시간대별 타는 사람 수**를 만든다. 다른 데이터가 전부 여기에 맞춰 붙는다.

## 왜 중요한가
데이터마다 역 이름 표기가 조금씩 다르다 (`서울역`/`서울`, `군자(능동)`/`군자`).
여기서 이름을 하나로 맞추지 않으면 막차·승객·버스가 지도 위에서 서로 안 붙는다. **팀에서 가장 많이 막히는 곳**이라 꼼꼼함이 제일 중요하다.

## 미리 알아 둘 것
- 역 좌표: `subwayStationMaster` (784행, `BLDN_ID`·`BLDN_NM`·`ROUTE`·`LAT`·`LOT`)
- 역 코드·순서: `SearchInfoBySubwayNameService` (`STATION_CD`·`STATION_NM`·`LINE_NUM`·`FR_CODE`)
  - `BLDN_ID` 와 `STATION_CD` 는 같은 번호 체계다 (서울역 1호선 = `0150`) → **이름 말고 코드로 붙인다**
  - `FR_CODE`(예: 강남 `222`)로 정렬하면 노선 위 역 순서가 된다
- 승하차: `CardSubwayTime/{YYYYMM}` → `HR_23_GET_ON_NOPE`, `HR_0_GET_ON_NOPE`, `HR_1_GET_ON_NOPE`
  - 값은 **한 달 합계**. 그 달 일수(`days`)를 같이 저장한다
  - 역 이름(`STTN`)과 노선 이름(`SBWY_ROUT_LN_NM`)만 있고 코드가 없다 → **여기서 이름 맞추기가 필요**
  - 환승역은 한 노선에 몰려 잡힐 수 있다 → 역 단위로 합친다
- 범위: `1호선`~`8호선` (+ `9호선` 2·3단계). 코레일 구간은 뺀다

## 할 일
1. `pipeline/collect_stations.py` → `data/out/stations.json`, `data/out/lines.json`
   - 역 ID = 정규화한 이름 (괄호 떼기, 앞뒤 공백 제거)
   - 같은 이름의 여러 노선 → 한 역으로 묶고 `lines: {"2": "0222", ...}`
   - `lines.json`: 노선마다 FR_CODE 순서대로 역 이름. 2호선은 순환(`loop: true`), 지선은 `"2a"` 따로
2. `pipeline/collect_ridership.py` → `data/out/ridership.json`
3. **못 맞춘 이름 목록**을 출력하고 `pipeline/name_fix.json` 에 손으로 짝을 적어 해결 (`{"서울": "서울역"}` 처럼)

## AI에게 줄 말

```
나는 개발 처음이고 서울 지하철 막차 지도 프로젝트에서 역 데이터 담당이야.
#file:pipeline/seoul_api.py #file:docs/data-contract.md #file:data/fixtures/stations.json #file:data/fixtures/lines.json
pipeline/collect_stations.py 를 만들어 줘.
1) fetch_all("subwayStationMaster") 로 좌표, fetch_all("SearchInfoBySubwayNameService") 로 코드·FR_CODE 받기
2) ROUTE / LINE_NUM 이 1~8호선인 것만
3) BLDN_ID == STATION_CD 로 두 데이터를 붙이기
4) 역 이름 정규화(괄호 제거) 해서 같은 이름은 한 역으로: {id, name, lat, lon, lines:{노선번호: 코드}}
5) 노선마다 FR_CODE 순서로 역 이름을 나열해 lines.json 만들기 (색은 노선 공식 색에 가깝게, 2호선 loop true)
6) 둘 다 data/out 에 저장
표준 라이브러리만, 코드 아래에 초보자 설명.
```

```
#file:pipeline/seoul_api.py #file:docs/data-contract.md #file:data/fixtures/ridership.json
pipeline/collect_ridership.py 를 만들어 줘.
- 인자로 월(YYYYMM)을 받고, fetch_all("CardSubwayTime", 월)
- 노선 이름이 1호선~8호선인 행만, HR_23/0/1 GET_ON 을 on_23/on_0/on_1 로
- 역 이름은 data/out/stations.json 의 id 와 맞추고, 못 맞춘 이름은 마지막에 목록 출력
- pipeline/name_fix.json 이 있으면 그 짝으로 이름을 바꿔서 다시 맞추기
- 같은 역은 노선 상관없이 합치기, 그 달 일수(days)도 저장
```

```
2호선은 본선이 순환이고 성수지선, 신정지선이 따로 있어. FR_CODE 로 이걸 어떻게 구분하는지
데이터를 보고 확인하는 방법을 알려 줘. 확인한 다음 lines.json 에 "2a", "2b" 로 따로 넣고 싶어.
```

## 확인 방법
```bash
python3 pipeline/collect_stations.py
python3 pipeline/collect_ridership.py 202610
```
- 못 맞춘 이름 목록이 **0개**가 될 때까지 `name_fix.json` 채우기
- 강남, 서울역, 군자를 찾아서 좌표를 지도 앱과 비교
- 5번 담당에게 `lines.json` 으로 노선이 제대로 그려지는지 확인 부탁

## 자주 막히는 곳
- **같은 이름 다른 역**: 5호선 `양평` vs 경의중앙 `양평`. 범위 밖 노선은 걸러지니 대부분 괜찮다
- **승하차 최신 달이 없음**: 보통 두 달 전 것이 최신. `check_sources.py` 가 고른 달을 참고
- **9호선**: 1단계(개화~신논현)는 운영사가 달라 범위 밖. 2·3단계 포함 여부는 리드와 상의

## 발표 때 설명할 것
- 이름 대신 코드로 붙인 이유, 이름 불일치를 어떻게 해결했는지 (몇 건이었는지)
- 승하차가 월 합계라는 점과 하루 평균으로 바꾼 방법
