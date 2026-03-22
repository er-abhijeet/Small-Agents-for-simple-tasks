import os
import json
import requests
import tempfile
import logging
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# 1. Configure standard pipeline logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [AGENT] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ensure GEMINI_API_KEY is in your environment variables
genai.configure(api_key="removed_key_for_git")

@app.route('/api/agent', methods=['POST'])
def run_code_agent():
    request_start_time = time.perf_counter()
    data = request.json
    query = data.get('query')
    
    if not query:
        logger.warning("Request rejected: Missing query.")
        return jsonify({"error": "Query is required"}), 400

    logger.info(f"Received problem query: {query}")

    # Step 1: LLM Generation with strict compiler-friendly constraints
    system_instruction = (
        "You are an autonomous code generation agent. The user will provide a problem. "
        "Write an optimal, highly efficient Python script to solve it. "
        "You must hardcode all necessary variables so the script executes independently without user input. "
        "CRITICAL REQUIREMENTS: "
        "1. You MUST output the final computed answer to standard output using print(). "
        "2. Treat the execution environment like a strict competitive programming judge: optimize for O(N) or better time complexity and keep memory allocation under 100MB. "
        "Respond ONLY with a valid JSON object strictly matching this schema: {\"code\": \"<python_code_here>\"}. "
        "Do not include markdown blocks, explanations, or any other text."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_instruction
    )
    
    logger.info("Initiating Gemini API call for code generation...")
    llm_start_time = time.perf_counter()
    
    try:
        response = model.generate_content(query)
        llm_duration = time.perf_counter() - llm_start_time
        logger.info(f"LLM Generation completed in {llm_duration:.2f} seconds.")
        
        response_text = response.text.strip()
        logger.debug(f"Raw LLM Response: {response_text}")
        
        # Strip markdown hallucination safeguards
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()

        code_data = json.loads(response_text)
        python_code = code_data.get('code')
        
        if not python_code:
            raise ValueError("JSON parsed successfully but 'code' key is missing.")
            
        logger.info("Successfully extracted and verified Python code from LLM.")
            
    except Exception as e:
        logger.error(f"LLM Generation/Parsing failed: {str(e)}")
        return jsonify({
            "error": "Failed to generate or parse code from LLM.",
            "details": str(e)
        }), 500

    # Step 2: Write to physical temp file and send to execution API
    compile_url = "http://20.244.41.47:3000/compile"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(python_code)
        temp_file_path = temp_file.name
        logger.info(f"Code temporarily saved to disk: {temp_file_path}")

    try:
        logger.info("Sending payload to compiler execution API...")
        exec_start_time = time.perf_counter()
        
        with open(temp_file_path, 'rb') as f:
            payload = {'lang': 'python'}
            files = {'code': ('main.py', f, 'text/x-python')}
            
            exec_response = requests.post(compile_url, data=payload, files=files)
            exec_data = exec_response.json()

        exec_duration = time.perf_counter() - exec_start_time
        logger.info(f"Remote execution completed in {exec_duration:.2f} seconds.")

        if not exec_data.get('success'):
             logger.error(f"Remote execution failed. Output: {exec_data.get('output')}")
             return jsonify({
                 "error": "Code execution failed", 
                 "generated_code": python_code,
                 "output": exec_data.get('output'),
                 "metrics": {
                     "llm_time_sec": round(llm_duration, 2),
                     "execution_time_sec": round(exec_duration, 2)
                 }
             }), 500

        total_duration = time.perf_counter() - request_start_time
        logger.info(f"Total pipeline execution successful. Total time: {total_duration:.2f} seconds.")
        
        return jsonify({
            "success": True,
            "generated_code": python_code,
            "output": exec_data.get('output'),
            "metrics": {
                 "llm_time_sec": round(llm_duration, 2),
                 "execution_time_sec": round(exec_duration, 2),
                 "total_time_sec": round(total_duration, 2)
            }
        })

    except Exception as e:
        logger.error(f"Compiler API network failure: {str(e)}")
        return jsonify({
            "error": "Failed to communicate with the compiler server.", 
            "details": str(e)
        }), 500
        
    finally:
        # Step 3: Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info("Cleaned up temporary file from disk.")

if __name__ == '__main__':
    app.run(port=5001, debug=True)