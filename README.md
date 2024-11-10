# WebUILite

WebUILite 是一个基于 Gradio 的轻量级 Web 用户界面，用于与开源大语言模型(兼容OpenAI接口)进行交互。该项目使用 LangChain 和 OpenAI API，支持多种文件格式的上传和聊天功能。

## 特性

- 使用 Gradio 创建用户友好的界面
- 支持多种文件格式的上传（如 PDF、Word、Excel 等）# 待实现
- 通过下拉框选择可用的模型
- 配置管理功能，支持动态加载和保存配置
- 实时聊天功能，支持历史记录

## 安装

1. 克隆该项目：

   ```bash
   git clone https://github.com/yourusername/WebUILite.git
   cd WebUILite
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用

1. 确保您已设置 OpenAI API 密钥，并在 `cfg/app_gradio.json` 中配置相关参数。

2. 运行应用程序：

   ```bash
   python app_main.py
   ```

3. 打开浏览器，访问 `http://localhost:7860` 以使用 Web 界面。

## 配置

您可以通过 Web 界面，或编辑 `cfg/app_gradio.json` 文件来修改以下配置项：

- `BASE_URL`: API 的基础 URL
- `API_KEY`: OpenAI API 密钥，Ollama固定为ollama
- `TEMPERATURE`: 控制输出随机性的温度参数
- `MODEL`: 默认使用的模型

## 贡献

欢迎提交问题和拉取请求！请确保在提交之前检查现有问题和功能请求。

## 许可证

该项目使用 MIT 许可证。有关详细信息，请参阅 LICENSE 文件。

## TODO

1. 支持黄区/绿区，支持设置无代理
2. 记录/打开历史会话
3. 支持RAG
4. 支持工具
5. 支持多模态
8. 历史限制条数，使用langgraph
- 已切换，但是当总结消息时，界面对话不自然，需要进一步修改
- MAX_MESSAGES = 10  # 最大消息数 # TODO: make this configurable
9. 解决API_KEY加解密问题
10. 支持多个模型Provider