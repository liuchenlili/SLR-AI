import { defineStore } from 'pinia';
import axios from 'axios';
import { getWeights } from '@/api/predictionController.ts'

interface Prediction {
  ida: number;
  prediction: [string, number][];
  results: [];
}

interface ConfigState {
  models: string[];
  selectedModel: string;
  weights: string[];
  selectedWeight: string;
  videoStyles: string[];
  selectedVideoStyle: string;
  uploadedVideo: File | null;
  recordedVideo: Blob | null;
  selectedCSLVideo: string;
  cslVideos: string[];
  prediction: Prediction | null;
  isValid: boolean;
  isRealtime: boolean;             // 是否处于实时识别状态
  realtimeFrame: string;           // 摄像头帧（base64）
  realtimeLabel: string;           // 实时识别标签
  realtimeConfidence: number;      // 实时置信度
  realtimeThres: number;    // SOFTMAX阈值
}

export const useConfigStore = defineStore('cslConfig', {
  state: (): ConfigState => ({
    models: ['r2+1d_100', 'r3d_100', 'LSTM_100', 'r2+1d_500', 'r3d_500','SignFormer_100'],
    selectedModel: 'r2+1d_100',
    weights: [],
    selectedWeight: 'r2+1d18_epoch012.pth',
    videoStyles: ['上传视频', '录制视频', 'CSL测试集'],
    selectedVideoStyle: '上传视频',
    uploadedVideo: null,
    recordedVideo: null,
    selectedCSLVideo: '',
    cslVideos: Array.from({ length: 500 }, (_, i) => `${i.toString().padStart(3, '0')}.mp4`),
    prediction: null,
    isValid: false,
    isRealtime: false,
    realtimeFrame: '',
    realtimeLabel: '',
    realtimeConfidence: 0,
    realtimeThres: 0.75,      // 默认阈值
  }),
  actions: {
    async fetchWeights() {
      const res = await getWeights({ model: this.selectedModel })
      this.weights = res.data || []
      this.selectedWeight = this.weights[0] || ''
    },
    setSelectedModel(model: string) {
      this.selectedModel = model;
      this.isValid = false;
    },
    setSelectedWeight(weight: string) {
      this.selectedWeight = weight;
      this.isValid = false;
    },
    setSelectedVideoStyle(style: string) {
      this.selectedVideoStyle = style;
      this.isValid = false;
    },
    setUploadedVideo(video: File) {
      this.uploadedVideo = video;
      this.isValid = true;
    },
    setRecordedVideo(video: Blob) {
      this.recordedVideo = video;
      this.isValid = true;
    },
    setSelectedCSLVideo(video: string) {
      this.selectedCSLVideo = video;
      this.isValid = true;
    },
    setPrediction(prediction: Prediction) {
      this.prediction = prediction;
    },
    // ===== 实时识别WebSocket控制 =====
    startRealtime() {
      this.isRealtime = true
    },
    stopRealtime() {
      this.isRealtime = false
      this.realtimeFrame = ''
      this.realtimeLabel = ''
      this.realtimeConfidence = 0
    },
    updateRealtimeResult(img: string, label: string, conf: number) {
      this.realtimeFrame = img
      this.realtimeLabel = label
      this.realtimeConfidence = conf
    },

  }
});
