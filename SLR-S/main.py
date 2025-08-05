import asyncio
import subprocess
from PIL import Image

from SignFormer import SignFormer
from models import r2plus1d_18, r3d_18, ResCRNN
import cv2
import torch
from fastapi import FastAPI, UploadFile, File, Form,WebSocket
from fastapi.middleware.cors import CORSMiddleware

from predication import predict
from real import get_transform, get_transform_signfor
from tool import image_to_video
import shutil, uuid, os
import numpy as np
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ...existing code...
app.mount("/videos", StaticFiles(directory="data/videos"), name="videos")
app.mount("/ptov", StaticFiles(directory="data/ptov"), name="ptov")
# ...existing code...
def load_model(selected_model: str, selected_weight: str):
    num_classes = int(selected_model[-3:])
    model_path = f"weight/{selected_model}/{selected_weight}"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if selected_model in ("r2+1d_100", "r2+1d_500"):
        model = r2plus1d_18(num_classes=num_classes).to(device)
    elif selected_model in ("r3d_100", "r3d_500"):
        model = r3d_18(num_classes=num_classes).to(device)
    elif selected_model in ("LSTM_100", "LSTM_500"):
        sample_size = 128
        sample_duration = 16
        lstm_hidden_size = 512
        lstm_num_layers = 1
        attention = False
        model = ResCRNN(
            sample_size=sample_size,
            sample_duration=sample_duration,
            num_classes=num_classes,
            lstm_hidden_size=lstm_hidden_size,
            lstm_num_layers=lstm_num_layers,
            arch="resnet18",
            attention=attention
        ).to(device)
    elif selected_model in ("SignFormer_100", "SignFormer_500"):
        model = SignFormer(num_classes=num_classes).to(device)
    else:
        raise RuntimeError(f"Unknown model: {selected_model}")

    state_dict = torch.load(model_path, map_location=device)
    if selected_model in ("SignFormer_100","SignFormer_500"):
        state_dict=state_dict['model_state_dict']
    model.load_state_dict(state_dict)
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
    return model
def get_labels():
    labels = []
    label_path = 'data/dictionary.txt'
    with open(label_path, 'r', encoding='utf-8') as label_file:
        for line in label_file:
            line = line.strip().split('\t')
            if len(line) > 1:
                labels.append(line[1])
    return labels



def image_to_base64(image_np):
    # 把opencv图片转为base64字符串，供前端显示
    from io import BytesIO
    import base64
    pil_img = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    buf = BytesIO()
    pil_img.save(buf, format='JPEG')
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
def safe(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x

def parse_confidence(val):
    """兼容 '93.914%' 字符串和 float/int 类型"""
    if isinstance(val, str):
        val = val.strip()
        if val.endswith('%'):
            val = val[:-1]
    return float(val)

# ===== WebSocket 实时识别接口 =====
# ------------- 实时识别WebSocket ---------------
@app.websocket("/ws/recognize")
async def ws_recognize(websocket: WebSocket):
    await websocket.accept()
    # 等待前端发送模型与权重名
    data = await websocket.receive_json()
    selected_model = data.get("model")
    selected_weight = data.get("weight")
    SOFTMAX_THRES = data.get("thres")
    print(SOFTMAX_THRES)
    model = load_model(selected_model, selected_weight)
    labels = get_labels()
    if selected_model in ("SignFormer_100", "SignFormer_500"):
        # SignFormer模型需要特殊的transform处理
        transform = get_transform_signfor()
        cache_input = torch.ones(1, 3, 16, 224, 224).cuda()
    else:
        transform = get_transform()
        cache_input = torch.ones(1, 3, 16, 128, 128).cuda()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    idx = 0
    _idx = 0
    i_frame = -1
    try:
        while cap.isOpened():
            success, image = cap.read()
            i_frame += 1
            if not success:
                break
            if i_frame % 2 == 0:
                img_tran = transform([Image.fromarray(image).convert('RGB')])
                cache_input = cache_input[:, :, 1:, :, :]
                input_var = torch.autograd.Variable(
                    img_tran.view(1, 3, 1, img_tran.size(1), img_tran.size(2))).cuda()
                cache_input = torch.cat((cache_input, input_var), dim=2)
                with torch.no_grad():
                    feat = model(cache_input)
                feat = feat.cpu()
                feat_np = feat.numpy().reshape(-1)
                feat_np -= feat_np.max()
                softmax = np.exp(feat_np) / np.sum(np.exp(feat_np))
                label = "NULL"
                confidence = 0.0
                if max(softmax) > SOFTMAX_THRES:
                    idx = np.argmax(feat.numpy(), axis=1)[0]
                    label = labels[idx]
                    confidence = float(max(softmax))
                await websocket.send_json({
                    "label": label,
                    "confidence": confidence,
                    "image": image_to_base64(image)
                })
                await asyncio.sleep(0.01)
    finally:
        cap.release()
        await websocket.close()

# @app.websocket("/ws/recognize")
# async def ws_recognize(websocket: WebSocket):
#     await websocket.accept()
#     # 第一次收到配置信息
#     config = await websocket.receive_json()
#     selected_model = config.get("model")
#     selected_weight = config.get("weight")
#     SOFTMAX_THRES = float(config.get("thres", 0.75))
#     model = load_model(selected_model, selected_weight)
#     labels = get_labels()
#     transform = get_transform()
#     cache_input = torch.ones(1, 3, 16, 128, 128).cuda()
#     idx = 0
#     _idx = 0
#     i_frame = -1
#     try:
#         while True:
#             # 前端发来一帧图片（base64字符串）
#             data = await websocket.receive_json()
#             if 'image' not in data:
#                 continue
#             # base64转np数组
#             import base64, io
#             img_data = data['image'].split(',')[1]
#             img_bytes = base64.b64decode(img_data)
#             pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
#             image = np.array(pil_img)
#
#             i_frame += 1
#             if i_frame % 2 == 0:
#                 img_tran = transform([Image.fromarray(image).convert('RGB')])
#                 cache_input = cache_input[:, :, 1:, :, :]
#                 input_var = torch.autograd.Variable(
#                     img_tran.view(1, 3, 1, img_tran.size(1), img_tran.size(2))).cuda()
#                 cache_input = torch.cat((cache_input, input_var), dim=2)
#                 with torch.no_grad():
#                     feat = model(cache_input)
#                 feat = feat.cpu()
#                 feat_np = feat.numpy().reshape(-1)
#                 feat_np -= feat_np.max()
#                 softmax = np.exp(feat_np) / np.sum(np.exp(feat_np))
#                 label = "NULL"
#                 confidence = 0.0
#                 if max(softmax) > SOFTMAX_THRES:
#                     idx = np.argmax(feat.numpy(), axis=1)[0]
#                     label = labels[idx]
#                     confidence = float(max(softmax))
#                 await websocket.send_json({
#                     "label": label,
#                     "confidence": confidence,
#                 })
#             await asyncio.sleep(0.01)  # 控制推理频率，可根据前端采样速度适当调整
#     except Exception as e:
#         print("ws error:", e)
#     finally:
#         await websocket.close()

@app.post("/predict/video")
async def predict_video(
        model: str = Form(...),
        weight: str = Form(...),
        video_style: str = Form(...),
        centercrop: bool = Form(False),
        video_path: str = Form(None),
        file: UploadFile = File(None)
):
    if video_path:
        video_filename = os.path.basename(video_path)
        video_path_full = video_path
    else:
        ext = os.path.splitext(file.filename)[-1].lower()
        video_uuid = uuid.uuid4().hex
        src_path = os.path.join("data/videos", f"{video_uuid}{ext}")
        with open(src_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # 如果是webm，转成mp4
        if ext == '.webm':
            mp4_path = os.path.join("data/videos", f"{video_uuid}.mp4")
            ffmpeg_path = r"D:\softwares\ffmpeg\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
            cmd = [
                ffmpeg_path, "-y",
                "-i", src_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                mp4_path
            ]
            subprocess.run(cmd, check=True)
            video_filename = os.path.basename(mp4_path)
            video_path_full = mp4_path
        else:
            video_filename = os.path.basename(src_path)
            video_path_full = src_path
    ida, prediction = predict(video_filename, model, weight, False, video_style, centercrop)

    ida = safe(ida)
    prediction_py = []
    for row in prediction:
        # row[0]: 类别名，row[1]: 置信度(小数)
        conf = safe(row[1])
        if isinstance(conf, str):
            try:
                conf_val = float(conf.strip('%'))
            except:
                conf_val = 0.0
        else:
            conf_val = float(conf)
        conf_str = f"{conf_val:.3f}%"  # 始终格式化为字符串带百分号
        prediction_py.append([safe(row[0]), conf_str])

    return {
        "filename": video_filename,
        "index": ida,
        "results": prediction_py
    }



@app.post("/predict/images")
async def predict_images(
        model: str = Form(...),
        weight: str = Form(...),
        video_style: str = Form(...),
        centercrop: bool = Form(False)
):
    video_filename = f"{uuid.uuid4().hex}.mp4"
    video_path = os.path.join("data/videos", video_filename)

    image_to_video(sample_dir="data/images", video_name=video_path)
    ida, prediction = predict(video_filename, model, weight, False, video_style, centercrop)

    return {"filename": video_filename, "index": ida, "results": prediction}
