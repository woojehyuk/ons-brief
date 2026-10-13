"""출동 전 브리핑 API. 실행: uvicorn main:app --port 8100"""
import json
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import build

app = FastAPI(title="ons-brief")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CFG = build.load_config(build.ROOT / "config.yaml")
APP_JSON = build.ROOT / CFG["paths"]["out_dir"] / "app.json"
SAMPLE = build.ROOT / "sample_data.json"
state = {"source": None, "error": None, "built_at": None}


def rebuild() -> None:
    """원본 데이터로 다시 계산. 실패(DRM·파일 없음 등) 시 가상 샘플 사용."""
    try:
        build.run(CFG)
        state.update(source="data", error=None)
    except Exception as e:  # noqa: BLE001 - 어떤 실패든 샘플로 대체
        state.update(source="sample", error=f"{type(e).__name__}: {e}"[:300])
    state["built_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_local(req: Request) -> bool:
    """터널(cloudflared) 경유 요청은 cf-connecting-ip 헤더가 붙음 → 외부로 간주."""
    return "cf-connecting-ip" not in req.headers and req.client is not None and req.client.host in ("127.0.0.1", "::1")


@app.get("/api/health")
def health(req: Request):
    if state["source"] is None:
        rebuild()
    return {"ok": True, "source": state["source"], "error": state["error"], "built_at": state["built_at"],
            "local": is_local(req)}


@app.get("/api/briefing")
def briefing(req: Request):
    if state["source"] is None:
        rebuild()
    path = APP_JSON if state["source"] == "data" else SAMPLE
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not is_local(req):
        payload["phones"] = {}  # 외부 접속에는 전체 번호 미전송
    payload["source"] = state["source"]
    return payload


@app.post("/api/build")
def rebuild_api(req: Request):
    rebuild()
    return health(req)
