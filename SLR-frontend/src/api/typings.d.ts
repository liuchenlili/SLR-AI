declare namespace API {
  type BaseResponseBoolean = {
    code?: number
    data?: boolean
    message?: string
  }

  type BaseResponseListPracticeRecord = {
    code?: number
    data?: PracticeRecord[]
    message?: string
  }

  type BaseResponseLoginUserVO = {
    code?: number
    data?: LoginUserVO
    message?: string
  }

  type BaseResponseLong = {
    code?: number
    data?: number
    message?: string
  }

  type BaseResponsePagePracticeRecord = {
    code?: number
    data?: PagePracticeRecord
    message?: string
  }

  type BaseResponsePageUserVO = {
    code?: number
    data?: PageUserVO
    message?: string
  }

  type BaseResponseUser = {
    code?: number
    data?: User
    message?: string
  }

  type BaseResponseUserVO = {
    code?: number
    data?: UserVO
    message?: string
  }

  type DeleteRequest = {
    id?: number
  }

  type fullPredictParams = {
    targetText: string
    model: string
    weight: string
    videoStyle: string
    centercrop: boolean
    video_path?: string
  }

  type getAccCurveParams = {
    model: string
  }

  type getByIdParams = {
    id: number
  }

  type getConfusionMatrixParams = {
    model: string
  }

  type getLossCurveParams = {
    model: string
  }

  type getNetworkGraphParams = {
    model: string
  }

  type getUserByIdParams = {
    id: number
  }

  type getUserVOByIdParams = {
    id: number
  }

  type getWeightsParams = {
    model: string
  }

  type listByUserParams = {
    userId: number
  }

  type LoginUserVO = {
    id?: number
    userAccount?: string
    userName?: string
    userAvatar?: string
    userProfile?: string
    userRole?: string
    editTime?: string
    createTime?: string
    updateTime?: string
  }

  type OrderItem = {
    column?: string
    asc?: boolean
  }

  type PagePracticeRecord = {
    records?: PracticeRecord[]
    total?: number
    size?: number
    current?: number
    orders?: OrderItem[]
    optimizeCountSql?: PagePracticeRecord
    searchCount?: PagePracticeRecord
    optimizeJoinOfCountSql?: boolean
    maxLimit?: number
    countId?: string
    pages?: number
  }

  type PageUserVO = {
    records?: UserVO[]
    total?: number
    size?: number
    current?: number
    orders?: OrderItem[]
    optimizeCountSql?: PageUserVO
    searchCount?: PageUserVO
    optimizeJoinOfCountSql?: boolean
    maxLimit?: number
    countId?: string
    pages?: number
  }

  type PracticeRecord = {
    id?: number
    userId?: number
    videoUrl?: string
    aiAdvice?: string
    predictJson?: string
    targetText?: string
    createTime?: string
  }

  type PracticeRecordQueryRequest = {
    current?: number
    pageSize?: number
    sortField?: string
    sortOrder?: string
    user_id?: number
    target_text?: string
  }

  type predictParams = {
    model: string
    weight: string
    videoStyle: string
    centercrop: boolean
    video_path?: string
  }

  type searchParams = {
    keyword: string
  }

  type SignWord = {
    id?: number
    word?: string
    videoUrl?: string
    actionDesc?: string
    chineseMeaning?: string
  }

  type User = {
    id?: number
    userAccount?: string
    userPassword?: string
    userName?: string
    userAvatar?: string
    userProfile?: string
    userRole?: string
    editTime?: string
    createTime?: string
    updateTime?: string
    isDelete?: number
  }

  type UserAddRequest = {
    userName?: string
    userAccount?: string
    userAvatar?: string
    userProfile?: string
    userRole?: string
  }

  type UserLoginRequest = {
    userAccount?: string
    userPassword?: string
  }

  type UserQueryRequest = {
    current?: number
    pageSize?: number
    sortField?: string
    sortOrder?: string
    id?: number
    userName?: string
    userAccount?: string
    userProfile?: string
    userRole?: string
  }

  type UserRegisterRequest = {
    userAccount?: string
    userPassword?: string
    checkPassword?: string
  }

  type UserUpdateRequest = {
    id?: number
    userName?: string
    userAvatar?: string
    userProfile?: string
    userRole?: string
  }

  type UserVO = {
    id?: number
    userAccount?: string
    userName?: string
    userAvatar?: string
    userProfile?: string
    userRole?: string
    createTime?: string
  }
}
