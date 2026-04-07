from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

response = llm.invoke("Explain binary search in simple words")

print(response)
