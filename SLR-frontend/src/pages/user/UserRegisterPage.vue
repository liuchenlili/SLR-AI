<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1 class="register-title">创建账号</h1>
        <p class="register-subtitle">加入智能手语教学平台</p>
      </div>

      <form @submit.prevent="handleSubmit" class="register-form">
        <div class="form-group">
          <label class="form-label">账号</label>
          <input
            v-model="formState.userAccount"
            type="text"
            class="form-input"
            placeholder="请输入账号"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="formState.userPassword"
            type="password"
            class="form-input"
            placeholder="请输入密码"
            required
            minlength="8"
          />
        </div>

        <div class="form-group">
          <label class="form-label">确认密码</label>
          <input
            v-model="formState.checkPassword"
            type="password"
            class="form-input"
            placeholder="请再次输入密码"
            required
            minlength="8"
          />
        </div>

        <button type="submit" class="register-button" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>

        <div class="register-footer">
          <span class="footer-text">已有账号？</span>
          <router-link to="/user/login" class="footer-link">立即登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import router from '@/router'
import { useLoginUserStore } from '@/stores/useLoginUserStore'
import { userRegister } from '@/api/userController.ts'

// 用于接受表单输入的值
const formState = reactive<API.UserRegisterRequest>({
  userAccount: '',
  userPassword: '',
  checkPassword: '',
})

const loading = ref(false)
const loginUserStore = useLoginUserStore()

/**
 * 提交表单
 */
const handleSubmit = async () => {
  if (!formState.userAccount || !formState.userPassword || !formState.checkPassword) {
    message.warning('请填写完整信息')
    return
  }

  if (formState.userPassword.length < 8) {
    message.warning('密码长度不能小于 8 位')
    return
  }

  // 校验两次输入的密码是否一致
  if (formState.userPassword !== formState.checkPassword) {
    message.error('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    const res = await userRegister(formState)
    // 注册成功，跳转到登录页面
    if (res.data.code === 0 && res.data.data) {
      message.success('注册成功')
      router.push({
        path: '/user/login',
        replace: true,
      })
    } else {
      message.error('注册失败，' + res.data.message)
    }
  } catch (error) {
    message.error('注册失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 20px;
  padding: 48px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
  width: 100%;
  max-width: 400px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.register-subtitle {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.form-input {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background: #fefefe;
}

.form-input:focus {
  outline: none;
  border-color: #64748b;
  box-shadow: 0 0 0 3px rgba(100, 116, 139, 0.1);
  background: white;
}

.form-input::placeholder {
  color: #94a3b8;
}

.register-button {
  width: 100%;
  padding: 14px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.register-button:hover:not(:disabled) {
  background: #1a252f;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.register-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}

.footer-text {
  color: #64748b;
  font-size: 0.875rem;
}

.footer-link {
  color: #2c3e50;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: #64748b;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-container {
    padding: 32px 24px;
    margin: 20px;
  }
  
  .register-title {
    font-size: 1.5rem;
  }
}
</style>
