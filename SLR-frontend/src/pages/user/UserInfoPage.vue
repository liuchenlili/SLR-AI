<template>
  <div class="user-info-page">
    <div class="content-container">
      <!-- 页面头部 -->
      <div class="header-section">
        <h1 class="page-title">个人信息</h1>
      </div>

      <!-- 用户信息卡片 -->
      <div class="info-card">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <div class="avatar-container">
            <img 
              :src="formState.userAvatar || '/simple-avatar.svg'" 
              alt="用户头像" 
              class="user-avatar"
            />
          </div>
          <div class="user-basic-info">
            <h2 class="user-name">{{ formState.userName || '未设置昵称' }}</h2>
            <div class="user-role">{{ getRoleText(formState.userRole) }}</div>
          </div>
        </div>

        <!-- 表单区域 -->
        <form @submit.prevent="handleSubmit" class="info-form">
          <input type="hidden" v-model="formState.id" />
          
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">用户账号</label>
              <input 
                v-model="formState.userAccount" 
                type="text" 
                class="form-input"
                readonly
                placeholder="用户账号"
              />
            </div>

            <div class="form-group">
              <label class="form-label">昵称</label>
              <input 
                v-model="formState.userName" 
                type="text" 
                class="form-input"
                placeholder="请输入昵称"
                maxlength="20"
              />
            </div>
          </div>

          <!-- 个人简介 -->
          <div class="form-group">
            <label class="form-label">个人简介</label>
            <textarea 
              v-model="formState.userProfile" 
              class="form-textarea"
              placeholder="介绍一下自己吧..."
              maxlength="200"
            ></textarea>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="loading">
              {{ loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 安全设置 -->
      <div class="security-card">
        <h3 class="card-title">安全设置</h3>
        <div class="security-actions">
          <button class="security-btn" @click="handlePasswordChange">修改密码</button>
          <button class="security-btn logout-btn" @click="handleLogout">退出登录</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import router from '@/router'
import { updateUser, userLogout } from '@/api/userController.ts'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'

const loading = ref(false)

// 表单数据结构
const formState = reactive({
  id: undefined as number | undefined,
  userAccount: '',
  userName: '',
  userAvatar: '',
  userProfile: '',
  userRole: 'user',
})

const loginUserStore = useLoginUserStore()

// 获取角色文本
const getRoleText = (role: string) => {
  const roleMap: { [key: string]: string } = {
    'user': '普通用户',
    'admin': '管理员',
    'vip': 'VIP用户'
  }
  return roleMap[role] || '普通用户'
}

// 获取数据
const fetchData = async () => {
  const userData = loginUserStore.loginUser
  Object.assign(formState, userData)
}

// 页面加载时获取数据
onMounted(() => {
  fetchData()
})

// 提交表单
const handleSubmit = async () => {
  if (!formState.userName?.trim()) {
    message.warning('请输入用户昵称')
    return
  }

  loading.value = true
  try {
    const res = await updateUser(formState)
    if (res.data.code === 0 && res.data.data) {
      await loginUserStore.fetchLoginUser()
      fetchData()
      message.success('信息更新成功')
    } else {
      message.error('更新失败：' + res.data.message)
    }
  } catch (error) {
    message.error('更新失败，请重试')
  } finally {
    loading.value = false
  }
}

// 更换头像
const handleAvatarChange = () => {
  message.info('头像上传功能正在开发中...')
  // TODO: 实现头像上传功能
}

// 修改密码
const handlePasswordChange = () => {
  message.info('密码修改功能正在开发中...')
  // TODO: 跳转到密码修改页面
}

// 退出登录
const handleLogout = async () => {
  try {
    const res = await userLogout()
    if (res.data.code === 0) {
      loginUserStore.setLoginUser({ userName: '未登录' })
      message.success('退出登录成功')
      await router.push('/user/login')
    } else {
      message.error('退出登录失败：' + res.data.message)
    }
  } catch (error) {
    message.error('退出登录失败')
  }
}
</script>

<style scoped>
.user-info-page {
  min-height: 100vh;
  background: #fafafa;
  padding: 24px;
}

.content-container {
  max-width: 600px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 500;
  color: #333;
  margin: 0;
}

.info-card, .security-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e5e5;
  margin-bottom: 20px;
  overflow: hidden;
}

.avatar-section {
  background: #f8f9fa;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ddd;
}

.user-name {
  font-size: 20px;
  font-weight: 500;
  margin: 0 0 4px 0;
  color: #333;
}

.user-role {
  font-size: 14px;
  color: #666;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.info-form {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  font-family: inherit;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.form-input[readonly] {
  background: #f5f5f5;
  color: #666;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  text-align: center;
  margin-top: 24px;
}

.submit-btn {
  padding: 10px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background: #45a049;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.security-card {
  padding: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 16px 0;
}

.security-actions {
  display: flex;
  gap: 12px;
}

.security-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.security-btn:hover {
  border-color: #4CAF50;
  color: #4CAF50;
}

.logout-btn:hover {
  border-color: #f44336;
  color: #f44336;
}

@media (max-width: 768px) {
  .user-info-page {
    padding: 16px;
  }
  
  .content-container {
    max-width: 100%;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .info-form {
    padding: 20px;
  }
  
  .security-actions {
    flex-direction: column;
  }
}
</style>
