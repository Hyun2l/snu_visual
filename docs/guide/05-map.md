# 5번 지도 화면

이슈 #5 · 먼저 읽기: [00-start](00-start.md), [데이터 계약](../data-contract.md), 프로토타입 [`makcha-demo/index.html`](../../makcha-demo/index.html)

## 한 줄로
프로토타입 한 장짜리 화면을 **파일 몇 개로 나누고**, 가짜 숫자 대신 **JSON 데이터를 읽게** 바꾼다.

## 왜 중요한가
평가의 "시각화 가독성"과 "웹 기능 완성도"가 이 화면에서 나온다. 사람들이 실제로 보는 건 이것뿐이다.
좋은 소식: **모양은 이미 다 있다.** 새로 그리는 게 아니라 옮기고 연결하는 일이다.

## 미리 알아 둘 것
- 프로토타입은 HTML·CSS·JS가 한 파일에 다 있다 (라이브러리 없음, 지도는 `<canvas>` 에 직접 그림)
- 데이터는 이미 계약 모양으로 `data/fixtures/` 에 있다: `stations.json`, `lines.json`, `last_trains.json`, `ridership.json`, `nbus.json`
- 파일을 나누면 `<script type="module">` 을 쓰게 되는데, **모듈은 파일을 더블클릭해서 열면 안 돌아간다.** 꼭 로컬 서버로 연다:
  ```bash
  python3 -m http.server 8000
  # 브라우저: http://localhost:8000/web/
  ```
- 채팅 연결 코드는 6번이 `web/chat.js` 로 이미 만들어 둠. 붙일 때 같이 작업

## 목표 구조
```
web/
  index.html    화면 뼈대 + CSS (프로토타입의 HTML·style 그대로)
  data.js       JSON 읽기. 폴더 경로 한 줄(DATA_DIR)만 바꾸면 fixtures ↔ out 전환
  map.js        캔버스에 노선·역·승객 점 그리기
  bubbles.js    한마디 말풍선 → 열차 애니메이션
  bus.js        심야버스 아이콘
  panel.js      오른쪽 내 역 카드, 시간 슬라이더
  main.js       위 파일들을 불러서 시작
  chat.js       (6번) 채팅 연결
```

## 할 일 (작게 나눠서 하나씩 PR)
1. `web/index.html` 에 프로토타입을 그대로 복사해서 로컬 서버로 열리는지 확인 → **PR 1**
2. JS를 위 구조대로 나누기. 동작은 프로토타입과 똑같아야 함 → **PR 2**
3. `data.js` 로 fixtures JSON 읽게 바꾸고 하드코딩된 `ST`, `LINES`, `NB` 지우기 → **PR 3**
4. 휴대폰 폭(375px)에서 확인, 겹치는 글자 정리 → **PR 4**
5. 실데이터가 들어오면 `DATA_DIR` 을 `../data/out/` 으로

## AI에게 줄 말

```
나는 개발 처음이고 서울 지하철 막차 지도 프로젝트에서 화면 담당이야.
#file:makcha-demo/index.html
이 파일은 HTML, CSS, JS가 한 파일에 있는 프로토타입이야. 먼저 이 코드가 어떤 부분들로
이루어져 있는지(데이터, 지도 그리기, 말풍선, 버스, 오른쪽 패널, 시간)를 함수 이름과 함께
초보자 말로 정리해 줘. 코드는 아직 고치지 마.
```

```
#file:makcha-demo/index.html
이 프로토타입의 <script> 를 ES 모듈 파일로 나누고 싶어:
web/data.js, map.js, bubbles.js, bus.js, panel.js, main.js
동작은 지금과 완전히 같아야 해. 빌드 도구 없이 <script type="module" src="main.js"> 로.
한 번에 다 하지 말고, 먼저 data.js 와 main.js 만 분리하는 방법을 보여 줘.
```

```
#file:docs/data-contract.md #file:data/fixtures/stations.json #file:data/fixtures/lines.json #file:data/fixtures/last_trains.json #file:web/data.js
지금 data.js 에 하드코딩된 ST, LINES 를 지우고 fetch 로 JSON 을 읽어서
기존 코드가 쓰던 모양(P 좌표, last[역][노선], stationLast, lineOf)을 만들어 주는 함수로 바꿔 줘.
폴더 경로는 맨 위 const DATA_DIR = "../data/fixtures/" 한 줄로.
```

```
에러가 났어. 브라우저 개발자도구(F12) Console 에 뜬 내용이야. 원인과 고칠 곳을 알려 줘.
(빨간 줄 전체 붙여 넣기)
```

## 확인 방법
- `python3 -m http.server 8000` → `http://localhost:8000/web/`
- **F12 → Console 에 빨간 줄이 없어야** 커밋
- 슬라이더를 01:15 로 → 노선이 꺼지고 버스가 나오는지
- F12 → 휴대폰 모양 아이콘 → 375px 에서 겹치는 곳 없는지

## 자주 막히는 곳
- **화면이 하얗고 Console 에 CORS 에러**: 파일을 더블클릭해서 열었음 → 로컬 서버로 열기
- **`fetch` 404**: 경로 문제. `web/` 기준으로 `../data/fixtures/` 가 맞는지
- **한 번에 많이 바꿨다가 안 돌아감**: 마지막으로 되던 커밋으로 돌아가서 작게 다시 (그래서 PR을 작게 나눔)

## 발표 때 설명할 것
- 지도 좌표를 화면 좌표로 바꾼 방법 (위도·경도 → 캔버스 x, y)
- 시간이 흐를 때 노선이 꺼지는 원리 (현재 시각 vs 그 구간 막차)
- 데이터 파일을 화면과 분리한 이유
