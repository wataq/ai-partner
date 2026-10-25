# AI 智能伴侣

基于 Streamlit + DeepSeek API 的角色扮演对话应用，支持多会话管理、自定义人设和流式输出。

## 功能

- 流式输出，回复逐字显示
- 多会话管理：新建 / 切换 / 删除，重启后不丢失
- 自定义昵称与性格，实时写入系统提示词
- 上下文窗口限制在最近 20 条，避免长时间对话超出模型上限
- 调用失败自动回滚，不会留下重复的用户消息

## 技术栈

- Python 3.10+
- Streamlit：页面、会话状态、流式渲染
- OpenAI SDK：通过兼容端点调用 DeepSeek
- JSON 文件持久化会话

## 本地运行

安装依赖：

```bash
pip install -r requirements.txt
```

配置 API Key，二选一。

环境变量：

```bash
set DEEPSEEK_API_KEY=你的key
```

或者新建 `.streamlit/secrets.toml`：

```toml
DEEPSEEK_API_KEY = "你的key"
```

启动：

```bash
streamlit run ai_partner_7.py
```

## 目录结构

```
.
├── ai_partner_7.py      主程序
├── assets/sample.png    侧边栏 logo
├── sessions/            会话存档（不上传）
├── requirements.txt
└── README.md
```

## 说明

`sessions/` 存放个人聊天记录，`.streamlit/secrets.toml` 存放密钥，两者都已加入 `.gitignore`。
