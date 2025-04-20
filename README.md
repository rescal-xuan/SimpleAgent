# SimpleAgent

SimpleAgent 是一个简单的智能代理项目，能够使用工具、记忆对话和检索增强生成。该项目结合了多种技术，包括语言模型、工具集成和检索增强生成（RAG）。

## 项目结构

- `SimpleAgnet.py`: 主代理类，负责初始化和管理工具、处理用户请求。
- `llm/`: 包含语言模型的实现。
- `memory/`: 负责对话历史的存储和管理。
- `rag/`: 实现检索增强生成功能。
- `tool/`: 包含各种工具的实现，如计算器和天气查询。
- `callback/`: 处理各种回调事件。
- `streamlit_app.py`: 使用 Streamlit 创建的前端应用，用于与代理进行交互。

## 安装

克隆仓库到本地：

   ```bash
   git clone https://github.com/rescal-xuan/SimpleAgent.git
   ```

## 使用方法

### 运行代理
进入目标目录：
```bash
cd  SimpleAgnet
```
可以直接运行 `SimpleAgnet.py` 文件来启动代理：

```bash
python SimpleAgnet.py
```
### 使用 Streamlit 前端

运行 `streamlit_app.py` 来启动前端应用：

```bash
streamlit run streamlit_app.py
```

## 贡献

欢迎贡献代码！请提交 Pull Request 或报告问题。

## 许可证

该项目使用 MIT 许可证。
```
