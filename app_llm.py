from typing import Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    RemoveMessage,
    HumanMessage,
    AIMessageChunk,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from pydantic import SecretStr
from langchain_core.runnables.config import RunnableConfig
from openai import OpenAI

# from langchain_community.llms.ollama import Ollama


class LLMProvider:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_models(self):
        """
        获取可用的模型列表
        :return: 模型ID列表
        """

        client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        models = [model.id for model in client.models.list()]

        return models


class ChatLLM:
    def __init__(self, model, base_url, api_key, temperature):

        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

        self.llm = ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.temperature,
            streaming=True,
        )

    def get_llm(self):
        return self.llm

    def set_llm(self, model, base_url, api_key, temperature):
        self.__init__(model, base_url, api_key, temperature) 

    def set_model(self, model):
        self.model = model
        self.llm = ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=self.temperature,
            streaming=True,
        )

    def chat(self, messages):
        return self.llm.invoke(messages)


class ChatWorkflow:
    MAX_MESSAGES = 10

    def __init__(self, chat_llm):

        self.chat_llm = chat_llm

        # self.model = Ollama(
        #     model=model
        # )

        self.workflow = self.create_workflow()

    def create_workflow(self):
        # We will add a `summary` attribute (in addition to `messages` key)
        class State(MessagesState):
            summary: str

        self.memory = MemorySaver()

        workflow = StateGraph(State)

        # Define the conversation node and the summarize node
        workflow.add_node("conversation", self.call_model)
        workflow.add_node("summarize_conversation", self.summarize_conversation)

        # Set the entrypoint as conversation
        workflow.add_edge(START, "conversation")

        # Add conditional edges
        workflow.add_conditional_edges(
            "conversation",
            self.should_continue,
        )

        # Add edge from summarize_conversation to END
        workflow.add_edge("summarize_conversation", END)

        return workflow.compile(checkpointer=self.memory)

    def call_model(self, state: MessagesState):
        summary = state.get("summary", "")
        messages = (
            [SystemMessage(content=f"Summary of conversation earlier: {summary}")]
            + state["messages"]
            if summary
            else state["messages"]
        )
        response = self.chat_llm.chat(messages)
        return {"messages": [response]}

    def should_continue(self, state: MessagesState):
        messages = state["messages"]
        return "summarize_conversation" if len(messages) > self.MAX_MESSAGES else END

    def summarize_conversation(self, state: MessagesState):
        summary = state.get("summary", "")
        summary_message = (
            (
                f"This is summary of the conversation to date: {summary}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )
            if summary
            else "Create a summary of the conversation above:"
        )

        messages = state["messages"] + [HumanMessage(content=summary_message)]
        response = self.chat_llm.chat(messages)

        # Delete messages that we no longer want to show up
        delete_messages = [
            RemoveMessage(id=str(m.id)) for m in state["messages"][: -self.MAX_MESSAGES]
        ]
        return {"summary": response.content, "messages": delete_messages}

    def pretty_message(self, message):
        # for k, v in update.items():
        #     for m in v["messages"]:
        #         m.pretty_print()
        #         yield m.pretty_repr()
        #     if "summary" in v:
        #         print(v["summary"])
        #         yield v["summary"]

        if isinstance(message, AIMessageChunk):
            # message.pretty_print()
            # print(f"{message.content}")
            return f"{message.content}"
        else:
            return ""

    async def run(self, input_message, history):
        config = RunnableConfig({"configurable": {"thread_id": "4"}})
        input_text = input_message["text"]
        input_message_obj = HumanMessage(content=input_text)
        # input_message_obj.pretty_print()
        response = "**" + self.chat_llm.model + "**\n"  # 显示模型名称(粗体)
        # print(response)
        async for (
            msg,
            metadata,
        ) in self.workflow.astream(
            {"messages": [input_message_obj]}, config, stream_mode="messages"
        ):
            # print("event: ",event)
            # for response in self.print_update(event):
            #     yield response
            response += self.pretty_message(msg)

            yield response


# Example usage
# if __name__ == "__main__":
#     chatbot = ChatbotWorkflow()
#     messages = [
#         "hi! I'm bob",
#         "what's my name?",
#         "i like the celtics!",
#         "i like how much they win"
#     ]
#     for msg in messages:
#         chatbot.run(msg)
