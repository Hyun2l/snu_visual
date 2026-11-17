# 1번 리드: 막차 규칙·검증·머지

브랜치 `hyun` · 이슈 #1 · 먼저 읽기: [00-start](00-start.md), [데이터 계약](../data-contract.md)

## 한 줄로
팀원이 만든 데이터가 **맞는지** 확인하고, 화면에 보여 줄 **"이 역 막차"를 정하고**, PR을 합친다.

## 왜 중요한가
막차 API는 행선지마다 시각이 다르다 (강남 내선: 신도림행 24:00, 서울대입구행 24:46).
"강남 막차 몇 시?"에 답이 하나가 아니라서 **규칙을 정해야** 화면이 거짓말을 안 한다. 평가의 "시각화 정확성"이 여기서 갈린다.

## 할 일
1. **PR 리뷰·머지** (매일)
   - PR → **Files changed** 에서 바뀐 파일 확인. 남의 폴더를 건드렸거나 `.env`, 큰 파일이 있으면 반려
   - 담당자에게 "이 부분 설명해 줘" 한 번씩 물어보기 (구현 이해 확인)
   - 합친 뒤 `docs/team.md` 표에 담당자 이름 채우기
2. **대표 막차 규칙** 정하기 → `pipeline/build_last.py`
   - 입력 `data/out/last_trains.json` (행선지별) → 출력 `data/out/last_by_station.json` (역·노선·방향별 1개)
   - 추천 규칙: 방향별로 **가장 늦게 출발하는 열차**를 대표로, 대신 그 열차의 행선지를 같이 표시 ("24:46 서울대입구행")
3. **검증 스크립트** → `pipeline/validate_out.py`
   - `data/out/*.json` 이 계약 모양인지, 역 이름이 파일끼리 다 맞는지, 시각이 1300~1560 분 안인지
4. **실제 대조**: 역 20곳을 카카오맵·네이버지도 막차 조회와 비교해 ±1분 안인지 `docs/check-last-train.md` 에 표로 남기기

## AI에게 줄 말

```
나는 서울 지하철 막차 지도 팀 프로젝트의 리드야.
#file:docs/data-contract.md #file:data/fixtures/last_trains.json #file:pipeline/seoul_api.py
last_trains.json 은 역·노선·방향(dir)·행선지(dest)별 막차 시각(t, 자정 넘으면 1440 이상인 분)이야.
pipeline/build_last.py 를 만들어 줘:
- 역·노선·dir 마다 t 가 가장 큰 행 하나를 골라 data/out/last_by_station.json 로 저장
- 입력 파일 경로는 인자로 받아서 fixtures 로도 돌려 볼 수 있게
- 표준 라이브러리만
코드 아래에 초보자도 알게 설명해 줘.
```

```
#file:docs/data-contract.md
pipeline/validate_out.py 를 만들어 줘. data/out (또는 인자로 준 폴더)의 json 파일들을 읽어서
1) 계약에 적힌 필드가 다 있는지 2) stations.json 에 없는 역 이름이 다른 파일에 나오는지
3) last_trains 의 t 가 1300~1560 사이인지 검사하고, 문제를 줄별로 출력해 줘. 문제가 있으면 종료코드 1.
```

## 확인 방법
```bash
python3 pipeline/build_last.py data/fixtures
python3 pipeline/validate_out.py data/fixtures
```
fixtures 로 먼저 통과시키고, 실데이터가 들어오면 `data/out` 으로 돌린다.

## 자주 막히는 곳
- **PR 충돌**: 두 사람이 같은 파일을 고치면 생긴다. 역할별 폴더를 지키게 하는 게 최선
- **팀원이 막혀서 조용함**: 매일 "어디까지 했어? 막힌 거 있어?" 한 번씩

## 발표 때 설명할 것
- 막차가 행선지마다 다르다는 발견과, 대표 막차를 고른 규칙과 그 이유
- 20곳 대조 결과 (정확성 근거)
