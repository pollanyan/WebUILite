from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
import base64
from openai import OpenAI

class ChatPredictor:
    """
    ChatPredictor 类用于处理聊天预测逻辑。
    它封装了与语言模型的交互，使用 langchain 库来处理聊天请求。
    """

    def __init__(self, base_url, api_key, temperature):
        """
        初始化 ChatPredictor 实例。

        参数:
        base_url (str): API 的基础 URL
        api_key (str): API 密钥
        temperature (float): 控制输出随机性的温度参数
        """
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature

    def predict(self, message, history, model):
        """
        根据给定的消息、历史记录和模型生成预测响应。

        参数:
        message (dict): 包含用户输入的消息字典
        history (list): 对话历史记录列表
        model (str): 要使用的模型名称

        返回:
        str: 模型生成的响应内容
        """
        print("执行模型: ", model)
        # 创建 ChatOpenAI 实例
        chat = ChatOpenAI(
            model=model,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.temperature,
            streaming=True,
        )

        # 将历史记录转换为 langchain 格式
        history_langchain_format = []

        for human, ai in history:
            history_langchain_format.append(HumanMessage(content=human))
            history_langchain_format.append(AIMessage(content=ai))

        # 添加当前用户消息
        history_langchain_format.append(HumanMessage(content=message["text"]))

        # 调用模型生成响应
        response = chat.invoke(history_langchain_format)

        # 返回模型生成的内容
        return response.content

    def get_models(self):
        """
        获取可用的模型列表
        :return: 模型ID列表
        """
        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        models = [model.id for model in client.models.list()]
        return models
