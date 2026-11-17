// 막차 대합실 채팅 — Supabase 실시간 연결.
// 화면(말풍선)은 map.js 쪽이 그린다. 이 파일은 "메시지가 들어오고 나가는 것"만 맡는다.
//
//   import { connectChat, pacing, clean } from "./chat.js";
//   const chat = await connectChat({ url, anonKey, onMessage, onStatus });
//   if (!chat.isMember) await chat.join("입장코드");
//   await chat.send({ text: "탔어요", kind: "preset", station: "강남", line: "2" });

import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/+esm";

export const MAX_LEN = 60;
export const REPLAY_MS = 30 * 60 * 1000; // 처음 열 때 다시 띄울 범위
export const REPLAY_MAX = 3;
export const STALE_MS = 60 * 1000;      // 대기열에서 1분 넘으면 버림

// 화면에 띄우기 전에 거르는 것 (서버도 60자는 막는다)
const BAN = ["시발", "씨발", "병신", "개새", "좆", "fuck"];
export function clean(s) {
  s = String(s || "").replace(/\s+/g, " ").trim().slice(0, MAX_LEN);
  s = s.replace(/01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}/g, "***-****-****");
  for (const w of BAN) s = s.split(w).join("♡".repeat(w.length));
  return s;
}

// 몰릴 때 말풍선 속도. 발표 때 30명이 한꺼번에 써도 대기열이 몇 분씩 밀리지 않게.
export function pacing(queued) {
  if (queued > 20) return { show: 2000, maxOn: 6 };
  if (queued > 8) return { show: 3500, maxOn: 5 };
  return { show: 7000, maxOn: 3 };
}

// uid → 익명 닉네임 (모두에게 같은 이름으로 보임)
const ADJ = ["뛰는", "졸린", "환승하는", "버티는", "느긋한", "급한", "야근한", "배고픈"];
const NOUN = ["막차러", "승객", "귀가러", "올빼미"];
export function nick(uid) {
  let h = 7;
  for (const c of String(uid || "x")) h = (h * 31 + c.charCodeAt(0)) % 9973;
  return `${ADJ[h % ADJ.length]} ${NOUN[(h >> 3) % NOUN.length]} #${h % 100}`;
}

// DB 행 → 화면에서 쓰는 모양
const toMsg = r => ({
  id: r.id, uid: r.uid, station: r.station, line: r.line,
  kind: r.kind, text: r.text, at: Date.parse(r.created_at),
});

// 에러 → 짧은 코드 (화면 문구는 쓰는 쪽에서)
function code(err) {
  const m = (err && (err.message || "")) + "";
  if (m.includes("rate_limited")) return "rate_limited";
  if (err && err.code === "23514") return "invalid";       // 길이·형식
  if (err && err.code === "42501") return "not_member";    // RLS 거절
  return "error";
}

/**
 * @param {object} o
 * @param {string} o.url        Supabase 프로젝트 URL
 * @param {string} o.anonKey    anon 키 (공개돼도 되는 키. service_role 키는 절대 넣지 말 것)
 * @param {(m: object, info: {replay: boolean}) => void} o.onMessage
 * @param {(s: string) => void} [o.onStatus]  "connecting" | "need_code" | "live" | "offline"
 */
export async function connectChat({ url, anonKey, onMessage, onStatus = () => {} }) {
  const sb = createClient(url, anonKey);
  const seen = new Set();
  let channel = null;

  onStatus("connecting");
  let { data: { session } } = await sb.auth.getSession();
  if (!session) {
    const { data, error } = await sb.auth.signInAnonymously();
    if (error) { onStatus("offline"); throw error; }
    session = data.session;
  }
  const uid = session.user.id;

  async function checkMember() {
    const { data } = await sb.from("members").select("uid").eq("uid", uid).maybeSingle();
    return !!data;
  }

  async function start() {
    // 최근 30분 중 마지막 3개만 다시 띄운다
    const since = new Date(Date.now() - REPLAY_MS).toISOString();
    const { data, error } = await sb.from("messages")
      .select("*").gte("created_at", since)
      .order("created_at", { ascending: false }).limit(REPLAY_MAX);
    if (!error) data.reverse().forEach(r => { seen.add(r.id); onMessage(toMsg(r), { replay: true }); });

    channel = sb.channel("messages")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "messages" }, p => {
        if (seen.has(p.new.id)) return;
        seen.add(p.new.id);
        onMessage(toMsg(p.new), { replay: false });
      })
      .subscribe(s => {
        if (s === "SUBSCRIBED") onStatus("live");
        else if (s === "CHANNEL_ERROR" || s === "TIMED_OUT" || s === "CLOSED") onStatus("offline");
      });
  }

  const api = {
    uid,
    isMember: await checkMember(),

    /** 입장 코드로 멤버 등록. 맞으면 true */
    async join(joinCode) {
      const { data, error } = await sb.rpc("join_room", { code: String(joinCode || "").trim() });
      if (error || !data) return false;
      api.isMember = true;
      await start();
      return true;
    },

    /** 한마디 보내기. 실패하면 { ok:false, reason } */
    async send({ text, kind = "text", station, line = null }) {
      text = clean(text);
      if (!text) return { ok: false, reason: "empty" };
      const { error } = await sb.from("messages").insert({ text, kind, station, line });
      return error ? { ok: false, reason: code(error) } : { ok: true };
    },

    async close() { if (channel) await sb.removeChannel(channel); },
  };

  if (api.isMember) await start();
  else onStatus("need_code");
  return api;
}
