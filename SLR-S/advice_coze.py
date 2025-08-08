# advice_coze.py —— 扣子建议路由：对标 Java：{bot_id, user, query}
import os
import json
import requests
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/advice", tags=["advice"])

# ========= 配置 =========
# 本地调试可直接写死；上线建议用环境变量
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN") or ""
COZE_BOT_ID    = os.getenv("COZE_BOT_ID") or ""
COZE_CHAT_URL  = "https://api.coze.cn/open_api/v2/chat"

# 强制禁用系统代理，避免 TLS/证书被劫持导致 EOF/4000
for k in ("HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","http_proxy","https_proxy","all_proxy","NO_PROXY","no_proxy"):
    os.environ.pop(k, None)

router = APIRouter(prefix="/advice", tags=["advice"])  # ★ 明确前缀

# ========= 入参模型 =========
class AdviceReq(BaseModel):
    label: str
    confidence: float
    recent: Optional[List[List[str]]] = None   # 例如 [["你好","93.1%"], ...]，可选
    question: Optional[str] = ""               # 用户附加问题，可选
    user_id: Optional[str] = "spring_client"   # 与 Java 一致

# ========= 仅拼识别上下文为 query（系统提示放在智能体里）=========
def build_query(req: AdviceReq) -> str:
    conf_pct = f"{req.confidence * 100:.1f}%"
    parts = [
        f"当前识别词：{req.label}（置信度：{conf_pct}）",
        f"TopK：{req.recent or []}",
        "若可信（>60%）请给示范要点；若不可信请给可能的混淆词与对比要点。"
    ]
    q = (req.question or "").strip()
    if q:
        parts.append(f"用户问题：{q}")
    return "\n".join(parts)

# ========= 解析：只取 assistant + answer =========
def pick_answer_text(resp_json: dict) -> str:
    msgs = resp_json.get("messages") or []
    for m in msgs:
        if m.get("role") == "assistant" and m.get("type") == "answer":
            c = m.get("content")
            if isinstance(c, str) and c.strip():
                return c.strip()
    for m in msgs:
        if m.get("role") == "assistant":
            c = m.get("content")
            if isinstance(c, str) and c.strip():
                return c.strip()
    for m in msgs:
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            return c.strip()
    return ""

# ========= 主路由 =========
@router.post("")
def gen_advice(req: AdviceReq):
    if not (COZE_API_TOKEN and COZE_BOT_ID):
        raise HTTPException(500, "COZE_API_TOKEN / COZE_BOT_ID 未配置或为空")

    payload = {
        "bot_id": COZE_BOT_ID,
        "user":   req.user_id or "spring_client",
        "query":  build_query(req),
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type":  "application/json; charset=utf-8",
        "Accept":        "application/json",
        "Content-Length": str(len(body)),
    }

    try:
        resp = requests.post(COZE_CHAT_URL, headers=headers, data=body, timeout=30)
        raw  = resp.text
        print("[coze v2/chat] http:", resp.status_code)
        print("[coze v2/chat] body:", raw[:1000])
    except Exception as e:
        raise HTTPException(502, f"请求 coze 失败：{e}")

    try:
        data = resp.json()
    except Exception:
        data = {}

    if not resp.ok or data.get("code") != 0:
        raise HTTPException(
            502,
            f"coze异常: http={resp.status_code}, code={data.get('code')}, msg={data.get('msg')}, body={raw[:800]}"
        )

    answer = pick_answer_text(data)
    return {"advice": answer or "(无建议返回)"}