

<template>
  <div class="realtime-demo" >
    <!-- 嵌入Streamlit实时识别界面 -->
    <iframe
      src="http://localhost:8501"
      width="100%" height="900px" frameborder="0">
    </iframe>

  </div>
</template>
<script setup lang="ts">

</script>
<style scoped>
.realtime-demo {
  padding-top: 0; /* 确保顶部内边距为0 */
  margin-top: 0;
}
</style>
