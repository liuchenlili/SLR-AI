<template>
  <div id="userLoginPage">
    <h2 class="title">用户信息</h2>
    <div class="desc">智能手语教学平台</div>
    <a-form :model="formState" name="basic" autocomplete="off" @finish="handleSubmit">
      <!-- ID (隐藏字段) -->
      <a-form-item hidden name="id">
        <a-input v-model:value="formState.id" />
      </a-form-item>
      <!-- 头像 -->
      <a-form-item label="用户头像" name="userAvatar">
        <a-space>
          <a-avatar :src="formState.userAvatar" />

        </a-space>
      </a-form-item>
      <!-- 账号 -->
      <a-form-item label="用户账号" name="userAccount">
        <a-input v-model:value="formState.userAccount" />
      </a-form-item>

      <!-- 昵称 -->
      <a-form-item label="用户昵称" name="userName">
        <a-input v-model:value="formState.userName" />
      </a-form-item>


      <!-- 简介 -->
      <a-form-item label="用户简介" name="userProfile">
        <a-textarea v-model:value="formState.userProfile" :rows="4" placeholder="请输入个人简介" />
      </a-form-item>

      <!-- 角色 -->
      <a-form-item label="用户角色" name="userRole">
        {{ formState.userRole }}
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit" style="width: 100%">提交</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>
<script lang="ts" setup>
import { onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue'
import router from '@/router'
import { updateUser } from '@/api/userController.ts'
import { useLoginUserStore } from '@/stores/useLoginUserStore.ts'

// 表单数据结构
const formState = reactive({
  id: null,
  userAccount: '',
  userName: '',
  userAvatar: '',
  userProfile: '',
  userRole: 'user',
})
const loginUserStore = useLoginUserStore()

// 获取数据
const fetchData = async () => {
  const userData = loginUserStore.loginUser
  Object.assign(formState, userData)
}

// 页面加载时获取数据，请求一次
onMounted(() => {
  fetchData()
})
/**
 * 提交表单
 * @param values
 */
const handleSubmit = async (values: any) => {
  console.log(formState)
  const res = await updateUser(values)
  //成功，保存到全局状态中
  if (res.data.code === 0 && res.data.data) {
    await loginUserStore.fetchLoginUser()
    fetchData()
    message.success('编辑成功')
  } else {
    message.error('编辑失败，' + res.data.message)
  }
}
</script>

<style scoped>
#userLoginPage {
  max-width: 360px;
  margin: 0 auto;
}

.title {
  text-align: center;
  margin-bottom: 16px;
}

.desc {
  text-align: center;
  color: #bbb;
  margin-bottom: 16px;
}
</style>
