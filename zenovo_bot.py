from base_bot.base_bot import BaseBot
import os
import sys
import asyncio
import requests
from emulator_client.emulator_cient import EmulatorClient
import yaml
from prompt_load import load_prompts
from comprehend_agent import ComprehendAgent
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
load_dotenv()
from navigation_screen_set import navigation_set
import ast

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

        navigation_name = "load_pdf_in_sds"
        # Only call start_navigation once and return its result
        self.start_navigation(navigation_name, message)

        navigation_name = "compare_claim_with_pdf"
        self.start_navigation(navigation_name, message)


        
    def send_request(self, key):
        response = self.emulator_client.process_command(key)
        return response
    
    def start_navigation(self, navigation_name, message):
        navigation_data = navigation_set()
        navigation_info = navigation_data.get_navigation(navigation_name)  
        start_command = "start"
        self.send_message(message, "starting the process")
        screens = self.send_request(start_command)
        self.execute_step(navigation_info, screens, message)
        return "Navigation process completed"  # Return a value to indicate completion
    
    def execute_step(self, navigation_info, screens, message):
        agent = ComprehendAgent()  
        size = len(navigation_info)
        for i in range(1, size):            
            key = f"screen{i}"
            condition = navigation_info.get(key).get("condition")
            step = navigation_info.get(key).get("step")
            title = navigation_info.get(key).get("title")
            
            self.send_message(message, f"⏳ <strong>Processing screen: '{title}' | 📝Task:</strong> {step}  | <strong> ⚡ Conditions to be satisfied for processing screen:</strong> {condition}")
            if("compare screens"  in step.lower()):
                response = self.compare_data(screens)
                self.send_message(message, f"✅ <strong>Comparison result:</strong> {response}")
            else:
                actionstr = agent.analyze_process_step(condition, step, screens)
                try:
                    actions = ast.literal_eval(actionstr.strip())
                    if actions[0] == "Screen is not suitable for the operation":
                        self.send_message(message, f"⚠️ <strong>Screen is not suitable for the operation:</strong> {step}")
                        return "exited"
                    
                    self.send_message(message, f"✅ <strong>Identified {len(actions)} action(s) for task:</strong> {step}. Executing sequentially...")
                    
                    for action in actions:
                        print("this is the action", action)
                        if "conditions failed" in action.lower():
                            self.send_message(message,f"⚠️ <strong>Condition check failed:</strong> {action}")
                            return "exited"
                        elif action.lower().startswith("display"):
                            _, message_text = action.split(":", 1)
                            self.send_message(message,f"ℹ️ <strong>Extracted information:</strong> {message_text.strip()}")
                        else:
                            _, actionKey = action.split(":", 1)
                            actionKey = actionKey.strip()
                            self.send_message(message,f"⌨️ <strong>Typing '{actionKey}' into Emulator.</strong>")
                            screens = self.send_request(actionKey)
                except (SyntaxError, ValueError) as e:
                    self.send_message(message,f"❌ <strong>Error parsing actions:</strong> {e}. Raw agent response: {actionstr}")
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
    
    def compare_data(self, screens):
        sds_data = self.emulator_client.pull_data_from_sds()
        claim_data = screens
        comparison_prompt = load_prompts("comparison_prompt")
        comparison_prompt = comparison_prompt.format(sds_data=sds_data, claim_data=claim_data)
        response = self.llm.invoke(comparison_prompt).content
        print("this is the response", response)
        return response

bot = ZenovoBot()
        
bot.start()

bot.join()
bot.cleanup()
