import json
import os
class navigation_set :

    def get_navigationData(self):
        

        json_filename = "./prompts/zenovo_bot/data.json"
        navigation_data = {}
        if os.path.exists(json_filename):
            with open(json_filename, "r") as json_file:
                navigation_data = json.load(json_file)
            print("Successfully loaded navigation data.")
        else:
            print(f"Error: {json_filename} not found!")

        return navigation_data

    def get_navigation(self, process_id) :    
        
      navigation_data = self.get_navigationData()
      if process_id in navigation_data:
          return navigation_data.get(process_id)
      else:
          print(f"Process {process_id} not found in JSON.")

    def getNavigationOptions(self):
        
        navigation_data = self.get_navigationData()
        return navigation_data.keys() 