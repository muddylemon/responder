import json
import requests
from models import *


url = "http://localhost:11434/api/generate"
systemPrompt = "You are a helpful content writer and research. Return comprehensive text that is easy to understand."


def generate(prompt, context, model=LLAMA3, systemPrompt=systemPrompt, temperature=0.8) -> tuple[str, list[dict]]:

    payload = {
        "system": systemPrompt,
        "model": model,
        "prompt": prompt,
        "context": context,
        "stream": False,
        "temperature": temperature,
    }
    payload_json = json.dumps(payload)
    r = requests.post(url,
                      headers={"Content-Type": "application/json"},
                      data=payload_json,
                      stream=False)

    r.raise_for_status()
    json_response = json.loads(r.text)
    if "error" in json_response:
        raise Exception(json_response["error"])

    return json_response["response"], json_response["context"]
