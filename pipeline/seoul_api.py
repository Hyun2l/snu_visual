"""서울 열린데이터광장 OpenAPI 호출 공통 코드 (표준 라이브러리만 씀).

키는 .env 의 SEOUL_API_KEY. 없으면 'sample' 키로 돌고, sample 은 한 번에 5건까지만 준다.
"""
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://openapi.seoul.go.kr:8088"


def _load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


_load_env()
KEY = os.environ.get("SEOUL_API_KEY") or "sample"
PAGE = 5 if KEY == "sample" else 1000


class ApiError(Exception):
    pass


def call(service, start, end, *params):
    """한 페이지 호출. params 는 URL 뒤에 붙는 요청인자(순서 중요)."""
    parts = [BASE, urllib.parse.quote(KEY), "json", service, str(start), str(end)]
    parts += [urllib.parse.quote(str(p)) for p in params]
    url = "/".join(parts) + "/"
    with urllib.request.urlopen(url, timeout=20) as r:
        body = r.read().decode("utf-8")
    if body.lstrip().startswith("<"):
        raise ApiError(body[:200])
    data = json.loads(body)
    if service not in data:
        raise ApiError(data.get("RESULT", data))
    return data[service]


def fetch_all(service, *params, limit=None, pause=0.1):
    """전체 행을 페이지 단위로 모은다. sample 키면 처음 5건만."""
    first = call(service, 1, PAGE, *params)
    total = first["list_total_count"]
    rows = list(first.get("row", []))
    if KEY == "sample":
        return rows, total
    want = min(total, limit or total)
    start = PAGE + 1
    while len(rows) < want:
        page = call(service, start, start + PAGE - 1, *params)
        rows += page.get("row", [])
        start += PAGE
        time.sleep(pause)
    return rows[:want], total


def to_min(hms):
    """'24:46:30' → 1486.5 (운행일 00:00 기준 분, 자정 넘으면 1440 이상)."""
    h, m, s = (int(x) for x in hms.split(":"))
    if h < 4:  # 일부 응답이 '00:46:30' 식으로 오면 다음날로 본다
        h += 24
    return h * 60 + m + s / 60
