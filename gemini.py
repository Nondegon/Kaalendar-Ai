import requests
import json
import re

def prompt_gemini(descriptions, api_key):
    url = "https://gemini.googleapis.com/v1alpha2/models/text-bison-001:generate"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    string = ""
    for ind, desc in enumerate(descriptions):
        string += "\n" + str(ind + 1) + "." + desc
    
    data = {
        "prompt": {
            "text": (
                "You are a smart planner for a high-school student. You are given a series of descriptions of assignments, "
                "and your goal is to estimate a lower bound on the assignment lengths of each assignment. Return your estimations "
                "in the form of a list of integers, describing how many minutes it takes. \n\n"
                "Extremely important guidelines: \n"
                "1. The length of the list should be equivalent to the number of assignments given.\n"
                "2. Provide a list, and only the list of integers, where each integer corresponds to how many minutes the assignment takes. "
                "An example output would be [20, 30, 40, 50].\n"
                "3. Make sure each element in the list corresponds to their assignment.\n"
                "4. Provide the list first, before explaining your reasoning. The assignment descriptions are listed out here:"
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
        
        # Regex to find the first list of integers
        match = re.search(r"\[(\d+(?:,\d+)*)\]", text_output)
        if match:
            numbers_str = match.group(1)
            numbers_list = [int(n) for n in numbers_str.split(",")]
            return numbers_list
        else:
            return f"No list of integers found in the response: {text_output}"
    else:
        return f"Error {response.status_code}: {response.text}"


