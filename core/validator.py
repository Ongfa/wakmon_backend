from pydantic import ValidationError
import json
import re


async def validate_with_retry(provider, prompt, schema, max_retries=2):
    last_exception = None

    for attempt in range(max_retries + 1):
        raw_response = await provider.generate(prompt)

        try:
            parsed = extract_json(raw_response)
            validated = schema(**parsed)
            return validated

        except (ValidationError, ValueError) as e:
            last_exception = e
            # Optionally log here
            continue

    raise Exception(f"AI validation failed after retries: {last_exception}")


def extract_json(raw_response: dict):
    # Gemini response structure depends on API format
    # Adjust this based on actual returned structure
    text = raw_response["candidates"][0]["content"]["parts"][0]["text"]

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON block using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in AI response")
