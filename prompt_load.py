def load_prompts(prompt_name):
     prompt_path = f"prompts/zenovo_bot/{prompt_name}.yml"
     with open(prompt_path, 'r') as file:
                prompt_template = file.read()
     return prompt_template






