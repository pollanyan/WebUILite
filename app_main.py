import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain.schema import AIMessage, HumanMessage
from openai import OpenAI
import gradio as gr
from pydantic import SecretStr
from app_config import ConfigManager
from app_llm import ChatPredictor
import base64

# 使用ConfigManager类来管理配置
config_manager = ConfigManager()

# 从配置管理器读取配置项
# BASE_URL = config_manager.get("BASE_URL", "http://localhost:11434/v1/")
# API_KEY = config_manager.get("API_KEY", SecretStr("ollama").get_secret_value())
# TEMPERATURE = config_manager.get("TEMPERATURE", 1.0)
# DEFAULT_MODEL = config_manager.get("DEFAULT_MODEL", "qwen2.5:latest")

# 创建一个字典来存储应用的全局状态
# def refresh_app_session():
#     app_session = {
#         "BASE_URL": config_manager.get("BASE_URL", "http://localhost:11434/v1/"),
#         "API_KEY": config_manager.get("API_KEY", SecretStr("ollama").get_secret_value()),
#         "TEMPERATURE": config_manager.get("TEMPERATURE", 1.0),
#         "DEFAULT_MODEL": config_manager.get("DEFAULT_MODEL", "qwen2.5:latest")
#     }
#     return app_session

# app_session = refresh_app_session()
app_session = config_manager.load_config()

# def get_models():
#     """
#     获取可用的模型列表
#     :return: 模型ID列表
#     """
#     client = OpenAI(base_url=app_session["BASE_URL"], api_key=app_session["API_KEY"])
#     models = [model.id for model in client.models.list()]
#     return models

# 创建 ChatPredictor 实例
chat_predictor = ChatPredictor(
    app_session["BASE_URL"], app_session["API_KEY"], app_session["TEMPERATURE"]
)

# 获取可用的模型列表
# models = chat_predictor.get_models()


# 定义一个包装函数来调用 ChatPredictor 的 predict 方法
def predict_wrapper(message, history):
    """
    包装 ChatPredictor 的 predict 方法，用于 Gradio 接口
    :param message: 用户输入的消息
    :param history: 聊天历史
    :param model: 选择的模型
    :return: ChatPredictor 的预测结果
    """
    return chat_predictor.predict(message, history, app_session["DEFAULT_MODEL"])


# 创建 Gradio 界面
with gr.Blocks(fill_height=True) as demo:
    chatbot = gr.Chatbot(layout="panel", label="聊天")

    with gr.Group():
        models = chat_predictor.get_models()
        with gr.Row():
            # 创建模型选择下拉框
            model_selector = gr.Dropdown(
                choices=models,
                value=app_session["DEFAULT_MODEL"],
                show_label=False,
                container=False,
            )

            # 定义模型选择变化时的处理函数
            def change_model(selected_model):
                # global DEFAULT_MODEL
                app_session["DEFAULT_MODEL"] = selected_model

            model_selector.change(fn=change_model, inputs=[model_selector])

            # 配置按钮
            config_button = gr.Button("配置")

        # 配置弹窗
        with gr.Column(visible=False) as config_popup:
            config = config_manager.load_config()
            base_url_input = gr.Textbox(label="BASE_URL", value=config["BASE_URL"])
            api_key_input = gr.Textbox(
                label="API_KEY", value=config["API_KEY"], type="password"
            )
            temperature_input = gr.Slider(
                label="TEMPERATURE",
                minimum=0,
                maximum=2,
                step=0.1,
                value=config["TEMPERATURE"],
            )
            default_model_input = gr.Dropdown(
                choices=models, value=config["DEFAULT_MODEL"], label="DEFAULT_MODEL"
            )
            # default_model_input = model_selector
            output_message = gr.Textbox(label="输出", interactive=False)
            with gr.Row():
                save_button = gr.Button("保存")
                close_button = gr.Button("返回")

                # 保存配置
                def save_config(base_url, api_key, temperature, default_model):
                    config_manager.set("BASE_URL", base_url)
                    config_manager.set("API_KEY", api_key)
                    config_manager.set("TEMPERATURE", temperature)
                    config_manager.set("DEFAULT_MODEL", default_model)
                    config_manager.save_config()

                    # 重新获取配置
                    global app_session
                    app_session = config_manager.load_config()
                    # model_selector.value = default_model
                    print("当前模型", model_selector.value)

                    return "成功, 配置已保存到app_gradio.json", default_model

                save_button.click(
                    fn=save_config,
                    inputs=[
                        base_url_input,
                        api_key_input,
                        temperature_input,
                        default_model_input,
                    ],
                    outputs=[output_message, model_selector],
                )

                # 关闭配置弹窗
                close_button.click(
                    fn=lambda: gr.update(visible=False), outputs=[config_popup]
                )

            # 打开配置弹窗
            config_button.click(
                fn=lambda: gr.update(visible=True), outputs=[config_popup]
            )

        # 创建多模态文本框，支持上传多种类型的文件
        textbox = gr.MultimodalTextbox(
            file_count="multiple",
            file_types=["image", "text", ".docx", ".pptx", ".xlsx", ".pdf"],
            info="支持上传多文件, 文件格式: PDF/Word文档(DOC/DOCX)/Excel表格(XLSX)/PPT(PPT/PPTX)/TXT/CSV/MD",
        )

    # 创建聊天界面
    chat_interface = gr.ChatInterface(
        predict_wrapper,
        chatbot=chatbot,
        textbox=textbox,
        # additional_inputs=[model_selector],
        concurrency_limit=5,
        title="",
        submit_btn="发送",
        stop_btn="停止",
        retry_btn=None,
        undo_btn=None,
        clear_btn=None,
        multimodal=True,
        fill_width=True,
    )


# 启动 Gradio 应用
if __name__ == "__main__":
    demo.launch()
