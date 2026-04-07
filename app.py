import streamlit as st
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
import re

# ==============================
# CONFIGURATION
# ==============================

OLLAMA_MODEL = "llama3"  
CONFIDENCE_THRESHOLD = 0.6
WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ==============================
# INITIAL KNOWLEDGE BASE
# ==============================

initial_documents = [
    "A vector database stores high-dimensional embeddings for similarity search.",
    "LangChain is a framework for building applications using large language models.",
    "Retrieval Augmented Generation retrieves relevant documents before generating answers.",
    "FAISS is a library developed by Facebook AI for efficient similarity search.",
    "Embeddings convert text into numerical vectors for semantic comparison."
]

# ==============================
# SESSION STATE INIT
# ==============================

if "documents" not in st.session_state:
    st.session_state.documents = initial_documents.copy()
    st.session_state.doc_ids = [f"doc_{i}" for i in range(len(initial_documents))]
    st.session_state.doc_weights = {doc_id: 1.0 for doc_id in st.session_state.doc_ids}
    
    # Build initial FAISS index
    doc_embeddings = embedding_model.encode(st.session_state.documents)
    dimension = doc_embeddings.shape[1]
    st.session_state.index = faiss.IndexFlatL2(dimension)
    st.session_state.index.add(np.array(doc_embeddings).astype("float32"))
    st.session_state.dimension = dimension
    st.session_state.new_docs_added = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

# ==============================
# RETRIEVAL FUNCTION
# ==============================

def retrieve(query, top_k=3):
    """Retrieve top-k documents from FAISS index with weighted ranking"""
    query_embedding = embedding_model.encode([query])
    D, I = st.session_state.index.search(np.array(query_embedding).astype("float32"), top_k)

    results = []
    for idx in I[0]:
        if idx < len(st.session_state.doc_ids):
            doc_id = st.session_state.doc_ids[idx]
            weight = st.session_state.doc_weights.get(doc_id, 1.0)
            results.append((doc_id, st.session_state.documents[idx], weight))

    # Sort by weight (Self-Evolving ranking)
    results.sort(key=lambda x: x[2], reverse=True)
    return results

# ==============================
# GENERATE ANSWER USING OLLAMA
# ==============================

def generate_answer(query, retrieved_docs):
    """Generate answer using Ollama with strict context-based rules"""
    context_text = "\n\n".join(
        [f"{doc_id}: {content}" for doc_id, content, _ in retrieved_docs]
    )

    prompt = f"""
You are an AI assistant inside an Autonomous Self-Improving RAG system.

STRICT RULES:
1. Answer ONLY using retrieved context.
2. Do NOT use outside knowledge.
3. If information is missing, say:
   "The retrieved documents do not contain sufficient information."

User Question:
{query}

Retrieved Context:
{context_text}

Final Answer:
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        st.error("❌ **Ollama is not running!**")
        st.info("Please start Ollama with: `ollama serve`")
        return "Error: Ollama service is not running. Please start it first."
    except Exception as e:
        st.error(f"Error generating answer: {str(e)}")
        return "Error occurred while generating answer."

# ==============================
# CONFIDENCE EVALUATION
# ==============================

def evaluate_confidence(query, answer, retrieved_docs):
    """Automatically evaluate answer confidence using Ollama"""
    # Skip confidence check if answer is an error message
    if "Error" in answer:
        return 0.0
    
    context_text = "\n\n".join(
        [f"{content}" for _, content, _ in retrieved_docs]
    )

    confidence_prompt = f"""
Question: {query}
Answer: {answer}
Retrieved Context: {context_text}

Is the answer fully supported by the retrieved context?
Respond with only a confidence score between 0 and 1.
Output format: just the number (e.g., 0.8)
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": confidence_prompt,
                "stream": False
            },
            timeout=30
        )
        
        confidence_text = response.json()["response"].strip()
        # Extract first number found in response
        match = re.search(r'0?\.\d+|[01]\.?\d*', confidence_text)
        if match:
            confidence = float(match.group())
            return min(max(confidence, 0.0), 1.0)  # Clamp between 0 and 1
        return 0.5  # Default if parsing fails
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Could not evaluate confidence - Ollama not responding")
        return 0.0
    except Exception as e:
        st.warning(f"⚠️ Confidence evaluation error: {str(e)}")
        return 0.5  # Default on error

# ==============================
# KNOWLEDGE EXPANSION
# ==============================

def chunk_text(text, max_length=200):
    """Split text into smaller chunks"""
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def fetch_wikipedia(query):
    """Fetch Wikipedia summary for given query"""
    try:
        # Clean query for Wikipedia API
        search_term = query.replace(" ", "_")
        url = f"{WIKIPEDIA_API}{search_term}"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            summary = data.get("extract", "")
            return summary
        return None
    except Exception as e:
        st.warning(f"Wikipedia fetch failed: {str(e)}")
        return None

def expand_knowledge(query):
    """Fetch from Wikipedia, chunk, embed, and add to FAISS index"""
    st.info("🔄 Low confidence detected. Expanding knowledge base...")
    
    # Fetch Wikipedia content
    wiki_content = fetch_wikipedia(query)
    
    if not wiki_content:
        st.warning("⚠️ Could not fetch additional knowledge from Wikipedia.")
        return []
    
    # Chunk the new content
    new_chunks = chunk_text(wiki_content)
    
    if not new_chunks:
        return []
    
    # Generate embeddings for new chunks
    new_embeddings = embedding_model.encode(new_chunks)
    
    # Add to FAISS index
    st.session_state.index.add(np.array(new_embeddings).astype("float32"))
    
    # Add to documents and doc_ids
    new_doc_ids = []
    for i, chunk in enumerate(new_chunks):
        doc_id = f"wiki_{len(st.session_state.documents)}_{i}"
        st.session_state.documents.append(chunk)
        st.session_state.doc_ids.append(doc_id)
        st.session_state.doc_weights[doc_id] = 1.0
        new_doc_ids.append(doc_id)
    
    st.success(f"✅ Added {len(new_chunks)} new knowledge chunks from Wikipedia!")
    
    return new_doc_ids

# ==============================
# OLLAMA HEALTH CHECK
# ==============================

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

# ==============================
# STREAMLIT UI
# ==============================

st.title("🧠 Autonomous Self-Improving RAG System")
st.caption("Automatically evaluates confidence and expands knowledge when needed")

# Ollama status check
if not check_ollama():
    st.error("⚠️ **Ollama is not running!**")
    st.info("""
    **To start Ollama:**
    1. Open a terminal/PowerShell
    2. Run: `ollama serve`
    3. Refresh this page
    """)
    st.stop()
else:
    st.success("✅ Ollama is connected")

query = st.text_input("Ask a question:")

if st.button("Generate Answer") and query:
    
    with st.spinner("🔍 Retrieving relevant documents..."):
        retrieved_docs = retrieve(query)
    
    with st.spinner("🤖 Generating answer..."):
        answer = generate_answer(query, retrieved_docs)
    
    # Automatic confidence evaluation
    with st.spinner("📊 Evaluating answer confidence..."):
        confidence = evaluate_confidence(query, answer, retrieved_docs)
    
    # Store initial state
    st.session_state.last_query = query
    st.session_state.last_docs = retrieved_docs
    st.session_state.last_answer = answer
    st.session_state.confidence = confidence
    st.session_state.new_docs_added = []
    st.session_state.knowledge_expanded = False
    
    # Autonomous knowledge expansion if low confidence
    if confidence < CONFIDENCE_THRESHOLD:
        st.session_state.knowledge_expanded = True
        new_doc_ids = expand_knowledge(query)
        st.session_state.new_docs_added = new_doc_ids
        
        # Regenerate answer with updated knowledge base
        if new_doc_ids:
            with st.spinner("🔄 Regenerating answer with expanded knowledge..."):
                updated_docs = retrieve(query)
                updated_answer = generate_answer(query, updated_docs)
                updated_confidence = evaluate_confidence(query, updated_answer, updated_docs)
            
            st.session_state.last_answer = updated_answer
            st.session_state.last_docs = updated_docs
            st.session_state.confidence = updated_confidence
    
    # Display results
    st.divider()
    
    # Confidence Score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confidence Score", f"{st.session_state.confidence:.2f}")
    with col2:
        status = "✅ High" if st.session_state.confidence >= CONFIDENCE_THRESHOLD else "⚠️ Low"
        st.metric("Status", status)
    with col3:
        expansion = "Yes" if st.session_state.knowledge_expanded else "No"
        st.metric("Knowledge Expanded", expansion)
    
    st.divider()
    
    # Answer
    st.subheader("📝 Answer")
    st.write(st.session_state.last_answer)
    
    st.divider()
    
    # Retrieved Documents
    st.subheader("📚 Retrieved Documents")
    for doc_id, content, weight in st.session_state.last_docs:
        is_new = doc_id in st.session_state.new_docs_added
        
        if is_new:
            st.markdown(f"**🆕 {doc_id} (weight: {round(weight,2)}) - NEWLY ADDED**")
            st.success(content)
        else:
            st.markdown(f"**{doc_id} (weight: {round(weight,2)})**")
            st.info(content)
        st.write("---")
    
    # Knowledge expansion details
    if st.session_state.knowledge_expanded and st.session_state.new_docs_added:
        st.divider()
        st.subheader("🌟 Newly Added Knowledge")
        st.caption(f"Added {len(st.session_state.new_docs_added)} chunks from Wikipedia")
        for doc_id in st.session_state.new_docs_added:
            idx = st.session_state.doc_ids.index(doc_id)
            st.markdown(f"**{doc_id}**")
            st.success(st.session_state.documents[idx])

# ==============================
# SYSTEM INFO
# ==============================

with st.sidebar:
    st.header("📊 System Info")
    st.metric("Total Documents", len(st.session_state.documents))
    st.metric("Original Documents", len(initial_documents))
    st.metric("Expanded Documents", len(st.session_state.documents) - len(initial_documents))
    
    st.divider()
    st.subheader("⚙️ Configuration")
    st.write(f"**Model:** {OLLAMA_MODEL}")
    st.write(f"**Confidence Threshold:** {CONFIDENCE_THRESHOLD}")
    st.write(f"**Embedding Model:** all-MiniLM-L6-v2")
    st.write(f"**Vector Dimension:** {st.session_state.dimension}")
    
    st.divider()
    st.subheader("🔄 How It Works")
    st.markdown("""
    1. **Query** → User asks question
    2. **Retrieve** → FAISS finds relevant docs
    3. **Generate** → LLM creates answer
    4. **Evaluate** → Auto confidence check
    5. **Expand** → If low confidence: fetch Wikipedia
    6. **Re-generate** → Answer with new knowledge
    """)
    
    if st.button("🔄 Reset Knowledge Base"):
        st.session_state.clear()
        st.rerun()