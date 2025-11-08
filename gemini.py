import requests
import json
import re

def prompt_gemini(descriptions, api_key):
    import requests, json, re
    
    url = "https://gemini.googleapis.com/v1alpha2/models/text-bison-001:generate"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    string = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    
    data = {
        "prompt": {
            "text": (
                "You are a smart planner for a high-school student. You are given a series of descriptions of assignments, and your goal is to estimate the assignment lengths of each assignment. \n Return your estimations in the form of a list of integers, describing how many minutes it takes. \n \n Extremely important guidelines: \n 1. The length of the list should be equivalent to the number of assignments given. \n 2. Provide a list, and only the list of integers, where each integer corresponds to how many minutes the assignment takes. An example output would be [20,30,40,50]. \n 3. Make sure each element in the list corresponds to their assignment. \n 4. Provide the list first, before explaining your reasoning. \n The assignment descriptions are listed out here:"
                + string
            )
        },
        "temperature": 0.7,
        "maxOutputTokens": 500
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        text_output = result.get("candidates", [{}])[0].get("content", "")
        
        # Try to extract integers more robustly
        numbers = re.findall(r"\d+", text_output)
        if len(numbers) >= len(descriptions):
            numbers_list = [int(n) for n in numbers[:len(descriptions)]]
            return numbers_list
        else:
            # Fallback: return 30 mins for each assignment if parsing fails
            return [30] * len(descriptions)
    else:
        # If API error, return 30 mins default
        return [30] * len(descriptions)
