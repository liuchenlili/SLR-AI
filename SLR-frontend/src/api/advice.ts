// src/api/advice.ts
export interface AdviceReq {
  label: string
  confidence: number
  recent?: string[][]
  question?: string
  user_id?: string
}

export interface AdviceResp {
  advice: string
}

const BASE_URL = "http://localhost:8001"              // 同源部署留空；否则写 "http://127.0.0.1:8001"
const ADVICE_URL = BASE_URL + "/advice"

/**
 * 支持 AbortSignal：传入 signal 可在外部中断请求
 */
export async function getAdvice(req: AdviceReq, signal?: AbortSignal): Promise<AdviceResp> {
  const resp = await fetch(ADVICE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  })
  if (!resp.ok) {
    const txt = await resp.text().catch(() => "")
    throw Object.assign(new Error(`Advice API ${resp.status}: ${txt}`), { status: resp.status, body: txt })
  }
  return resp.json()
}
