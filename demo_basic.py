from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

response = llm.invoke("Explain how to solve leetcode problems effectively.")

print(response)
