"""데이터 소스가 우리가 기대한 모양인지 확인한다.

    python3 pipeline/check_sources.py            # sample 키로 5건씩 확인
    SEOUL_API_KEY=... python3 pipeline/check_sources.py

결과는 docs/data-check-latest.md 에도 남긴다.
"""
import datetime as dt
import sys

from seoul_api import KEY, ApiError, ROOT, call, to_min

checks = []


def check(name, fn):
    try:
        ok, note = fn()
    except (ApiError, OSError, KeyError, ValueError) as e:
        ok, note = False, f"호출 실패: {e}"
    checks.append((name, ok, note))
    print(("OK  " if ok else "FAIL"), name, "-", note)


def station_master():
    d = call("subwayStationMaster", 1, 5)
    r = d["row"][0]
    need = {"BLDN_ID", "BLDN_NM", "ROUTE", "LAT", "LOT"}
    return need <= r.keys(), f"{d['list_total_count']}행, 예: {r['BLDN_NM']} {r['ROUTE']} ({r['LAT']}, {r['LOT']}) id={r['BLDN_ID']}"


def station_codes():
    d = call("SearchInfoBySubwayNameService", 1, 5)
    r = d["row"][0]
    return {"STATION_CD", "STATION_NM", "LINE_NUM", "FR_CODE"} <= r.keys(), f"{d['list_total_count']}행, 예: {r['STATION_NM']} {r['LINE_NUM']} cd={r['STATION_CD']}"


def timetable_train_no():
    d = call("SearchSTNTimeTableByIDService", 1, 5, "0222", "1", "1")  # 강남, 평일, 상행/내선
    r = d["row"][0]
    return bool(r.get("TRAIN_NO")), f"강남 평일 {d['list_total_count']}편, 열차번호 {r.get('TRAIN_NO')!r}, 출발 {r['LEFTTIME']} → {r['SUBWAYENAME']}"


def last_train():
    d = call("SearchLastTrainTimeByIDService", 1, 5, "0222", "1", "1")
    rows = d["row"]
    best = max(rows, key=lambda r: to_min(r["LEFTTIME"]))
    dests = ", ".join(f"{r['SUBWAYENAME']} {r['LEFTTIME']}" for r in rows)
    return to_min(best["LEFTTIME"]) > 1440, f"방면(행선지)마다 막차가 다름: {dests}"


def ridership_night():
    month = (dt.date.today().replace(day=1) - dt.timedelta(days=40)).strftime("%Y%m")
    d = call("CardSubwayTime", 1, 5, month)
    r = d["row"][0]
    have = all(f"HR_{h}_GET_ON_NOPE" in r for h in (23, 0, 1))
    return have, f"{month} {d['list_total_count']}행, {r['SBWY_ROUT_LN_NM']} {r['STTN']}: 23시 {r['HR_23_GET_ON_NOPE']:.0f} / 0시 {r['HR_0_GET_ON_NOPE']:.0f} / 1시 {r['HR_1_GET_ON_NOPE']:.0f} (월 합계)"


def bus_stops():
    d = call("busStopLocationXyInfo", 1, 5)
    r = d["row"][0]
    return {"STOPS_NO", "STOPS_NM", "XCRD", "YCRD"} <= r.keys(), f"{d['list_total_count']}개 정류장 좌표 있음. 노선(N버스)과의 연결은 이 API에 없음"


check("역 좌표 (subwayStationMaster)", station_master)
check("역 코드 (SearchInfoBySubwayNameService)", station_codes)
check("시간표에 열차번호 있음", timetable_train_no)
check("막차 시각, 자정 넘김 표기", last_train)
check("승하차 23·0·1시 칸", ridership_night)
check("버스 정류장 좌표", bus_stops)

out = ROOT / "docs" / "data-check-latest.md"
out.parent.mkdir(exist_ok=True)
lines = [f"# 데이터 확인 결과 ({dt.datetime.now():%Y-%m-%d %H:%M}, 키: {'sample' if KEY == 'sample' else '개인 키'})", ""]
lines += [f"- {'✅' if ok else '❌'} **{n}** — {note}" for n, ok, note in checks]
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n저장:", out.relative_to(ROOT))
sys.exit(0 if all(ok for _, ok, _ in checks) else 1)
