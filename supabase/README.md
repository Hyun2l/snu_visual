# 채팅 설정 (Supabase)

ABS 14기 약 30명이 쓰는 익명 한마디. 무료 요금제로 충분하다.

## 방식

- **익명 로그인 + 입장 코드.** 이메일을 모으지 않는다. 저장소가 공개라 명단을 올릴 수 없기 때문.
- 입장 코드는 DB(`settings` 표)에만 있다. 코드를 넣은 사람만 `members` 에 들어가고, 멤버만 한마디를 읽고 쓴다.
- 화면에는 uid로 만든 닉네임("졸린 올빼미 #42")만 보인다. 누가 썼는지는 관리자도 uid까지만 안다.
- 서버가 막는 것: 60자 초과, 같은 사람 3초 안 재전송, 멤버 아닌 사람의 읽기·쓰기, 관리자 아닌 사람의 삭제.

## 처음 한 번 (채팅 담당)

1. [supabase.com](https://supabase.com) 에서 새 프로젝트 만들기 (지역: Northeast Asia (Seoul)).
2. **Authentication → Sign In / Providers → Anonymous sign-ins 켜기.**
3. **SQL Editor** 에 [`schema.sql`](schema.sql) 전체를 붙여 넣고 Run.
4. 같은 곳에서 입장 코드 정하기 (코드는 단톡방으로만 공유, 저장소에 적지 말 것):
   ```sql
   insert into public.settings (key, value) values ('join_code', '정한-코드')
     on conflict (key) do update set value = excluded.value;
   ```
5. **Project Settings → API** 에서 URL과 `anon` 키를 복사해 `web/config.js` 에 넣기 (`config.example.js` 복사).
   anon 키는 공개돼도 되는 키다. `service_role` 키는 절대 넣지 않는다.
6. `web/chat-test.html` 을 열어서 확인:
   ```bash
   python3 -m http.server 8000
   # 브라우저에서 http://localhost:8000/web/chat-test.html
   ```
   입장 코드 → 한마디. **다른 사람(또는 시크릿 창)과 둘이서** 서로 보이는지 확인.
7. 화면에 나온 본인 uid로 관리자 지정:
   ```sql
   update public.members set is_admin = true where uid = '본인-uid';
   ```

## 지도 화면에 붙이기 (지도 담당과 같이)

```js
import { connectChat, pacing } from "./chat.js";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "./config.js";

const chat = await connectChat({
  url: SUPABASE_URL, anonKey: SUPABASE_ANON_KEY,
  onMessage: (m, { replay }) => enqueue(m),  // 프로토타입의 enqueue 그대로
  onStatus: s => setStatusText(s),
});
// 말풍선 대기열을 꺼낼 때마다: const { show, maxOn } = pacing(queue.length);
// 대기열에서 STALE_MS(1분) 넘은 건 버린다.
```

## 꼭 알아 둘 것

- **무료 프로젝트는 일주일 동안 안 쓰면 멈춘다.** 발표 전날 대시보드에서 살아 있는지 확인하고, 멈췄으면 Restore.
- 입장 코드가 새면 4번 SQL로 바꾸면 된다. 이미 들어온 사람은 그대로 남는다. 다 내보내려면 `delete from public.members where not is_admin;`.
- 익명 로그인은 브라우저마다 따로라서, 다른 기기에서 열면 입장 코드를 다시 넣어야 한다.
- 이 SQL은 실제 Supabase 에서 아직 돌려 보지 않았다. 3번에서 에러가 나면 메시지 그대로 리드에게 공유.
