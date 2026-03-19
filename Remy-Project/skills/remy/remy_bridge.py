import sys
import json
import os
import re
import datetime
from PIL import Image
import google.genai as genai

# --- 1. 配置与初始化 ---
MEMORY_FILE = "remy_memory.md"

# 建议通过环境变量获取 API Key，更安全
api_key = os.getenv("GOOGLE_API_KEY") 
if not api_key:
    # 也可以手动填入作为后备
    api_key = "你的_API_KEY" 

genai.configure(api_key=api_key)
# 使用 1.5-flash 模型以获得更快的响应速度，适合 Agent 调用
model = genai.GenerativeModel('gemini-1.5-flash') 

def read_memory():
    if not os.path.exists(MEMORY_FILE):
        return "- 暂时还没有记录您的偏好哦。"
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read()

def main():
    # 检查命令行参数：需传入图片路径
    if len(sys.argv) < 2:
        print(json.dumps({"error": "未提供图片路径"}))
        return

    image_path = sys.argv[1]
    
    # 如果 OpenClaw 传入了当前的库存状态字符串，可以作为第二个参数接收
    current_inventory_str = sys.argv[2] if len(sys.argv) > 2 else "目前冰箱是空的"

    try:
        image = Image.open(image_path)
        user_prefs = read_memory()

        # 复用 RemyApp.py 中的核心 Prompt 逻辑
        prompt = f"""
        你是一位温馨、懂生活的家庭大厨。请观察这张新买食材的图片。
        已知冰箱里【已经有】以下食材：{current_inventory_str}。
        用户当下的【饮食偏好/记忆】如下：{user_prefs}

        核心指令：你必须严格提供至少 4 道完全不同的菜谱！
        请结合【图片中的新食材】和【已有的食材】，严格按以下 JSON 格式返回结果（不要任何 Markdown 标记）：
        {{
          "new_items": [
            {{"name": "食材名", "quantity": 数量(纯数字), "unit": "单位", "expiry_days": 预估能放几天(整数)}}
          ],
          "recipes": [
            {{
              "title": "菜名", "reason": "推荐理由", "ingredients": ["所需食材"], "steps": ["步骤1", "步骤2"], "link": "https://www.xiachufang.com/search/?keyword=菜名"
            }}
          ],
          "shopping": {{
            "urgent": ["缺货常备品"],
            "deals": ["推荐购买的生鲜食材(附带原因)"]
          }}
        }}
        """

        # 调用模型
        response = model.generate_content([prompt, image])
        
        # 清理返回的文本，确保它是纯 JSON
        raw_text = response.text.strip().strip('```json').strip('```').strip()
        
        # 直接输出 JSON 给标准输出 (stdout)，供 OpenClaw 读取
        print(raw_text)

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()