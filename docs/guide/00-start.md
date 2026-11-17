# 처음 시작하기 (개발 처음인 사람용)

이 문서만 따라 하면 내 컴퓨터에서 프로젝트를 열고, 내 브랜치에서 고치고, 팀에 올릴 수 있다.
막히면 혼자 오래 붙잡지 말고 **30분 안에** 단톡방에 화면 캡처와 함께 물어보기.

---

## 1. 용어 다섯 개만 알면 된다

| 용어 | 한 줄 설명 | 비유 |
|---|---|---|
| **저장소(repo)** | 프로젝트 파일 전체가 들어 있는 GitHub 폴더 | 팀 공유 드라이브 |
| **브랜치(branch)** | 저장소의 내 작업용 복사본. 우리 팀은 이름별로 하나씩 있다 | 원본을 복사한 내 연습장 |
| **커밋(commit)** | "여기까지 했다"고 저장하는 것. 메시지를 같이 남긴다 | 게임 세이브 |
| **푸시(push)** | 내 컴퓨터의 커밋을 GitHub에 올리는 것 | 드라이브에 업로드 |
| **PR(Pull Request)** | "내 브랜치 내용을 main에 합쳐 주세요" 요청. 리드가 보고 합친다 | 결재 올리기 |

`main` = 모두가 보는 완성본. **절대 직접 고치지 않는다.** 항상 내 이름 브랜치에서 작업하고 PR로 올린다.

우리 팀 이름 브랜치: `hyun`(리드), `LEE`, `Min`, `Walnut`, `jun`, `kdkook`

---

## 2. 설치 (한 번만)

1. **VS Code**: https://code.visualstudio.com
2. **Git**
   - Mac: 터미널에서 `git --version` 입력 → 설치하라는 창이 뜨면 설치
   - Windows: https://git-scm.com 에서 받아 기본값으로 설치
3. **Python 3**: https://www.python.org/downloads (Windows는 설치 첫 화면에서 **"Add python.exe to PATH" 체크** 필수)
4. VS Code 왼쪽 확장(□ 모양 아이콘)에서 설치
   - `Python` (Microsoft)
   - `GitHub Copilot`, `GitHub Copilot Chat` (학생이면 GitHub Education으로 무료)
5. VS Code 왼쪽 아래 사람 모양 아이콘 → **GitHub로 로그인**

설치 확인: VS Code에서 `` Ctrl+` ``(Mac은 `` Cmd+` ``)로 터미널을 열고

```bash
git --version
python3 --version
```

Windows에서 `python3` 가 안 되면 `python` 으로 쳐 본다. 이후 문서의 `python3` 도 똑같이 바꿔서 쓰면 된다.

---

## 3. 프로젝트 받기 (한 번만)

1. VS Code 첫 화면 → **Clone Git Repository** (또는 `Ctrl+Shift+P` → `Git: Clone`)
2. 주소 붙여 넣기: `https://github.com/Hyun2l/snu_visual.git`
3. 저장할 폴더 고르기 (예: 바탕화면) → **Open**

---

## 4. 내 브랜치로 바꾸기 (매번 확인)

VS Code **왼쪽 아래**에 지금 브랜치 이름이 보인다 (처음엔 `main`).

1. 그걸 클릭 → 목록에서 `origin/내이름` 선택 (예: `origin/Min`)
2. 왼쪽 아래가 `Min` 으로 바뀌면 성공

**작업 시작 전에 항상 왼쪽 아래가 내 이름인지 본다.** `main` 이면 다시 바꾼다.

---

## 5. 매일 작업 순서

```
① 최신 받기  →  ② 고치기  →  ③ 확인  →  ④ 커밋  →  ⑤ 푸시  →  ⑥ (끝나면) PR
```

① **최신 받기**: 터미널에서
```bash
git pull origin main
```
다른 사람이 main에 합친 내용을 내 브랜치로 가져온다. 하루 시작할 때 한 번.

② **고치기**: 내 역할 가이드에 적힌 파일만 고친다.

③ **확인**: 가이드의 "확인 방법"대로 실행해 본다. 에러가 나면 커밋하지 않는다.

④ **커밋**: 왼쪽 세 번째 아이콘(Source Control, 갈래 모양)
- 바뀐 파일 목록이 보인다. 이상한 파일(`.env`, 큰 데이터 파일)이 있으면 **멈추고 물어보기**
- 위 칸에 메시지 쓰기 (예: `역 좌표 수집 코드 추가`) → **Commit**
- "스테이징된 변경 없음" 창이 뜨면 **Yes**(전부 커밋)

⑤ **푸시**: Commit 버튼이 **Sync Changes**로 바뀌면 누른다. 이제 GitHub에 올라갔다.

⑥ **PR**: 기능 하나가 끝나면
- https://github.com/Hyun2l/snu_visual 접속 → 노란 띠의 **Compare & pull request**
  (안 보이면 **Pull requests → New pull request**, base: `main` ← compare: `내이름`)
- 제목: 한 일 한 줄. 본문: 무엇을 했는지, 어떻게 확인했는지, 이슈 번호 (`#3` 처럼)
- **Create pull request** → 리드가 보고 합친다

---

## 6. 절대 하지 말 것

- `main` 에서 직접 커밋하기
- `.env` 파일이나 API 키를 커밋하기 (키가 GitHub에 올라가면 바로 리드에게 말하기. 키를 새로 발급해야 함)
- 남의 역할 폴더 고치기 (필요하면 PR 설명에 쓰고 담당자에게 말하기)
- 이해 못한 AI 코드를 그대로 커밋하기 (아래 7번)

---

## 7. AI(Copilot) 쓰는 법

평가에 **"구현 이해·발표"** 가 있다. 교수님이 "이 코드 왜 이렇게 했어요?" 물으면 내가 답해야 한다.
그래서 AI에게는 **코드만 받지 말고 설명도 같이 받는다.**

### Copilot Chat 열기
VS Code 오른쪽 위 Copilot 아이콘 또는 `Ctrl+Alt+I` (Mac `Cmd+Ctrl+I`).
채팅창에서 `#` 을 치면 파일을 첨부할 수 있다 (예: `#file:docs/data-contract.md`). **관련 파일은 꼭 첨부한다.** 안 붙이면 AI가 우리 프로젝트를 모르고 지어낸다.

### 좋은 질문의 모양
```
[상황] 나는 개발 처음이고, 서울 지하철 막차 지도 팀 프로젝트에서 ○○ 담당이야.
[첨부] #file:docs/data-contract.md #file:pipeline/seoul_api.py
[할 일] ○○를 만드는 코드를 짜 줘.
[조건] 표준 라이브러리만 / 기존 함수 call() 재사용 / 결과는 data/out/○○.json
[설명] 코드 아래에 줄마다 무슨 일을 하는지 초보자 말로 설명해 줘.
```

### 매번 쓰면 좋은 마무리 질문 (복사해서 쓰기)
```
방금 코드에서 내가 발표 때 설명해야 할 핵심 3가지만 쉬운 말로 정리해 줘.
```
```
이 코드가 틀릴 수 있는 경우(빈 데이터, 이름 불일치, 자정 넘는 시각 등)를 찾아 줘.
```
```
에러가 났어. 아래가 에러 메시지 전체야. 원인을 초보자 말로 설명하고, 고칠 곳을 알려 줘.
(에러 전문 붙여 넣기)
```

### AI에게 절대 주지 말 것
- API 키, `.env` 내용, 입장 코드, 비밀번호
- 팀원 개인정보

---

## 8. 내 역할 가이드

| # | 역할 | 가이드 |
|---|---|---|
| 1 | 리드: 막차 규칙·검증·머지 | [01-lead.md](01-lead.md) |
| 2 | 시간표·막차 수집 | [02-timetable.md](02-timetable.md) |
| 3 | 역 마스터·승하차 | [03-stations.md](03-stations.md) |
| 4 | 심야버스 | [04-nbus.md](04-nbus.md) |
| 5 | 지도 화면 | [05-map.md](05-map.md) |
| 6 | 채팅·배포 | [06-chat.md](06-chat.md) |

먼저 같이 읽을 것: [팀 분담](../team.md), [데이터 계약](../data-contract.md)

---

## 9. 첫날 체크리스트

- [ ] 2번 설치 끝, `git --version`, `python3 --version` 나옴
- [ ] 3번 클론 끝, VS Code에 폴더가 열림
- [ ] 4번 왼쪽 아래가 내 이름 브랜치
- [ ] 터미널에서 `python3 pipeline/check_sources.py` → `OK` 6줄
- [ ] 서울 열린데이터광장(data.seoul.go.kr) 가입 → **인증키 신청** (데이터 담당 2·3·4번은 필수)
- [ ] `.env.example` 을 복사해서 `.env` 만들고 키 넣기 (`.env` 는 커밋 안 되게 이미 막혀 있음)
- [ ] GitHub 이슈에서 내 역할 이슈를 열고 오른쪽 **Assignees** 에 나를 지정
- [ ] 연습 커밋: `docs/members/내이름.md` 파일을 새로 만들고 `맡은 역할: ○번 ○○` 한 줄 쓰기 → 커밋 → 푸시 → PR
  (각자 다른 파일이라 서로 충돌이 안 난다. 리드가 합치면서 `docs/team.md` 표에 이름을 채운다)
