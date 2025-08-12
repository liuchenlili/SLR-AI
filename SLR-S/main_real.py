import os
import cv2
import time
import json
import uuid
import torch
import asyncio
import numpy as np
from PIL import Image
from typing import List

from fastapi import FastAPI, WebSocket, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ===== 你项目里的模块 =====
from SignFormer import SignFormer
from models import r2plus1d_18, r3d_18, ResCRNN
from real import get_transform, get_transform_signfor
from predication import predict
from tool import image_to_video

# ---------- 基础设置 ----------
app = FastAPI(title="SLR Realtime Backend", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 生产环境建议收敛域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/videos", exist_ok=True)
os.makedirs("data/images", exist_ok=True)
os.makedirs("data/ptov", exist_ok=True)
app.mount("/videos", StaticFiles(directory="data/videos"), name="videos")
app.mount("/ptov", StaticFiles(directory="data/ptov"), name="ptov")


# ---------- 工具函数 ----------
def image_to_base64(image_np: np.ndarray) -> str:
    """BGR ndarray -> base64 data URL"""
    from io import BytesIO
    import base64
    pil_img = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    pil_img.save(buf, format='JPEG')
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

def get_labels() -> List[str]:
    labels = []
    with open("data/dictionary.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > 1:
                labels.append(parts[1])
    return labels

def load_model(selected_model: str, selected_weight: str) -> torch.nn.Module:
    """
    selected_model: r2+1d_100 / r3d_100 / LSTM_100 / r2+1d_500 / r3d_500 / LSTM_500 / SignFormer_100 / SignFormer_500
    selected_weight: 对应的权重文件名（位于 weight/{selected_model}/ 目录）
    """
    n_cls = int(selected_model.split("_")[-1])
    model_path = f"weight/{selected_model}/{selected_weight}"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if selected_model in ("r2+1d_100", "r2+1d_500"):
        model = r2plus1d_18(num_classes=n_cls).to(device)
    elif selected_model in ("r3d_100", "r3d_500"):
        model = r3d_18(num_classes=n_cls).to(device)
    elif selected_model in ("LSTM_100", "LSTM_500"):
        model = ResCRNN(
            sample_size=128, sample_duration=16, num_classes=n_cls,
            lstm_hidden_size=512, lstm_num_layers=1, arch="resnet18",
            attention=False
        ).to(device)
    elif selected_model in ("SignFormer_100", "SignFormer_500"):
        model = SignFormer(num_classes=n_cls).to(device)
    else:
        raise RuntimeError(f"Unknown model: {selected_model}")

    state = torch.load(model_path, map_location=device)
    if selected_model.startswith("SignFormer"):
        state = state["model_state_dict"]
    model.load_state_dict(state)
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
    return model


# ---------- 本地 OpenCV 测试（离线） ----------
def run_local_test(selected_model: str, selected_weight: str, thres: float = 0.75):
    """
    本地摄像头 + 模型推理验证（弹窗显示，按 Q 退出）
    """
    labels = get_labels()
    model = load_model(selected_model, selected_weight)

    use_signformer = selected_model.startswith("SignFormer")
    transform = get_transform_signfor() if use_signformer else get_transform()
    H, W = (224, 224) if use_signformer else (128, 128)

    cache_input = torch.ones(1, 3, 16, H, W)
    if torch.cuda.is_available():
        cache_input = cache_input.cuda()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    i_frame = -1
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            i_frame += 1

            if i_frame % 2 == 0:  # 隔帧推理降负载
                t1 = time.time()
                img_tran = transform([Image.fromarray(frame).convert('RGB')])

                cache_input = cache_input[:, :, 1:, :, :]
                input_var = img_tran.view(1, 3, 1, img_tran.size(1), img_tran.size(2))
                if torch.cuda.is_available():
                    input_var = input_var.cuda()
                cache_input = torch.cat((cache_input, input_var), dim=2)

                with torch.no_grad():
                    feat = model(cache_input)  # [1, C]

                feat = feat.detach().cpu().numpy().reshape(-1)
                feat -= feat.max()
                prob = np.exp(feat) / np.sum(np.exp(feat))
                idx = int(np.argmax(prob))
                conf = float(prob[idx])

                if conf > thres:
                    text = f"{labels[idx]} ({conf*100:.1f}%)"
                else:
                    text = f"NULL ({conf*100:.1f}%)"

                t2 = time.time()
                fps = 1.0 / max(t2 - t1, 1e-6)
                cv2.putText(frame, text, (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
                cv2.putText(frame, f"FPS: {fps:.1f}", (16, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,180,0), 2)

            cv2.imshow("Local Realtime Test (Press Q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


# ---------- WebSocket：推流到前端 ----------
@app.websocket("/ws/recognize")
async def ws_recognize(websocket: WebSocket):
    """
    前端连接后先发送配置 JSON:
    {
      "model": "SignFormer_100",  // 或 r2+1d_100 / r3d_100 / LSTM_100 / ...
      "weight": "best.pth",
      "thres": 0.75
    }
    后端从本地摄像头采集 -> 预处理 -> 模型推理 -> 返回 {label, confidence, image(base64)}
    """
    await websocket.accept()

    cfg = await websocket.receive_json()
    selected_model = cfg.get("model", "SignFormer_100")
    selected_weight = cfg.get("weight", "best.pth")
    thres = float(cfg.get("thres", 0.75))

    labels = get_labels()
    model = load_model(selected_model, selected_weight)

    use_signformer = selected_model.startswith("SignFormer")
    transform = get_transform_signfor() if use_signformer else get_transform()
    H, W = (224, 224) if use_signformer else (128, 128)

    cache_input = torch.ones(1, 3, 16, H, W)
    if torch.cuda.is_available():
        cache_input = cache_input.cuda()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    i_frame = -1
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            i_frame += 1

            if i_frame % 2 == 0:
                img_tran = transform([Image.fromarray(frame).convert('RGB')])

                cache_input = cache_input[:, :, 1:, :, :]
                input_var = img_tran.view(1, 3, 1, img_tran.size(1), img_tran.size(2))
                if torch.cuda.is_available():
                    input_var = input_var.cuda()
                cache_input = torch.cat((cache_input, input_var), dim=2)

                with torch.no_grad():
                    feat = model(cache_input)

                feat = feat.detach().cpu().numpy().reshape(-1)
                feat -= feat.max()
                prob = np.exp(feat) / np.sum(np.exp(feat))
                conf = float(prob.max())
                label = "NULL"
                if conf > thres:
                    label = labels[int(np.argmax(prob))]

                await websocket.send_json({
                    "label": label,
                    "confidence": conf,
                    "image": image_to_base64(frame)
                })

            await asyncio.sleep(0.01)  # 控制发送频率，避免前端卡顿
    except Exception as e:
        print("ws error:", e)
    finally:
        cap.release()
        await websocket.close()


# ---------- 可选：HTTP 上传视频/帧批量预测 ----------
@app.post("/predict/video")
async def predict_video(
    model: str = Form(...),
    weight: str = Form(...),
    video_style: str = Form(...),
    centercrop: bool = Form(False),
    file: UploadFile = File(...)
):
    ext = os.path.splitext(file.filename)[-1].lower()
    name = uuid.uuid4().hex + ext
    save_path = os.path.join("data/videos", name)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    ida, prediction = predict(name, model, weight, False, video_style, centercrop)
    # 归一化输出
    out = []
    for p in prediction:
        label = str(p[0])
        conf = p[1]
        if isinstance(conf, str) and conf.endswith("%"):
            conf = float(conf[:-1])
        out.append([label, f"{float(conf):.3f}%"])
    return {"filename": name, "index": int(ida) if hasattr(ida, "__int__") else ida, "results": out}


@app.post("/predict/images")
async def predict_images(
    model: str = Form(...),
    weight: str = Form(...),
    video_style: str = Form(...),
    centercrop: bool = Form(False),
):
    video_filename = f"{uuid.uuid4().hex}.mp4"
    video_path = os.path.join("data/videos", video_filename)
    image_to_video(sample_dir="data/images", video_name=video_path)
    ida, prediction = predict(video_filename, model, weight, False, video_style, centercrop)
    return {"filename": video_filename, "index": ida, "results": prediction}

from advice_coze import router as advice_router
app.include_router(advice_router)
# ---------- 启动入口 ----------
if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["test", "serve"], default="serve",
                        help="test: 本地OpenCV测试; serve: 启动API/WS服务")
    parser.add_argument("--model", default="SignFormer_100")
    parser.add_argument("--weight", default="best_checkpoint.pth")
    parser.add_argument("--thres", type=float, default=0.75)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    if args.mode == "test":
        run_local_test(args.model, args.weight, args.thres)
    else:
        uvicorn.run("main_real:app", host=args.host, port=args.port, reload=True)
