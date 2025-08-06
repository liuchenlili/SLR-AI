<template>
  <div id="globalHeader">
    <a-row :wrap="false">
      <a-col flex="210px">
        <RouterLink to="/">
          <div class="title-bar">
            <img class="logo" src="../assets/logo.jpg" alt="logo" />
            <div class="title">智能手语教学平台</div>
          </div>
        </RouterLink>
      </a-col>
      <a-col flex="auto">
        <a-menu
          v-model:selectedKeys="current"
          mode="horizontal"
          :items="items"
          @click="doMenuClick"
        />
      </a-col>
      <a-col flex="120px">
        <div class="user-login-status">
          <div v-if="loginUserStore.loginUser.id">
            <a-dropdown>
              <a-space>
                <a-avatar :src="loginUserStore.loginUser.userAvatar" />
                {{ loginUserStore.loginUser.userName ?? '无名' }}
              </a-space>
              <template #overlay>
                <a-menu>
                  <a-menu-item>
                    <router-link to="/user/edit">
                      <UserOutlined />
                      用户信息
                    </router-link>
                  </a-menu-item>
                  <a-menu-item @click="doLogout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
          <div v-else>
            <a-button type="primary" href="/user/login">登录</a-button>
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>
<script lang="ts" setup>
import { computed, h, ref } from 'vue'
import { EditOutlined, HomeOutlined,UserOutlined,BookOutlined,LogoutOutlined,NotificationOutlined } from '@ant-design/icons-vue'
import { type MenuProps, message } from 'ant-design-vue'
import { useRouter } from "vue-router";
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'
import { userLogout } from '@/api/userController.ts'
const router = useRouter();
const loginUserStore = useLoginUserStore()

// 路由跳转事件
const doMenuClick = ({ key }: { key: string }) => {
  router.push({
    path: key,
  });
};
// 当前选中菜单
const current = ref<string[]>([]);
// 监听路由变化，更新当前选中菜单
router.afterEach((to, from, next) => {
  current.value = [to.path];
});

const items = computed<MenuProps['items']>(() => {
  const base = [
    {
      key: '/',
      icon: () => h(HomeOutlined),
      label: '模型指标',
      title: '模型指标',
    },
    {
      key: '/about',
      icon: () => h(NotificationOutlined),
      label: '使用说明',
      title: '使用说明',
    },
  ];

  // 登录用户菜单
  const userMenus = [
    {
      key: '/learn',
      icon: () => h(BookOutlined),
      label: '视频学习',
      title: '视频学习',
    },
    {
      key: '/practice',
      icon: () => h(EditOutlined),
      label: '智能手语识别',
      title: '智能手语识别',
    },
    {
      key: '/real',
      icon: () => h(EditOutlined),
      label: '实时识别',
      title: '实时识别',
    },
    {
      key: '/practice/history',
      icon: () => h(HomeOutlined),
      label: '识别记录',
      title: '识别记录',
    },
  ];

  // 管理员菜单
  const adminMenus = [
    {
      key: '/admin/userManage',
      icon: () => h(UserOutlined),
      label: '用户管理',
      title: '用户管理',
    },
  ];

  // 根据登录状态和用户角色动态组合菜单
  if (loginUserStore.loginUser.id) {
    // 已登录
    if (loginUserStore.loginUser.userRole === 'admin') {
      // 管理员用户
      return [...base, ...userMenus, ...adminMenus];
    }
    // 普通登录用户
    return [...base, ...userMenus];
  }

  // 未登录用户
  return base;
});
// 用户注销
const doLogout = async () => {
  const res = await userLogout()
  console.log(res)
  if (res.data.code === 0) {
    loginUserStore.setLoginUser({
      userName: '未登录',
    })
    message.success('退出登录成功')
    await router.push('/user/login')
  } else {
    message.error('退出登录失败，' + res.data.message)
  }
}
</script>
<style scoped>
#globalHeader .title-bar {
  display: flex;
  align-items: center;
}

.title {
  color: black;
  font-size: 18px;
  margin-left: 16px;
}
.logo {
  height: 48px;
}
</style>
