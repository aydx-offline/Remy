import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import datetime
import re
import os

MEMORY_FILE = "remy_memory.md"

# 初始化记忆文件
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write("# REMY 的主厨备忘录\n\n- 暂时还没有记录您的偏好哦。")

def read_memory():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read()

def save_memory(content):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# --- 1. 配置 Gemini API ---
# 建议实际开发时将 Key 存入 st.secrets 或环境变量
API_KEY = "AIzaSyAndZewKfOFF70RdtDGU19_CvqyaL7phbw"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.1-flash-image-preview')

# --- 2. 网页配置与温馨 UI 风格注入 ---
st.set_page_config(page_title="REMY | 你冰箱里的料理鼠王", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

def refresh_suggestions():
    # 1. 获取当前库存快照
    current_items = []
    for name, info in st.session_state.inventory.items():
        current_items.append(f"{name} (剩余{info['quantity']}{info['unit']}, { (info['expiry_date'] - st.session_state.current_date).days }天后过期)")
    
    inventory_str = "、".join(current_items) if current_items else "冰箱已经空了"
    
    # 2. 读取用户偏好
    user_prefs = read_memory()

    # 3. 构建文本提示词
    update_prompt = f"""
    你是一位温馨、懂生活的家庭大厨。现在冰箱的【实时库存】如下：{inventory_str}。
    
    用户当下的【饮食偏好/记忆】如下：
    {user_prefs}

    请根据以上信息，重新联动生成：
    1. 4个食谱（必须完全基于现有食材）。
    2. 采购清单（根据库存减少情况，推荐补货或解馋好物）。

    严格按 JSON 格式返回，不要有 Markdown 标记：
    {{
      "recipes": [
    {{
        "title": "菜名", "reason": "为什么推荐它", "ingredients": ["所需食材（需要多少颗菜/多少酱油/多少肉等）"], "steps": ["步骤1", "步骤2"（每一步前面加上序号，写清楚每一步烧多久、加多少分量的调味品等,"link": "https://www.xiachufang.com/search/?keyword=菜名"]
    }}
    ],
    "shopping": {{
    "urgent": ["缺货常备品1（仅包含平日需要储存在冰箱里的常备品，如鸡蛋、饮品、葱等等，这些不需要说明选购原因）"],
    "deals": ["生鲜食材的名称"（生成5-10个不等，种类需要包括：这几天需要用来做饭的食材、我喜欢的食物、正在打折的酸奶/冷链速食/甜品、降价生鲜、应季水果、网红食品、速食快手菜等）(在每一个产品后写上选购原因，8个汉字以内)]
    }}
    }}
    """
    
    try:
        response = model.generate_content(update_prompt)
        raw_text = response.text.strip().strip('```json').strip('```').strip()
        data = json.loads(raw_text)
        
        # 4. 更新全局状态
        st.session_state.recipes = data.get("recipes", [])
        st.session_state.shopping_list = data.get("shopping", {})
    except Exception as e:
        st.error(f"联动更新失败")


# 核心 CSS 改造区
st.markdown("""
<style>
    /* 1. 引入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Nunito:wght@400;600&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/lxgw-wenkai-lite-webfont@1.1.0/style.css');

    /* 2. 精准全局字体设置 (取消了 span 和 div 的强制覆盖，修复了箭头变成文字的 BUG) */
    .stApp { background-color: #FAF7F2 !important; }
    p, label, li, h2, h3, h4, h5, h6 { 
        color: #5C4D4D !important; 
        font-family: 'Nunito', 'LXGW WenKai Lite', sans-serif !important;
        letter-spacing: 0.5px !important;
    }
    
    .remy-title-wrapper {
        display: flex;
        justify-content: center;
        align-items: baseline; /* 让英文和中文在底部基线对齐 */
        margin-top: 2rem !important; 
        margin-bottom: 0.5rem !important;
        gap: 15px; /* 控制 REMY 和右侧小字之间的距离 */
    }

    .remy-giant-title {
        font-family: 'Caveat', 'LXGW WenKai Lite', sans-serif !important;
        font-size: 4.5rem !important; 
        color: #D47B55 !important;
        text-shadow: 2px 3px 10px rgba(212, 123, 85, 0.2) !important;
        line-height: 1.2 !important;
        margin: 0 !important; /* 去掉多余边距，交给 wrapper 控制 */
    }

    .remy-side-title {
        font-family: 'LXGW WenKai Lite', sans-serif !important;
        font-size: 1.6rem !important;
        color: #D47B55 !important;
        font-weight: 600 !important;
        margin: 0 !important;
        position: relative;
    }

    /* 把截图里顶部那条碍眼的白色系统导航栏变透明，完美融入燕麦色背景 */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    .remy-sub-title {
        text-align: center; 
        color: #8D6E63; 
        font-size: 1.2rem; 
        margin-top: 0px; 
        margin-bottom: 2rem; 
        font-style: italic;
    }

    /* 缩小页面顶部的留白空白区，让所有内容整体上移 */
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 3rem !important;
        max-width: 1200px !important; 
    }

    /* 4. 侧边栏整体美化 */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        font-family: 'LXGW WenKai Lite', sans-serif !important;
        font-size: 0.8rem !important;
        color: #8D7B68 !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
        line-height: 1.4 !important;
        display: block !important;
        opacity: 1 !important;
    }

    /* 5. 美化上传框 (File Uploader)：变得软糯、字号变小 */
    [data-testid="stFileUploader"] section {
        background-color: #FCFAF7 !important;
        border: 2px dashed #DCCDBA !important;
        border-radius: 20px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] div {
        font-size: 0.85rem !important; /* 缩小上传框里的提示字体 */
        color: #8D7B68 !important;
    }
    [data-testid="stFileUploader"] small {
        display: none !important; /* 隐藏讨厌的 "Limit 200MB per file" 英文提示 */
    }

    /* 6. 美化侧边栏的专属按钮：不抢戏，更温柔 */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent !important; 
        color: #D47B55 !important;
        border: 2px solid #D47B55 !important;
        border-radius: 20px !important; 
        box-shadow: none !important; 
        font-size: 1.1rem !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #D47B55 !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(212, 123, 85, 0.3) !important; 
    }

    div[data-baseweb="tab-list"] {
        display: flex !important;
        width: 100% !important; /* 强制占满全宽 */
    }

    button[data-baseweb="tab"] {
        flex: 1 !important; /* 👈 核心魔法：让三个 Tab 绝对平分、各占 1/3 */
        display: flex !important;
        justify-content: center !important; /* 让文字水平居中 */
        align-items: center !important; /* 让文字垂直居中 */
        padding: 1.2rem 0 !important; /* 把左右固定的 3rem 去掉，交给 flex 自动分配空间 */
        min-width: 0 !important; /* 去掉之前固定的 180px，防止在小屏幕上溢出 */
        border-radius: 25px 25px 0 0 !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.4s ease;
        text-align: center !important;
    }
    
    /* 🌟 核心修复：强制穿透，放大 Tab 内部的真正文字容器！ */
    button[data-baseweb="tab"] p, 
    button[data-baseweb="tab"] span, 
    button[data-baseweb="tab"] div {
        font-family: 'Nunito', 'LXGW WenKai Lite', sans-serif !important;
        font-size: 1.3rem !important; /* 保持你调整好的 1.3rem */
        font-weight: 600 !important; /* 稍微加粗一点，更有主菜单的气势 */
        color: #BCAAA4 !important; /* 未选中时，颜色稍微淡一点 */
        margin: 0 !important;
    }

    /* 被选中时 Tab 的背景和底线 */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FAF7F2 !important; /* 可以根据需要换成 #FCFAF7 增加层次感 */
        border-bottom: 4px solid #D47B55 !important;
    }
    
    /* 🌟 被选中时，里面的文字颜色变醒目 */
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span,
    button[data-baseweb="tab"][aria-selected="true"] div {
        color: #D47B55 !important; 
    }
            
    div[data-baseweb="tab-list"] {
        border-bottom: none !important; 
        gap: 10px;
        margin-bottom: 1.5rem !important;
    }
    
    /* 顺手把 Streamlit 可能自带的默认底层边框也彻底隐藏 */
    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    /* 主界面的按钮依然保持原本的高亮颜色 */
    .stTabs .stButton > button {
        background-color: #E28765 !important; 
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 30px !important; 
        padding: 0.6rem 1.5rem !important;
        font-family: 'Nunito', 'LXGW WenKai Lite', sans-serif !important;
        font-weight: bold;
        box-shadow: 0 6px 15px rgba(226, 135, 101, 0.25) !important; 
        transition: all 0.3s ease;
    }
    .stTabs .stButton > button:hover {
        transform: translateY(-3px) !important;
        background-color: #D47B55 !important;
    }

    div[data-testid="stExpander"] {
        border-radius: 24px !important; 
        border: 1px solid #F0EAE1 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 10px 30px rgba(141, 110, 99, 0.06) !important; 
        overflow: hidden !important;
        margin-bottom: 1.5rem !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #FCFAF7 !important; 
        padding: 1rem 1.5rem !important;
    }
    div[data-testid="stExpander"] summary p {
        font-family: 'Caveat', 'LXGW WenKai Lite', sans-serif !important;
        font-size: 1.2rem !important;
        color: #4A3B32 !important;
    }
    
    /* 7. 食材卡片基础样式 */
    .ingredient-card {
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 8px 24px rgba(141, 110, 99, 0.06);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        background-color: #FFFFFF;
    }
    .ingredient-card:hover { transform: translateY(-5px); }
    
    
    /* 绿色：新鲜 */
    .card-fresh { border-left: 8px solid #2A9D8F; }
    /* 黄色：临期*/
    .card-warning { border-left: 8px solid #F4A261; background-color: #FFFCF5; }
    /* 红色：当天过期*/
    .card-danger { border-left: 8px solid #E76F51; background-color: #FFF9F8; }
    /* 灰色：已过期*/
    .card-expired { border-left: 8px solid #9E9E9E; background-color: #F5F5F5; opacity: 0.7; }
    
    /* --- 8. 深度美化记忆输入框 (Text Area) --- */
    
    /* 定制输入框容器 */
    div[data-testid="stTextArea"] textarea {
        font-family: 'LXGW WenKai Lite', sans-serif !important;
        font-size: 1.1rem !important;
        color: #5C4D4D !important;
        background-color: #FCFAF7 !important; /* 极浅的米色背景 */
        border: 2px dashed #E8DCC8 !important; /* 虚线边框，更有手账感 */
        border-radius: 15px !important;
        padding: 15px !important;
        transition: all 0.3s ease;
    }


    /* 输入框聚焦时的状态 */
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #D47B55 !important; /* 聚焦时变成主色调 */
        background-color: #FFFFFF !important;
        box-shadow: 0 0 10px rgba(212, 123, 85, 0.1) !important;
    }

    /* 修改输入框上方的标签文字 (Label) */
    div[data-testid="stTextArea"] label p {
        font-size: 1rem !important;
        color: #8D7B68 !important;
        font-weight: bold !important;
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
    <div class='remy-title-wrapper'>
        <span class='remy-giant-title'>🍳 REMY</span>
        <span class='remy-side-title'>你冰箱里的“料理鼠王”</span>
    </div>
""", unsafe_allow_html=True)
st.markdown("<p class='remy-sub-title'>“用心对待每一顿饭，就是认真对待生活。”</p>", unsafe_allow_html=True)


# --- 3. 状态管理 (Session State) ---
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.date.today()
if 'inventory' not in st.session_state:
    st.session_state.inventory = {}
if 'recipes' not in st.session_state:
    st.session_state.recipes = []
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = {}
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

# --- 4. 侧边栏：上传、备忘录、时光机测试 ---
with st.sidebar:
    
    st.markdown("<h3 style='margin-bottom: 1rem; color:#8D7B68;'>Remy视察冰箱中👀</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("放了什么进冰箱呢？", type=["jpg", "jpeg", "png"], key=f"uploader_{st.session_state.uploader_key}")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("""<style>[data-testid="stImage"] img { border-radius: 16px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }</style>""", unsafe_allow_html=True)
        st.image(image, caption='准备入库的食材', use_container_width=True)
        
        st.write("") 
        if st.button("✨ 确认入库", use_container_width=True):
            with st.spinner('REMY 正抓紧清点你的食材...'):
                status_box = st.empty()
                try:
                    current_items = list(st.session_state.inventory.keys())
                    current_items_str = ", ".join(current_items) if current_items else "目前冰箱是空的"

                    prompt = f"""
                    你是一位温馨、懂生活的家庭大厨。请观察这张新买食材的图片。
                    已知冰箱里【已经有】以下食材：{current_items_str}。

                    核心指令：你必须严格提供至少 4 道完全不同的菜谱！少于 4 道视为严重错误！需要是一般中国家庭的家常菜，或者简单的西餐。每道菜必须附带一个能直接搜索该菜品的链接！

                    请结合【图片中的新食材】和【已有的食材】，严格按以下 JSON 格式返回结果（不要任何 Markdown 标记）：
                    {{
                      "new_items": [
                        {{"name": "食材名（仅输出食材名本身！！！如果不能肯定某种食材，则仅仅输出一种可能性，不要输出A/B的形式）", "quantity": 数量(纯数字), "unit": "单位(如:个/把/盒)", "expiry_days": 预估能放几天(纯整数数字)}}
                      ],
                      "recipes": [
                        {{
                          "title": "菜名", "reason": "为什么推荐它", "ingredients": ["所需食材（需要多少颗菜/多少酱油/多少肉等）"], "steps": ["步骤1", "步骤2"（每一步前面加上序号，写清楚每一步烧多久、加多少分量的调味品等,"link": "https://www.xiachufang.com/search/?keyword=菜名"]
                        }}
                      ],
                      "shopping": {{
                        "urgent": ["缺货常备品1（仅包含平日需要储存在冰箱里的常备品，如鸡蛋、饮品、葱等等，这些不需要说明选购原因）"],
                        "deals": ["生鲜食材的名称"（生成5-10个不等，种类需要包括：这几天需要用来做饭的食材、我喜欢的食物、正在打折的酸奶/冷链速食/甜品、降价生鲜、应季水果、网红食品、速食快手菜等）(在每一个产品后写上选购原因，8个汉字以内)]
                      }}
                    }}
                    """
                    
                    response = model.generate_content([prompt, image], stream=True)
                    
                    full_text = ""

                    for chunk in response:
                        full_text += chunk.text
                        matches = re.findall(r'"name"\s*:\s*"([^"]+)"', full_text)
                        if matches:
                            seen = set()
                            unique_items = [x for x in matches if not (x in seen or seen.add(x))]
                            items_str = "、".join(unique_items)
                            
                            status_box.markdown(f"<p style='color:#A68A7E; font-size: 0.95rem; font-style: italic; margin-top: 10px;'>👀 REMY 刚刚看到了：<span style='color:#D47B55; font-weight:bold;'>{items_str}</span> ...</p>", unsafe_allow_html=True)
                    
                    raw_text = full_text.strip().strip('```json').strip('```').strip()
                    data = json.loads(raw_text)
                    
                    status_box.empty()
                    
                    for item in data.get("new_items", []):
                        name = item["name"]
                        qty = item["quantity"]
                        exp_date = st.session_state.current_date + datetime.timedelta(days=int(item["expiry_days"]))
                        
                        if name in st.session_state.inventory:
                            st.session_state.inventory[name]["quantity"] += qty
                            st.session_state.inventory[name]["expiry_date"] = exp_date
                        else:
                            st.session_state.inventory[name] = {
                                "quantity": qty,
                                "unit": item.get("unit", "份"),
                                "expiry_date": exp_date,
                            }
                    
                    st.session_state.recipes = data.get("recipes", [])
                    st.session_state.shopping_list = data.get("shopping", {})
                    st.success("入库成功！")
                    st.session_state.uploader_key += 1 # 换一把新钥匙
                    st.rerun() # 立刻刷新页面
                    
                except Exception as e:
                    st.error(f"抱歉，REMY 走神了，再来一次！")
                    
    st.markdown("<br><hr style='border: 1px dashed #E8DCC8;'><br>", unsafe_allow_html=True)
    st.markdown("### 📝 主厨备忘录")
    current_mem = read_memory()
    new_mem = st.text_area("告诉 REMY 你的忌口或偏好：", value=current_mem, height=120)

    if st.button("更新记忆", use_container_width=True):
        save_memory(new_mem)
        st.toast("REMY 已经拿小本本记下来了！", icon="📖")
        if st.session_state.inventory:
            with st.spinner("正在根据新偏好调整食谱..."):
                refresh_suggestions()
        st.rerun()

    st.markdown("<br><hr style='border: 1px dashed #E8DCC8;'><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#8D7B68;'>⏳ 模拟时光机</h3>", unsafe_allow_html=True)
    st.caption("测试专用：点击模拟时间流逝，观察保质期变化")
    if st.button("⏩ 前进 1 天", use_container_width=True):
        st.session_state.current_date += datetime.timedelta(days=1)
        st.rerun()



# --- 5. 主界面：三大平行功能区 ---
tab1, tab2, tab3 = st.tabs(["📦 动态库存", "🍽️ 食谱助手", "🛒 一键采购"])

with tab1:
    st.markdown(f"<h4 style='color: #8D7B68 !important; margin-bottom: 1.5rem; font-size: 1.1rem; font-weight: normal;'>📅 冰箱日历：今天是 {st.session_state.current_date.strftime('%Y-%m-%d')}</h4>", unsafe_allow_html=True)
    
    if not st.session_state.inventory:
        st.info("冰箱现在空空的，快去进点货吧！")
    else:
        cols = st.columns(3)
        col_idx = 0
        
        # 对库存进行“危机程度”排序
        def sort_by_urgency(item):
            name, info = item
            rem_days = (info["expiry_date"] - st.session_state.current_date).days
            if rem_days < 0:
                # 如果已经过期了，放在列表最后面
                return (1, rem_days)  
            else:
                # 如果还没过期，按照剩余天数从小到大排（越临近过期，越排在前面）
                return (0, rem_days)  

        # 使用写好的逻辑，把原本乱序的字典变成排好序的列表
        sorted_inventory = sorted(st.session_state.inventory.items(), key=sort_by_urgency)
        
        # 遍历排好序的库存
        for name, info in sorted_inventory:
            remaining_days = (info["expiry_date"] - st.session_state.current_date).days
            
            # 🌟 四色状态 & 动态按钮文案判定
            if remaining_days < 0:
                card_class = "ingredient-card card-expired"
                status_emoji = "🪦"
                days_text = "已过期"
                text_color = "#9E9E9E" 
                button_text = f"🗑️ 快扔掉吧"
            elif remaining_days == 0:
                card_class = "ingredient-card card-danger"
                status_emoji = "🚨"
                days_text = "今日到期"
                text_color = "#E76F51" 
                button_text = f"🍴 吃掉一份 {name}"
            elif remaining_days <= 2: 
                card_class = "ingredient-card card-warning"
                status_emoji = "⚠️"
                days_text = f"剩 {remaining_days} 天"
                text_color = "#F4A261" 
                button_text = f"🍴 吃掉一份 {name}"
            else:
                card_class = "ingredient-card card-fresh"
                status_emoji = "🌿"
                days_text = f"剩 {remaining_days} 天"
                text_color = "#2A9D8F" 
                button_text = f"🍴 吃掉一份 {name}"
            
            with cols[col_idx % 3]:
                st.markdown(f"""
                <div class="{card_class}">
                    <h4 style="margin:0; color:{'#9E9E9E' if remaining_days < 0 else '#4A3B32'}; font-size:1.3rem;">{status_emoji} {name}</h4>
                    <p style="margin:12px 0 8px 0; color:#8D7B68; font-size: 0.95rem;">数量：{info['quantity']} {info['unit']}</p>
                    <p style="margin:0; color:{text_color}; font-weight:bold; font-size: 0.95rem;">
                        ⏳ {days_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # 🌟 按钮执行动作区分
                if st.button(button_text, key=f"action_{name}", use_container_width=True):
                    if remaining_days < 0:
                        # 对于已经过期的，点击“扔掉吧”直接把该食材从冰箱清空
                        del st.session_state.inventory[name]
                    else:
                        # 对于没过期的，正常消耗一份
                        st.session_state.inventory[name]["quantity"] -= 1
                        if st.session_state.inventory[name]["quantity"] <= 0:
                            del st.session_state.inventory[name]

                    with st.spinner("REMY 正在根据新库存重新规划..."):
                        refresh_suggestions()

                    st.rerun() # 刷新页面
            
            col_idx += 1

with tab2:
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>👨‍🍳 根据当前库存，Remy为您搭配</h3>", unsafe_allow_html=True)
    if not st.session_state.recipes:
        st.write("冰箱里居然空空如也！快去买点吃的喝的，REMY 再为您定制菜单哦。")
    else:
        col1, col2 = st.columns(2)
        for i, recipe in enumerate(st.session_state.recipes):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.expander(f"✨ {recipe.get('title', '美味佳肴')}"):
                    st.caption(f"💡 {recipe.get('reason', '为您特别推荐')}")
                    st.markdown("<hr style='border: 0.5px solid #F0EAE1; margin: 10px 0;'>", unsafe_allow_html=True)
                    st.markdown("**🛒 准备食材：**")
                    st.markdown("、".join(recipe.get('ingredients', [])))
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**🍳 烹饪方法：**")
                    for step in recipe.get('steps', []):
                        st.markdown(f"<p style='margin-bottom: 5px;'>{step}</p>", unsafe_allow_html=True)

                    if recipe.get('link'):
                        st.markdown(f"<br><a href='{recipe.get('link')}' target='_blank' style='color: #D47B55; font-weight: bold; text-decoration: none;'>🔗 点击查看详细图文食谱 ↗</a>", unsafe_allow_html=True)

with tab3:
    st.markdown("<h3 style='margin-bottom: 1.5rem;'>🛒 REMY 的优选清单</h3>", unsafe_allow_html=True)
    if not st.session_state.shopping_list:
         st.write("暂时没有推荐的采购计划呢")
    else:
        shopping = st.session_state.shopping_list
        
        if shopping.get("urgent"):
            st.markdown("<h4 style='color: #E76F51 !important;'>🚨 紧急补货</h4>", unsafe_allow_html=True)
            for item in shopping["urgent"]:
                st.checkbox(f"**{item}**", key=f"urg_{item}")
        else:
            st.success("常备物资储备充足哦！")
            
        st.markdown("<br><hr style='border: 1px dashed #E8DCC8;'><br>", unsafe_allow_html=True)

        if shopping.get("deals"):
            st.markdown("<h4 style='color: #2A9D8F !important;'>🏷️ Remy推荐</h4>", unsafe_allow_html=True)
            st.caption("😊 REMY 还为你搜罗了其他好吃的：")
            for item in shopping["deals"]:
                st.checkbox(f"🛒 {item}", key=f"deal_{item}")