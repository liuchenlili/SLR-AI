<template>
  <header class="global-header">
    <div class="header-container">
      <!-- Logo 区域 -->
      <RouterLink to="/" class="logo-section">
        <img src="../assets/logo.jpg" alt="SLR-AI" class="logo-image" />
        <div class="logo-text">
          <span class="brand-name">智能手语教学平台</span>
          <span class="brand-subtitle">SLR-AI</span>
        </div>
      </RouterLink>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon">
            {{ item.path === '/' ? '🏠' :
               item.path === '/models' ? '📊' :
               item.path === '/about' ? 'ℹ️' :
               item.path === '/learn' ? '📚' :
               item.path === '/practice' ? '📷' :
               item.path === '/real' ? '🎥' :
               item.path === '/practice/history' ? '📋' :
               item.path === '/admin/userManage' ? '👤' : '•' }}
          </span>
          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- 用户区域 -->
      <div class="user-section">
        <div v-if="loginUserStore.loginUser.id" class="user-info">
          <div class="user-dropdown" @click="toggleDropdown">
            <img
              :src="loginUserStore.loginUser.userAvatar || '/simple-avatar.svg'"
              alt="用户头像"
              class="user-avatar"
            />
            <span class="user-name">{{ loginUserStore.loginUser.userName || '用户' }}</span>
            <svg class="dropdown-arrow" :class="{ open: dropdownOpen }" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
            </svg>
          </div>

          <div v-if="dropdownOpen" class="dropdown-menu" @click="closeDropdown">
            <RouterLink to="/user/edit" class="dropdown-item">
              <UserOutlined class="dropdown-icon" />
              <span>个人信息</span>
            </RouterLink>
            <div class="dropdown-item" @click="doLogout">
              <LogoutOutlined class="dropdown-icon" />
              <span>退出登录</span>
            </div>
          </div>
        </div>

        <RouterLink v-else to="/user/login" class="login-btn">
          <span>登录</span>
        </RouterLink>
      </div>
    </div>
  </header>
</template>
<script lang="ts" setup>
import { computed, ref } from 'vue'
import { UserOutlined, LogoutOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useRouter, useRoute } from "vue-router"
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { userLogout } from '@/api/userController.ts'

const router = useRouter()
const route = useRoute()
const loginUserStore = useLoginUserStore()
const dropdownOpen = ref(false)

// 导航项目配置
const navItems = computed(() => {
  const baseItems = [

    { path: '/models', label: '模型指标', icon: 'ChartIcon' },
    { path: '/about', label: '使用说明', icon: 'InfoIcon' }
  ]

  if (loginUserStore.loginUser.id) {
    const userItems = [
      { path: '/', label: '首页', icon: 'HomeIcon' },
      { path: '/learn', label: '学习中心', icon: 'BookIcon' },
      { path: '/practice', label: '智能识别', icon: 'CameraIcon' },
      { path: '/real', label: '实时识别', icon: 'VideoIcon' },
      { path: '/practice/history', label: '练习记录', icon: 'HistoryIcon' }
    ]

    if (loginUserStore.loginUser.userRole === 'admin') {
      userItems.push({ path: '/admin/userManage', label: '用户管理', icon: 'AdminIcon' })
    }

    return [...userItems, ...baseItems]
  }

  return baseItems
})

// 判断导航项是否激活
const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 切换下拉菜单
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

// 关闭下拉菜单
const closeDropdown = () => {
  dropdownOpen.value = false
}

// 用户注销
const doLogout = async () => {
  try {
    const res = await userLogout()
    if (res.data.code === 0) {
      loginUserStore.setLoginUser({ userName: '未登录' })
      message.success('退出登录成功')
      await router.push('/user/login')
    } else {
      message.error('退出登录失败，' + res.data.message)
    }
  } catch (error) {
    message.error('退出登录失败')
  }
  closeDropdown()
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownOpen.value) {
    const dropdown = (event.target as Element)?.closest('.user-dropdown')
    if (!dropdown) {
      closeDropdown()
    }
  }
}

// 监听点击事件
document.addEventListener('click', handleClickOutside)

// 简单的图标组件
const HomeIcon = () => '🏠'
const ChartIcon = () => '📊'
const InfoIcon = () => 'ℹ️'
const BookIcon = () => '📚'
const CameraIcon = () => '📷'
const VideoIcon = () => '🎥'
const HistoryIcon = () => '📋'
const AdminIcon = () => '👤'
</script>

<style scoped>
.global-header {
  background: linear-gradient(135deg, #ffffff 0%, #fafafa 100%);
  border-bottom: 1px solid #e8e5dd;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

/* Logo 区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  transition: transform 0.3s ease;
}

.logo-section:hover {
  transform: scale(1.02);
}

.logo-image {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid #e8e5dd;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1;
}

.brand-subtitle {
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1;
  font-weight: 500;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item:hover {
  background: #f8f9fa;
  color: #6a9f7a;
  transform: translateY(-1px);
}

.nav-item.active {
  background: linear-gradient(135deg, #6a9f7a 0%, #5a8a6a 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(106, 159, 122, 0.3);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #6a9f7a;
  border-radius: 50%;
}

.nav-icon {
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  white-space: nowrap;
}

/* 用户区域 */
.user-section {
  position: relative;
}

.user-info {
  position: relative;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.user-dropdown:hover {
  background: #f8f9fa;
  border-color: #e8e5dd;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e8e5dd;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-avatar:hover {
  border-color: #6a9f7a;
  box-shadow: 0 4px 12px rgba(106, 159, 122, 0.2);
  transform: scale(1.05);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  fill: #7f8c8d;
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid #e8e5dd;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  min-width: 160px;
  overflow: hidden;
  z-index: 1000;
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #495057;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border-bottom: 1px solid #f1f1f1;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f8f9fa;
  color: #6a9f7a;
}

.dropdown-icon {
  font-size: 14px;
  color: #7f8c8d;
}

.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: linear-gradient(135deg, #6a9f7a 0%, #5a8a6a 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.login-btn:hover {
  background: linear-gradient(135deg, #5a8a6a 0%, #4a7a5a 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(106, 159, 122, 0.3);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
  }

  .logo-text {
    display: none;
  }

  .nav-menu {
    gap: 4px;
  }

  .nav-item {
    padding: 6px 8px;
    font-size: 13px;
  }

  .nav-label {
    display: none;
  }

  .nav-icon {
    font-size: 18px;
  }

  .user-name {
    display: none;
  }
}

@media (max-width: 640px) {
  .nav-menu {
    gap: 2px;
  }

  .nav-item {
    padding: 6px;
  }
}
</style>
