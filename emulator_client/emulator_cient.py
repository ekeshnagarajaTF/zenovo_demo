import asyncio
import base64
import threading
import time
import requests

stop_event = threading.Event()

class EmulatorClient:
    def __init__(self):
        self.port = 5002
        self.REST_API_URL = None
        pass

    def pull_data_from_sds(self):
        sds_data = requests.get(f"http://localhost:{self.port}/sds_data")
        return sds_data.json()

# "A function" that takes input, process it, and gives you back with new set of instructions (screen info and nav options)
    def process_command(self, command):
        try:
            # 1. Call REST API
            self.REST_API_URL = f"http://localhost:{self.port}/command"
            print(f"Calling REST API for message: {command}")
            response = requests.post(self.REST_API_URL, json={"message": command})  # Adapt request as needed
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            rest_response = response.json()  # Parse JSON response
            # print(f"{rest_response}")

            print('SLEEPING 1 seconds before next screenshot')
            time.sleep(1)
            print(f"this is the response............. {type(rest_response)}")
            # Convert the response dictionary to a string representation
            if isinstance(rest_response, dict):
                rest_response = str(rest_response)
                print(f"Converted response to string: {type(rest_response)}")
            return rest_response

        except requests.exceptions.RequestException as e:
            print(f"Error calling REST API: {e}")
            return {"error": str(e)}  # Return error information
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": str(e)}
    
    def get_current_screen(self):
        current_screen = requests.get(f"http://localhost:{self.port}/api/current-screen")
        try:
            response = current_screen
            # Check if the response is successful
            response.raise_for_status()
            
            # Try to convert to JSON first
            try:
                screen_data = response.json()
                return str(screen_data)
            except ValueError:
                # If not JSON, return the text content
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error getting current screen: {e}")
            return str({"error": str(e)})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return str({"error": str(e)})
        
