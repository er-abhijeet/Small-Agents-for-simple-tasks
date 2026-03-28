import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# LangChain Imports - Updated for Modern LCEL Architecture
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = Flask(__name__)
CORS(app) 

# In-memory reference to the vector store for demonstration.
global_vector_store = None

@app.route('/api/upload', methods=['POST'])
def upload_document():
    global global_vector_store
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)

        try:
            # 1. Load and extract
            loader = PyPDFLoader(temp_path)
            docs = loader.load()

            # 2. Chunk the document
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)

            # 3. Create Embeddings and Vector Store
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            global_vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)

            return jsonify({
                "message": "Document processed and knowledge base created successfully.", 
                "chunks": len(splits)
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        return jsonify({"error": "Only PDF files are supported currently."}), 400


@app.route('/api/query', methods=['POST'])
def query_document():
    global global_vector_store
    
    if not global_vector_store:
        return jsonify({"error": "No document has been uploaded yet."}), 400

    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "Query is required."}), 400

    try:
        # 1. Initialize Gemini Model
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

        # 2. Retrieve Documents directly (to retain metadata for citations)
        retriever = global_vector_store.as_retriever(search_kwargs={"k": 4})
        retrieved_docs = retriever.invoke(user_query)

        # 3. Format context for the LLM
        formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        # 4. Build the LCEL Generation Chain
        system_prompt = (
            "You are an expert AI research assistant. Use the provided context to answer the user's query. "
            "If you don't know the answer based on the context, state that clearly. \n\n"
            "Context: {context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{query}"),
        ])

        # Modern LCEL Pipeline: Prompt -> LLM -> String Output
        generation_chain = prompt | llm | StrOutputParser()

        # 5. Execute Chain
        answer = generation_chain.invoke({
            "context": formatted_context,
            "query": user_query
        })

        # 6. Extract Citations from the retrieved_docs
        citations = []
        for doc in retrieved_docs:
            citations.append({
                "page": doc.metadata.get('page', 'N/A'),
                "content": doc.page_content
            })

        return jsonify({
            "answer": answer,
            "citations": citations
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)