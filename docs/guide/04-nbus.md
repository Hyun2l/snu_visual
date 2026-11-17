# 4번 심야버스

이슈 #4 · 먼저 읽기: [00-start](00-start.md), [데이터 계약](../data-contract.md)의 `nbus.json`

## 한 줄로
막차가 끊긴 역 근처에 **어떤 N버스가 서는지** 데이터를 만든다. 지도에서 귀여운 버스 아이콘으로 나온다.

## 왜 중요한가
"막차 놓쳤다 → 그럼 어떻게 가지?"에 답하는 부분이라 사용자 입장에서 가장 쓸모 있다.
대신 **데이터 출처가 아직 확실하지 않다.** 그래서 첫 주에 출처부터 정하는 게 이 역할의 핵심이다.

## 미리 알아 둘 것
- 버스 정류장 좌표: `busStopLocationXyInfo` (서울 열린데이터광장, 11,236개, 확인됨)
- **어떤 노선이 어느 정류장에 서는지**는 이 API에 없다. 후보는 두 가지:
  - A. 서울 버스 노선정보 API (공공데이터포털 data.go.kr, 서울 열린데이터광장 OA-1095). 노선 목록 → 노선별 경유 정류소. **키 발급이 막혀 있었다는 공지가 있었음 → 지금 되는지 먼저 확인**
  - B. 손으로 조사: 주요 역 20~30곳만 카카오맵·네이버지도에서 N버스 정류장을 찾아 CSV로 적기
- 실시간 도착 시간은 **보너스**. 기본은 "N61 · 140m" 처럼 노선과 걷는 거리만

## 할 일
1. **첫 이틀: 출처 정하기**
   - data.go.kr 가입 → "서울특별시 노선정보조회" 검색 → 활용 신청이 되는지 확인
   - 되면 A, 안 되면 B. 결과를 이슈 #4 댓글로 남기기
2. A라면 `pipeline/collect_nbus.py`: N으로 시작하는 노선만 → 경유 정류소 → 정류장 좌표
3. B라면 `data/manual/nbus.csv` 작성 (열: `station,route,stop_name`)
4. 공통: 역(`stations.json`)에서 **반경 300m 안 정류장**을 거리 계산으로 붙여 `data/out/nbus.json`

## AI에게 줄 말

```
나는 개발 처음이고 서울 지하철 막차 지도 프로젝트에서 심야버스 담당이야.
서울 N버스(심야버스)가 어느 정류장에 서는지 공공데이터로 얻고 싶어.
공공데이터포털의 "서울특별시_노선정보조회 서비스"로 노선 목록에서 N으로 시작하는 노선을 찾고,
노선별 경유 정류소 목록을 받는 순서를 초보자 기준으로 알려 줘.
요청 주소 모양과 필요한 인자, 응답에서 봐야 할 필드를 정리해 주고,
모르는 부분은 추측하지 말고 "공식 문서에서 확인 필요"라고 표시해 줘.
```

```
#file:docs/data-contract.md #file:pipeline/seoul_api.py #file:data/fixtures/stations.json #file:data/fixtures/nbus.json
pipeline/build_nbus.py 를 만들어 줘.
- 입력: data/out/stations.json (없으면 data/fixtures/stations.json), data/manual/nbus.csv (station,route,stop_name)
- fetch_all("busStopLocationXyInfo") 로 정류장 좌표(XCRD=경도, YCRD=위도)를 받고 data/raw/bus_stops.json 에 저장해서 재사용
- csv 의 stop_name 과 정류장 이름(STOPS_NM)을 맞추고, 역 좌표와의 거리(m)를 하버사인 공식으로 계산
- 300m 넘으면 경고 출력
- 계약 모양 {station, routes:[{no, stop_id, stop_name, walk_m}]} 으로 data/out/nbus.json
표준 라이브러리만, 하버사인 공식이 뭔지도 쉽게 설명해 줘.
```

## 확인 방법
```bash
python3 pipeline/build_nbus.py
```
- 강남, 홍대입구, 신림 같은 큰 역을 지도 앱에서 직접 찾아 N버스 번호가 맞는지 확인
- `walk_m` 이 말이 되는지 (보통 50~300m)

## 자주 막히는 곳
- **같은 이름 정류장이 여러 개** (양방향): 역에서 가까운 쪽 하나만 쓰거나 둘 다 적기
- **좌표 순서 헷갈림**: `XCRD` 가 경도(127.x), `YCRD` 가 위도(37.x)
- **키 발급 막힘**: 바로 B(손 조사)로 간다. 30곳이면 반나절이면 된다. 발표 때 "왜 손으로 했는지" 설명하면 된다

## 발표 때 설명할 것
- 데이터 출처를 어떻게 정했는지 (A/B와 이유)
- 역과 정류장을 거리로 이은 방법
