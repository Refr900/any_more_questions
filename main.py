import requests
import json

response = requests.get(
  url="https://openrouter.ai/api/v1/auth/key",
  headers={
    "Authorization": f"Bearer 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"
  }
)

print(json.dumps(response.json(), indent=2))
