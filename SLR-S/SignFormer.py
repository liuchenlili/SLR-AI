import torch
import torch.nn as nn
from transformers import VideoMAEForVideoClassification

class SignFormer(nn.Module):
    """
    一个基于VideoMAE的孤立词手语识别模型，
    专门为CSL-500数据集（500个类别）进行微调。

    该模型利用在Kinetics-400上预训练的VideoMAE-Base模型，
    并将其分类头替换为适用于500个类别的新分类头。
    """
    def __init__(self, num_classes=500,pretrained_model_name=None):
        """
        初始化模型。

        Args:
            num_classes (int): 数据集中的类别数量，对于CSL-500，默认为500。
        """
        super().__init__()

        # 1. 定义预训练模型的名称
        #    我们选用在Kinetics-400上微调过的VideoMAE-Base模型，
        #    这是一个公认的、强大的视频理解骨干网络。
        pretrained_model_name = "./videomae-base-finetuned-kinetics"

        # 2. 从Hugging Face Hub加载预训练的VideoMAE模型
        #    这将下载模型配置和权重。
        #    模型结构是一个基于Vision Transformer (ViT)的编码器，
        #    后面跟着一个用于视频分类的线性层。
        self.videomae = VideoMAEForVideoClassification.from_pretrained(
            pretrained_model_name,
            ignore_mismatched_sizes=True, # 允许加载一个分类头尺寸不同的模型
            local_files_only=True
        )

        # 3. 替换分类头以适配CSL-500数据集
        #    原始模型的分类头是为Kinetics-400（400类）设计的。
        #    我们需要将其替换为一个新的、输出为500个类别的线性层。

        # 获取原始分类器输入特征的维度
        in_features = self.videomae.classifier.in_features

        # 创建一个新的线性层作为分类头
        self.videomae.classifier = nn.Linear(in_features, num_classes)

        print(f"模型初始化完成：")
        print(f"  - 骨干网络: {pretrained_model_name}")
        print(f"  - 新的分类头: {self.videomae.classifier}")
        print(f"  - 目标类别数: {num_classes}")


    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """
        定义模型的前向传播逻辑。

        Args:
            pixel_values (torch.Tensor): 预处理后的视频张量。
                                         形状应为 (B, C, T, H, W)，其中：
                                         B = 批次大小 (batch size)
                                         C = 通道数 (通常为3，代表RGB)
                                         T = 帧数 (number of frames)
                                         H = 高度 (height)
                                         W = 宽度 (width)

        Returns:
            torch.Tensor: 模型输出的logits，形状为 (B, num_classes)。
        """
        # pixel_values: [B, C, T, H, W] → 需要变成 [B, T, C, H, W]
        if pixel_values.shape[1] == 3:
            pixel_values = pixel_values.permute(0, 2, 1, 3, 4)  # [B, T, C, H, W]

        # 将视频张量输入到VideoMAE模型中
        outputs = self.videomae(pixel_values=pixel_values)

        # Hugging Face模型返回一个包含多个元素的输出对象，
        # 我们只需要其中的'logits'部分。
        logits = outputs.logits

        return logits

# --- 使用示例 ---
if __name__ == '__main__':
    # 检查是否有可用的GPU，否则使用CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"正在使用设备: {device}")

    # 1. 实例化我们为CSL-500定制的模型
    model = SignFormer(num_classes=500).to(device)
    model.eval() # 设置为评估模式

    # 2. 创建一个模拟的视频输入张量
    #    - 批次大小 B = 2 (2个视频)
    #    - 通道数 C = 3 (RGB)
    #    - 帧数 T = 16
    #    - 高度 H = 224
    #    - 宽度 W = 224
    #    这是VideoMAE模型的典型输入尺寸
    dummy_video_batch = torch.randn(2, 3, 16, 224, 224).to(device)
    dummy_video_batch = dummy_video_batch.permute(0, 2, 1, 3, 4)

    print(f"\n输入张量形状: {dummy_video_batch.shape}")

    # 3. 通过模型进行前向传播
    with torch.no_grad(): # 在评估时关闭梯度计算以节省资源
        logits = model(dummy_video_batch)

    # 4. 打印输出结果的形状
    #    输出应为 (批次大小, 类别数)，即 (2, 500)
    print(f"输出Logits形状: {logits.shape}")

    # 5. 检查输出的维度是否正确
    assert logits.shape == (2, 500)
    print("\n模型输出维度正确！")

    # 打印模型参数量
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"模型可训练参数总量: {total_params / 1_000_000:.2f} M")