<template>
  <div class="about-container">
    <h1 class="about-title">平台使用说明</h1>
    <div class="about-content">
      <section>
        <h2>首页功能</h2>
        <ol>
          <li>
            <b>上传视频：</b>
            <div>选择模型与权重，视频方式选“上传视频”，在侧边栏上传已有视频，点击“开始识别”即可得到识别结果。</div>
          </li>
          <li>
            <b>录制视频：</b>
            <div>选择模型与权重，视频方式选“录制视频”，点击“开始录制”后使用摄像头采集视频，录制结束后点“停止录制”，再点击“开始识别”获得识别结果。</div>
          </li>
          <li>
            <b>测试集视频：</b>
            <div>选择模型与权重，视频方式选“CSL测试集”，选择测试视频后点击“开始识别”可获得识别结果与模型准确率。</div>
          </li>
          <li>
            <b>实时识别：</b>
            <div>点击“实时识别”进入实时识别界面，摄像头下实时显示当前手语的识别结果。</div>
          </li>
          <li>
            <b>结果可视化：</b>
            <div>主页支持 acc 曲线、loss 曲线和网络结构可视化等。</div>
          </li>
        </ol>
      </section>

      <section>
        <h2>学习功能</h2>
        <ol>
          <li>
            <b>词汇学习：</b>
            <div>浏览手语词汇，观看演示视频、查看动作说明和中文释义。支持关键词搜索。</div>
          </li>
          <li>
            <b>AI 问答：</b>
            <div>输入有关手语的问题，获取 AI 专业解答和学习建议。</div>
          </li>
        </ol>
      </section>

      <section>
        <h2>练习与记录</h2>
        <ol>
          <li>
            <b>练习功能：</b>
            <div>填写练习目标，录制并提交视频，获得模型预测结果与 AI 智能点评。</div>
          </li>
          <li>
            <b>练习记录：</b>
            <div>随时查看自己的历次练习，包括目标、时间、视频、预测与智能建议，方便持续提升。</div>
          </li>
        </ol>
      </section>
    </div>
  </div>
</template>

<style scoped>
.about-container {
  max-width: 900px;
  margin: 40px auto 0;
  /* background: #fff; */    /* 移除背景 */
  /* border-radius: 14px; */ /* 移除圆角 */
  /* box-shadow: 0 2px 16px rgba(0,0,0,0.07); */ /* 移除阴影 */
  padding: 36px 40px 32px 40px;
}

.about-title {
  font-size: 2.3rem;
  font-weight: bold;
  color: #2d3748;
  text-align: center;
  margin-bottom: 32px;
  letter-spacing: 1px;
}

.about-content h2 {
  color: #4183f2;
  margin-top: 18px;
  font-size: 1.35rem;
  font-weight: 600;
}

.about-content ol {
  margin: 0 0 14px 0;
  padding-left: 20px;
}

.about-content li {
  margin-bottom: 12px;
  font-size: 1rem;
}

.about-content b {
  color: #222;
  font-weight: 600;
}

.about-content div {
  color: #555;
  margin-top: 4px;
  margin-bottom: 2px;
  font-size: 0.98rem;
  line-height: 1.8;
}

@media (max-width: 600px) {
  .about-container {
    padding: 16px 8px;
  }
  .about-title {
    font-size: 1.5rem;
  }
}
</style>
