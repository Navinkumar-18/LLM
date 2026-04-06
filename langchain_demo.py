import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

st.title("🤖 Ollama Demo Bot")

input_text = st.text_input("Enter your queries:")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI Assistant. Your name is Doraemon."),
        ("human", "{your query}")
    ]
)

llm = ChatOllama(
    model="llama3:latest",
    temperature=0.7
)

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

if input_text:
    st.write(chain.invoke({"your query": input_text}))
