// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 此处后端没有提供注释 GET /python/metrics/acc */
export async function getAccCurve(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getAccCurveParams,
  options?: { [key: string]: any }
) {
  return request<string[]>('/python/metrics/acc', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 GET /python/metrics/confusion */
export async function getConfusionMatrix(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getConfusionMatrixParams,
  options?: { [key: string]: any }
) {
  return request<string>('/python/metrics/confusion', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 GET /python/metrics/loss */
export async function getLossCurve(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getLossCurveParams,
  options?: { [key: string]: any }
) {
  return request<string[]>('/python/metrics/loss', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 GET /python/net/graph */
export async function getNetworkGraph(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getNetworkGraphParams,
  options?: { [key: string]: any }
) {
  return request<string>('/python/net/graph', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 POST /python/predict */
/** POST /python/predict 文件上传+参数 */
export async function predict(
  params: {
    model: string
    weight: string
    videoStyle: string
    centercrop: boolean
    videoPath?: string        // 新增，测试集模式下要传
  },
  file: File,
  options?: { [key: string]: any }
) {
  const formData = new FormData()
  formData.append('model', params.model)
  formData.append('weight', params.weight)
  formData.append('videoStyle', params.videoStyle)
  formData.append('centercrop', String(params.centercrop))
  if (params.videoPath) {
    formData.append('video_path', params.videoPath) // CSL测试集传入
  }
  if (file) {
    formData.append('file', file) // 上传/录制传入
  }
  return request<string>('/python/predict', {
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...(options || {})
  })
}

/** 此处后端没有提供注释 GET /python/weights */
export async function getWeights(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getWeightsParams,
  options?: { [key: string]: any }
) {
  return request<string[]>('/python/weights', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}
