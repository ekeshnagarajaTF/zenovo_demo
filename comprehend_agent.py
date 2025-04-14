from langchain_community.chat_models import ChatOpenAI
import dotenv
import os
from screendeciderAgent import screenDeciderAgent
from prompt_load import load_prompts
dotenv.load_dotenv()

class ComprehendAgent:   
   
    def __init__(self ):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model_name="gpt-4-turbo", temperature = 0.3, openai_api_key=openai_api_key)
        
        
    def analyze_process_step(self, process_conditions,  prompt: str, summary:str, callback = None) -> str:
        
        screen_decider_Agent = screenDeciderAgent()
        check = screen_decider_Agent.analyze_screen(summary, prompt)
        
        if check in ["False", "false"]:
            return '["Screen is not suitable for the operation"]'
        
        breaked_conditions = self.condition_break_down(process_conditions)
        process_analysis_results = self.per_screen_process_analyzer(breaked_conditions, summary)
        simplified_results = self.getSimplifiedResults(process_analysis_results)
        print(simplified_results)

        results =self.condition_sumamry_analyzer(process_analysis_results)
        if("conditions not met" in results.lower()):
            return '["conditions failed"]'
        
        actions_prompt = load_prompts("action_generator")
        actions_prompt = actions_prompt.format(screen_data=summary, prompt=prompt)
        response = self.llm.invoke(actions_prompt)
        actions_response = self.format_outputActions(response.content)
        return actions_response
    
        #return  { action_type: "anything", value: actions_response }

    def per_screen_process_analyzer(self,formatted_conditions, screen_data):

            condition_prompt = load_prompts("process_analyzer") 
            prompt = condition_prompt.format(screen_data=screen_data, formatted_conditions=formatted_conditions)
            response = self.llm.invoke(prompt)
            return response.content

    def getSimplifiedResults(self, process_analysis_results):
        condition_prompt = load_prompts("condition_summarizer") 
        prompt = condition_prompt.format(process_analysis_results = process_analysis_results)
        response = self.llm.invoke(prompt)
        return response.content

    def format_outputActions(self, actions):
        formatting_prompt = f'''
                            Your are a python list extractor, your job is to strictly return python list present in the data so it can be directly used in python code without any formatting errors.
                            Given the actions data - {actions}.
                            If the data contains any json annotations or some extra summary, extract the list from the data and return only valid python list.
                            Dont summarize the data only return valid python list present in data as response.
                            Strictly follow the output format. exmaple format ["action1", "action2", "action3"]
                            ''' 
        
        response = self.llm.invoke(formatting_prompt)
        return response.content

    def condition_sumamry_analyzer(self, process_analysis_results):
        condition_prompt = load_prompts("conditions_summary_analyzer") 
        prompt = condition_prompt.format(conditions_analysis = process_analysis_results)
        response = self.llm.invoke(prompt)
        return response.content
    
    def condition_break_down(self, conditions): 
        response = self.llm.invoke(f'''
                                    Given the conditions - {conditions},break down the combined conditions into individual conditions and return in json format.
                                    Only analyse the givn condtions and don't give any general response or summary.
                                    output format : {{condition_name: condition description}}.
                                    If no conditions are present return "No conditions to check".
                                     ''')
        return response.content      

    
