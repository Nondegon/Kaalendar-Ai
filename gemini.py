def prompt_gemini(descriptions, api_key):
    import requests, json, re
    
    url = "https://gemini.googleapis.com/v1alpha2/models/text-bison-001:generate"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    
    string = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    
    data = {
        "prompt": {
            "text": (
                "You are a smart planner for a high-school student. You are given a series of descriptions of assignments, "
                "and your goal is to estimate the assignment lengths of each assignment. \nReturn your estimations in the form of a list of integers. "
                "Extremely important guidelines:\n"
                "1. Length of the list must match the number of assignments.\n"
                "2. Provide ONLY a list of integers. Example: [20,30,40,50]\n"
                "3. The list must correspond to the assignments in order.\n"
                "4. List must appear first, before any explanation.\n"
                "Assignments:\n" + string
            )
        },
        "temperature": 0.7,
        "maxOutputTokens": 500
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        text_output = result.get("candidates", [{}])[0].get("content", "")
        
        # Robustly extract first list of integers
        match = re.search(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", text_output)
        if match:
            numbers_str = match.group(1)
            numbers_list = [int(n) for n in re.findall(r"\d+", numbers_str)]
            if len(numbers_list) == len(descriptions):
                return numbers_list
        
        # Fallback: print debug and ask manual input
        print("Could not parse Gemini response:", text_output)
        return [30] * len(descriptions)  # temporary fallback
    else:
        print("Gemini API error:", response.status_code, response.text)
        return [30] * len(descriptions)
