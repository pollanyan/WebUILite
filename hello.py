import os
from langchain_community.chat_models import ChatOllama
from langchain.schema import AIMessage, HumanMessage
import openai
import gradio as gr

# os.environ["OPENAI_API_KEY"] = "sk-..."  # Replace with your key

llm = ChatOllama(temperature=1.0, model='qwen2.5:latest')

def predict(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm.invoke(history_langchain_format)  
    return gpt_response.content

gr.ChatInterface(predict).launch()