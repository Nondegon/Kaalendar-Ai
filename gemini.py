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
                "You are a smart planner. Estimate assignment lengths in minutes. "
                "Return only a list of integers of the same length as the assignments: "
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
