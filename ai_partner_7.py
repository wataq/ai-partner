import os
import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from openai import OpenAI

# 页面设置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="😻",
    # 布局
    layout="wide",
    # 侧边栏状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 项目根目录（跟着代码走，换电脑也不用改）
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

# 只把最近 20 条消息发给模型，防止聊久了超出上下文上限
MAX_HISTORY = 20


# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息函数
def save_session():
    if not st.session_state.current_session:
        return
    session_data = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages,
    }
    path = SESSIONS_DIR / f"{st.session_state.current_session}.json"
    try:
        path.write_text(
            json.dumps(session_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        st.error(f"保存会话失败：{e}")


# 加载历史会话函数
def load_sessions():
    session_list = [p.stem for p in SESSIONS_DIR.glob("*.json")]
    session_list.sort(reverse=True)
    return session_list


# 加载指定会话信息函数
def load_session(session_name):
    try:
        path = SESSIONS_DIR / f"{session_name}.json"
        if not path.exists():
            return
        session_data = json.loads(path.read_text(encoding="utf-8"))
        st.session_state.messages = session_data["messages"]
        st.session_state.nick_name = session_data["nick_name"]
        st.session_state.nature = session_data["nature"]
        st.session_state.current_session = session_name
    except Exception as e:
        st.error(f"加载会话失败：{e}")


# 删除会话信息函数
def delete_session(session_name):
    try:
        path = SESSIONS_DIR / f"{session_name}.json"
        if path.exists():
            path.unlink()
        # 如果删除的是当前会话，则需要更新消息列表
        if session_name == st.session_state.current_session:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
    except Exception as e:
        st.error(f"删除会话失败：{e}")


# 读取 API Key：优先环境变量，其次 st.secrets（部署到云端时用）
def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key
    try:
        return st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        return None


# 大标题
st.title("AI智能伴侣")

# logo（图片不存在时就不显示，不会让页面崩掉）
logo_path = BASE_DIR / "assets" / "sample.png"
if logo_path.exists():
    st.logo(str(logo_path))

# 系统提示词
system_prompt = """
        你叫%s,现在你是用户的伴侣,请完全带入伴侣角色。:
        规则：
            1. 每次只回复一条消息
            2. 禁止任何场景或描述性文字
            3.匹配用户的语言
            4.简短回复，像微信聊天一样
            5.有需要可以用emoji表情 
            6.用符合伴侣性格的方式对话
            7.回复内容必须符合伴侣的性格特征
        性格特征：
            - %s
        你必须严格按照以上规则和我对话
"""


# 初始化聊天信息(所有消息，ai和用户)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小美"

# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "温柔体贴"

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()


# 展示聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])


# 大模型客户端
api_key = get_api_key()
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com") if api_key else None


# 左侧侧边栏
with st.sidebar:
    st.subheader("AI控制面板")

    # 新建对话
    if st.button("新建会话", width="stretch", icon="🆕"):
        # 有内容才存档；空会话不落盘，免得历史列表被空记录塞满
        if st.session_state.messages:
            save_session()
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        st.rerun()

    # 会话历史
    st.text("会话历史")
    for session in load_sessions():
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                session,
                width="stretch",
                icon="📄",
                key=f"load_{session}",
                type="primary" if session == st.session_state.current_session else "secondary",
            ):
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌️", key=f"del_{session}"):
                delete_session(session)
                st.rerun()

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    st.session_state.nick_name = nick_name.strip() or st.session_state.nick_name

    nature = st.text_area("性格", placeholder="请输入性格特征", value=st.session_state.nature)
    st.session_state.nature = nature.strip() or st.session_state.nature


# 消息输入框
prompt = st.chat_input("请输入您的消息：")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        if client is None:
            raise RuntimeError("未找到 DEEPSEEK_API_KEY，请在环境变量或 .streamlit/secrets.toml 中配置")

        # 调用 ai 大模型
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt % (st.session_state.nick_name, st.session_state.nature),
                },
                *st.session_state.messages[-MAX_HISTORY:],
            ],
            stream=True,
        )

        # 流式输出：容器建一次，之后只更新内容
        full_response = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()

        for chunk in response:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_session()

    except Exception as e:
        # 调用失败就把刚才那条用户消息撤回，避免重试时重复
        st.session_state.messages.pop()
        st.error(f"调用失败，请检查网络、余额或 API Key：{e}")
