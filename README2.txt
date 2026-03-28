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

# Multi-Step Task Bot (Human-in-the-Loop FSM)

A conversational AI application that executes complex, multi-step tasks by pairing a Large Language Model (LLM) with a Finite State Machine (FSM). 

Unlike autonomous agents (like ReAct) that attempt to solve tasks in a single hidden loop, this system enforces a **Human-in-the-Loop (HITL)** architecture. It breaks tasks down, pauses execution, presents intermediate outputs, and requires explicit user approval before advancing to the next logical step.

## 🛠 Tech Stack

* **Backend:** Python 3, Flask
* **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (via CDN)
* **AI/LLM:** Google Gemini API (`google-genai` SDK)
* **Model:** `gemini-3.1-flash`

## 🧠 Core Methods & Architecture

This project implements several industry-standard design patterns for predictable LLM execution:

1.  **Finite State Machine (FSM) Routing:** The application layer, not the LLM, controls the execution flow. The bot's current state (`PLANNING`, `STEP_1`, `STEP_2`, etc.) acts as the strict boundary for what the AI is allowed to process.
2.  **Dynamic System Prompting:** Instead of a single, massive system prompt, instructions are hot-swapped at every conversational turn based on the FSM state. This prevents "prompt drift" and ensures high adherence to immediate step constraints.
3.  **Deterministic State Transitions:** The LLM is instructed to output specific control tokens (e.g., `[ADVANCE_STATE]`) when it detects the user has approved the current step. The backend parses this token to programmatically move the FSM forward.

## 📂 Project Structure

.
├── app.py                  # Flask backend and FSM routing logic
├── templates/
│   └── index.html          # Frontend UI (Tailwind CSS + JS)
└── README.md