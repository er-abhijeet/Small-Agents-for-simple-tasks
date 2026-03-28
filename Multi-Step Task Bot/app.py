# import os
# from google import genai
# from google.genai import types

# class MultiStepTaskBot:
#     def __init__(self):
#         # Initialize the FSM state
#         self.state = "PLANNING"
#         # Maintain an explicit array for conversation memory
#         self.memory = []
        
#         # Initialize the client. It automatically picks up the GEMINI_API_KEY environment variable.
#         self.client = genai.Client(api_key="AIzaSyBbJDUDMRPPICJyWj4b44GxWKgqxoxninY")
#         self.model_id = "gemini-2.5-flash" 

#     def _get_system_prompt(self) -> str:
#         """Returns the strict instructions for the current state."""
#         prompts = {
#             "PLANNING": "You are a task planner. Break the user's request into 3 logical steps. Ask the user if they agree to proceed with Step 1. Stop generating after asking.",
#             "STEP_1": "We are on Step 1: Identify Purpose. Ask targeted questions to gather constraints (dates, budget). Do not draft the itinerary yet. Once you have enough info, summarize it and ask the user to confirm. If they explicitly confirm, end your response with exactly: [ADVANCE_STATE]",
#             "STEP_2": "We are on Step 2: Suggest Itinerary. Draft a schedule based on the constraints. Ask for feedback. Once they approve the final draft, end your response with exactly: [ADVANCE_STATE]",
#             "STEP_3": "We are on Step 3: Recommend Travel Plan. Suggest specific flights and transit options. Ask if the task is complete."
#         }
#         return prompts.get(self.state, "")

#     def process_user_input(self, user_text: str) -> str:
#         # 1. Append user message to memory using the strongly typed Content schema
#         self.memory.append(
#             types.Content(role="user", parts=[types.Part.from_text(text=user_text)])
#         )

#         # 2. Dynamically inject the system prompt for the CURRENT state
#         config = types.GenerateContentConfig(
#             system_instruction=self._get_system_prompt(),
#             temperature=0.2 # Low temperature enforces strict adherence to step instructions
#         )

#         # 3. Call the Gemini API
#         response = self.client.models.generate_content(
#             model=self.model_id,
#             contents=self.memory,
#             config=config
#         )

#         bot_reply = response.text

#         # 4. Application-level State Transition Logic
#         # (Triggering state changes based on user agreement or LLM markers)
#         if self.state == "PLANNING" and "yes" in user_text.lower():
#             self.state = "STEP_1"
#         elif "[ADVANCE_STATE]" in bot_reply:
#             # Clean the hidden marker from the output shown to the user
#             bot_reply = bot_reply.replace("[ADVANCE_STATE]", "").strip()
            
#             # Advance the state machine
#             if self.state == "STEP_1":
#                 self.state = "STEP_2"
#             elif self.state == "STEP_2":
#                 self.state = "STEP_3"

#         # 5. Append the cleaned bot response to memory
#         self.memory.append(
#             types.Content(role="model", parts=[types.Part.from_text(text=bot_reply)])
#         )

#         return bot_reply

# # Example Execution
# if __name__ == "__main__":
#     bot = MultiStepTaskBot()
#     print("Bot initialized. What task would you like to plan? (Type 'quit' to exit)")
    
#     while True:
#         user_input = input("\nUser: ")
#         if user_input.lower() == 'quit':
#             break
            
#         response = bot.process_user_input(user_input)
#         print(f"\nBot [State: {bot.state}]:\n{response}")

import os
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

class MultiStepTaskBot:
    def __init__(self):
        self.state = "PLANNING"
        self.memory = []
        # Pulls from GEMINI_API_KEY environment variable
        self.client = genai.Client(api_key="AIzaSyBbJDUDMRPPICJyWj4b44GxWKgqxoxninY")
        self.model_id = "gemini-2.5-flash" 

    def _get_system_prompt(self) -> str:
        prompts = {
            "PLANNING": "You are a task planner. Break the user's request into 3 logical steps. Ask the user if they agree to proceed with Step 1. Stop generating after asking.",
            "STEP_1": "We are on Step 1: Identify Purpose. Ask targeted questions to gather constraints (dates, budget). Do not draft the itinerary yet. Once you have enough info, summarize it and ask the user to confirm. If they explicitly confirm, end your response with exactly: [ADVANCE_STATE]",
            "STEP_2": "We are on Step 2: Suggest Itinerary. Draft a schedule based on the constraints. Ask for feedback. Once they approve the final draft, end your response with exactly: [ADVANCE_STATE]",
            "STEP_3": "We are on Step 3: Recommend Travel Plan. Suggest specific flights and transit options. Ask if the task is complete."
        }
        return prompts.get(self.state, "")

    def process_user_input(self, user_text: str) -> str:
        self.memory.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_text)])
        )

        config = types.GenerateContentConfig(
            system_instruction=self._get_system_prompt(),
            temperature=0.2 
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=self.memory,
            config=config
        )

        bot_reply = response.text

        if self.state == "PLANNING" and "yes" in user_text.lower():
            self.state = "STEP_1"
        elif "[ADVANCE_STATE]" in bot_reply:
            bot_reply = bot_reply.replace("[ADVANCE_STATE]", "").strip()
            if self.state == "STEP_1":
                self.state = "STEP_2"
            elif self.state == "STEP_2":
                self.state = "STEP_3"

        self.memory.append(
            types.Content(role="model", parts=[types.Part.from_text(text=bot_reply)])
        )

        return bot_reply

app = Flask(__name__)
# Global instance for single-user local testing. 
# In production, state and memory are retrieved from a database per request.
bot = MultiStepTaskBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        reply = bot.process_user_input(user_message)
        return jsonify({
            'reply': reply,
            'state': bot.state
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)