Group Members:
Abhijeet Mohapatra (DSAI 231020202)
Akash Kumar (DSAI 231020408)

Video Demonstration Link: https://drive.google.com/file/d/1ylKk8NLucmkr-pcKAtpwQLLjzRhBdvvy/view?usp=sharing
Github Repo: https://github.com/er-abhijeet/Small-Agents-for-simple-tasks

--------------------------------------------------------------------------------
Project: AI Research Assistant
--------------------------------------------------------------------------------

TECHNOLOGIES
Python, JavaScript, React, Tailwind CSS, Flask, LangChain (LCEL), ChromaDB, Google Gemini API.

TECH STACK
* Frontend: React.js (built with Vite) for UI state management; Tailwind CSS for modern, responsive styling.
* Backend: Python with Flask and Flask-CORS, providing a decoupled REST API architecture.
* Orchestration: LangChain Expression Language (LCEL) for building asynchronous, transparent LLM pipelines.
* Language Model: Google Generative AI (Gemini 1.5 Pro) for high-accuracy text synthesis and reasoning.
* Vector Database: ChromaDB for local vector indexing and fast semantic similarity search.
* Embeddings: Google Generative AI Embeddings (models/gemini-embedding-001) for text vectorization.
* Document Processing: PyPDFLoader for text/metadata extraction; RecursiveCharacterTextSplitter for optimal chunking.

METHODOLOGY
1. Ingestion & Chunking: The backend receives a PDF, extracts selectable text along with page number metadata, and splits the text into overlapping chunks to preserve contextual boundaries.
2. Embedding & Indexing: Text chunks are converted into dense vector representations and stored in a ChromaDB vector database.
3. Retrieval (RAG): User queries are embedded into the same vector space to retrieve the top-k most semantically similar document chunks.
4. Generation: An LCEL pipeline injects the retrieved chunks and the original query into a strict prompt template, instructing the Gemini API to synthesize an answer grounded only in the provided context.
5. Presentation: The React frontend displays the generated response alongside accurate, page-level citations extracted directly from the retrieved chunk metadata.


--------------------------------------------------------------------------------
Project: Autonomous Code Interpreter Agent
--------------------------------------------------------------------------------

TECHNOLOGIES (KEYWORDS)
React.js, TailwindCSS, Python 3, Flask, REST API, Gemini 2.5 Flash, Prompt Engineering, Multipart/Form-Data, Remote Code Execution (RCE), Sandboxing.

TECH STACK
- Frontend: React (UI), Tailwind CSS (Styling), Lucide React (Icons).
- Backend: Python 3, Flask (Web Framework), Flask-CORS (Cross-Origin Resource Sharing), Requests (HTTP Client), Built-in modules (Tempfile, Logging, Time).
- AI/LLM: Google Generative AI SDK (gemini-2.5-flash model) for autonomous code generation.
- Execution Environment: External Code Compilation Server handling multipart/form-data requests for remote code execution.

METHODOLOGY
The React frontend captures a user's algorithmic query and forwards it to the Flask API.
The backend orchestrates a call to the Gemini 2.5 Flash model using a highly constrained system prompt to generate an optimized, memory-efficient Python script formatted strictly as JSON.
The backend parses this JSON, writes the executable code to a thread-safe temporary file, and dispatches it to an isolated remote execution server.
The execution outputs, along with precise pipeline latency metrics, are then retrieved and streamed back to the frontend UI.