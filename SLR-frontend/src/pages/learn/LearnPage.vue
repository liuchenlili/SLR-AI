<template>
  <div style="padding:15px;">
    <a-tabs v-model:activeKey="activeTab" tabPosition="top">
      <a-tab-pane key="vocab" tab="词汇学习">
        <SignWordLearn />
      </a-tab-pane>
      <a-tab-pane key="ai" tab="AI问答">
        <SignAiQna />
      </a-tab-pane>
<!--      <a-tab-pane key="course" tab="课程学习">-->
<!--        <SignCourseLearn />-->
<!--      </a-tab-pane>-->
    </a-tabs>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import SignWordLearn from './SignWordLearn.vue'
import SignAiQna from './SignAiQna.vue'
import SignCourseLearn from './SignCourseLearn.vue'

const activeTab = ref('vocab')
</script>
