from base_bot.base_bot import BaseBot
import os
import sys
import asyncio
import requests
from compare import compare_data
from emulator_client.emulator_cient import EmulatorClient
import yaml
from prompt_load import load_prompts
from comprehend_agent import ComprehendAgent
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
import compare
from navigation_screen_set import navigation_set
import ast
import os
from datetime import datetime

load_dotenv()
class ZenovoBot(BaseBot):
    
    def __init__(self, options=None):
        """
        Initialize the ZenovoBot with custom configuration
        
        Args:
            options (dict, optional): Additional configuration options
        """
        # Set default options for this bot
        default_options = {
            "bot_id": "zenovo_bot",
            "bot_name": "Zenovo Bot",
            "bot_type": "task_bot",
            "autojoin_channel": "general"
        }

        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model_name="gpt-4-turbo", temperature = 0.3, openai_api_key=openai_api_key)
        self.emulator_client = EmulatorClient()
        
        # Merge with any provided options
        if options:
            default_options.update(options)
            
        # Initialize the parent class with our options
        super().__init__(options=default_options)
        
    async def generate_response(self, message):
        print("hey this is the message", message)
        self.emulator_client.port = "5001"
        navigation_name = "load_pdf_in_sds"

        reponse = self.start_navigation(navigation_name, message)
        self.emulator_client.port = "5003"
        navigation_name = "compare_claim_with_pdf"
        reponse = self.start_navigation(navigation_name, message)
        return reponse
     
    def send_request(self, key):
        response = self.emulator_client.process_command(key)
        return response
    
    def start_navigation(self, navigation_name, message):
        navigation_data = navigation_set()
        navigation_info = navigation_data.get_navigation(navigation_name)  
        self.send_message(message, "starting the process")
        screens = self.emulator_client.get_current_screen()
        self.execute_step(navigation_info, screens, message)
        return "Navigation process completed"  # Return a value to indicate completion
    
    def execute_step(self, navigation_info, screens, message):
        agent = ComprehendAgent()  
        size = len(navigation_info)
        for i in range(1, size+1):            
            key = f"screen{i}"
            condition = navigation_info.get(key).get("condition")
            step = navigation_info.get(key).get("step")
            title = navigation_info.get(key).get("title")
            self.send_message(message, f"⏳ Processing screen: '{title}' | 📝Task: {step}  |  ⚡ Conditions to be satisfied for processing screen: {condition}")
            if("compare"  in step.lower()):
                response = self.compare_data(screens, message)
                self.send_message(message, f"✅ Comparison result: {response}")
            else:
                actionstr = agent.analyze_process_step(condition, step, screens)
                try:
                    actions = ast.literal_eval(actionstr.strip())
                    if actions[0] == "Screen is not suitable for the operation":
                        self.send_message(message, f"⚠️ Screen is not suitable for the operation: {step}")
                        return "exited"
                    
                    self.send_message(message, f"✅ Identified {len(actions)} action(s) for task: {step}. Executing sequentially...")
                    
                    for action in actions:
                        print("this is the action", action)
                        if "conditions failed" in action.lower():
                            self.send_message(message,f"⚠️ Condition check failed: {action}")
                            return "exited"
                        elif action.lower().startswith("display"):
                            _, message_text = action.split(":", 1)
                            self.send_message(message,f"ℹ️ Extracted information: {message_text.strip()}")
                        else:
                            _, actionKey = action.split(":", 1)
                            actionKey = actionKey.strip()
                            self.send_message(message,f"⌨️ Typing '{actionKey}' into Emulator.")
                            screens = self.send_request(actionKey)
                except (SyntaxError, ValueError) as e:
                    self.send_message(message,f"❌ Error parsing actions: {e}. Raw agent response: {actionstr}")
                    continue
        
        return "navigation completed"
        

    def send_message(self, message, output):
        print("sending message", message, output)
        # Check if message is a dictionary or a string
        if isinstance(message, dict):
            channel_id = message.get("channelId")
        else:
            # If message is a string, use the current channel
            channel_id = self.state.get("current_channel_id")
            
        if channel_id:
            self.socket.emit('message', {
                "channelId": channel_id,
                "content": output
            })
        else:
            print("Warning: No channel ID available to send message")
    
    def compare_data(self, screens, message):
            self.emulator_client.port = 5001
            sds_data = self.emulator_client.pull_data_from_sds()
            claim_data = screens
            comparison_prompt = load_prompts("comparison_prompt")
            comparison_prompt = comparison_prompt.format(sds_data=sds_data, claim_data=claim_data)
            response = self.llm.invoke(comparison_prompt).content
            self.save_comparison_result(response, message)
            return response
       

    def save_comparison_result(self, result, message):
        """
        Save the comparison result to the downloads folder
        """
        print("Starting to save comparison result...")
        
        # Create downloads directory if it doesn't exist
        downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Generate filename with timestamp to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(downloads_dir, f"comparison_results_{timestamp}.txt")
        
        # Save the result to file
        with open(filename, "w") as f:
            f.write(result)
        self.send_message(message, f"Comparison results saved to: {filename}")
        print(f"Comparison results saved to: {filename}")
        return filename

bot = ZenovoBot()
        
bot.start()

bot.join()
bot.cleanup()
