import os
import json
from pydantic import SecretStr
import base64

class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_file="cfg/app_gradio.json"):
        """
        初始化配置管理器
        :param config_file: 配置文件路径，默认为'cfg/app_gradio.json'
        """
        self.config_file = config_file
        self.initialize_config()

    def load_config(self):
        """
        从配置文件加载配置项
        :return: 配置项字典，如果文件不存在则返回空字典
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, config=None):
        """保存配置项到配置文件"""
        with open(self.config_file, "w") as f:
            if config is None:
                json.dump(self.config, f, indent=4)
            else:
                json.dump(config, f, indent=4)

    def initialize_config(self):
        """
        初始化配置文件
        如果配置文件不存在，创建默认配置；否则加载现有配置
        """
        if not os.path.exists(self.config_file):
            initial_config = {
                "BASE_URL": "http://localhost:11434/v1/",
                "API_KEY": SecretStr("ollama").get_secret_value(),
                "TEMPERATURE": 1.0,
                "DEFAULT_MODEL": "qwen2.5:latest"
            }
            self.config = initial_config
            self.save_config()
        else:
            self.config = self.load_config()

    def get(self, key, default=None):
        """
        获取配置项
        :param key: 配置项的键
        :param default: 如果键不存在时返回的默认值
        :return: 配置项的值
        """
        return self.config.get(key, default)

    def set(self, key, value):
        """
        设置配置项并保存
        :param key: 配置项的键
        :param value: 配置项的值
        """
        self.config[key] = value
        self.save_config()
