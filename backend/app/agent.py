import os
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langfuse.callback import CallbackHandler
from app.tools.carrefour_search import CarrefourSearchTool # The personalized tools

def get_carrefour_agent():
    # 1. Langfuse Config
    langfuse_handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")
    )

    # 2. Gemini LLM via Vertex
    llm = ChatVertexAI(
        model_name="gemini-pro",
        max_output_tokens=1024,
        temperature=0.2,
        convert_system_message_to_human=True
    )

    # 3. Tools definiton
    tools = [CarrefourSearchTool()]

    # 4. Conversation in-memory
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )

    # 5. Create agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        callbacks=[langfuse_handler] # Injection du tracing Langfuse
    )

    return agent
