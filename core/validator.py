from pydantic import ValidationError
import json
import re


async def validate_with_retry(raw_response, schema, retries=2):
    for _ in range(retries):
        try:
            parsed = extract_json(raw_response)
            return schema(**parsed)
        except ValidationError:
            continue

    raise Exception("Invalid AI output")

def extract_json(raw_response: dict):
    # Gemini response structure depends on API format
    # Adjust this based on actual returned structure
    text = raw_response["candidates"][0]["content"]["parts"][0]["text"]

    #Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    #Fallback: extract JSON block using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in AI response")
