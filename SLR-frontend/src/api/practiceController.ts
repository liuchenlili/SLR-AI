// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** 此处后端没有提供注释 POST /practice/add */
export async function addPracticeRecord(
  body: API.PracticeRecord,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseBoolean>('/practice/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 POST /practice/ask */
export async function askAi(body: Record<string, any>, options?: { [key: string]: any }) {
  return request<Record<string, any>>('/practice/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 POST /practice/fullPredict */
export async function fullPredict(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.fullPredictParams,
  body: {},
  file?: File,
  options?: { [key: string]: any }
) {
  const formData = new FormData()

  if (file) {
    formData.append('file', file)
  }

  Object.keys(body).forEach((ele) => {
    const item = (body as any)[ele]

    if (item !== undefined && item !== null) {
      if (typeof item === 'object' && !(item instanceof File)) {
        if (item instanceof Array) {
          item.forEach((f) => formData.append(ele, f || ''))
        } else {
          formData.append(ele, JSON.stringify(item))
        }
      } else {
        formData.append(ele, item)
      }
    }
  })

  return request<Record<string, any>>('/practice/fullPredict', {
    method: 'POST',
    params: {
      ...params,
    },
    data: formData,
    // requestType: 'form',
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 POST /practice/list/page/vo */
export async function listRecordByPage(
  body: API.PracticeRecordQueryRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponsePagePracticeRecord>('/practice/list/page/vo', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 GET /practice/listByUser */
export async function listByUser(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.listByUserParams,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseListPracticeRecord>('/practice/listByUser', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** 此处后端没有提供注释 GET /practice/listMy */
export async function listMyRecords(options?: { [key: string]: any }) {
  return request<API.BaseResponseListPracticeRecord>('/practice/listMy', {
    method: 'GET',
    ...(options || {}),
  })
}
