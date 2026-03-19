---
name: remy-omni-chef
description: Remy 的全能核心指令集。实现从“照片识别”到“食谱生成”及“自动补货”的完整闭环。集成视觉理解、长期偏好记忆与外部生鲜采购接口。
homepage: https://remy-project.io/skills/omni-chef
metadata: {
  "clawdbot": {
    "emoji": "🐭",
    "requires": {
      "python_packages": ["google-generativeai", "pillow"],
      "bins": ["remy-delivery-cli"]
    },
    "install": [
      { "id": "pip", "kind": "pip", "module": "google-generativeai", "label": "安装 Gemini SDK" },
      { "id": "pip", "kind": "pip", "module": "pillow", "label": "安装图像处理库" }
    ]
  }
}
---

# Remy Omni-Chef 核心工作流

目标：通过一张冰箱照片，自动完成库存审计、食谱推送和缺货补足。

## 1. 核心触发与指令 (Commands)
当 Agent 检测到用户上传图片或询问“冰箱里有什么”时，将调用以下桥接脚本执行核心推理：

```bash
python remy_bridge.py {{image_path}} "{{inventory_summary}}"