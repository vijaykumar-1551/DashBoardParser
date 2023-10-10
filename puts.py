import requests
import json

object_id = "65155328e1f03719003c3282"
url = f"http://127.0.0.1:5000/update_data/65155328e1f03719003c3282"

data = {
    "comments": "New Comment 3",
    "plan_of_action": "New Plan of Action 3",
    "eta": "New ETA 3"
}

headers = {'Content-Type': 'application/json'}

response = requests.put(url, data=json.dumps(data), headers=headers)

print(response.status_code)
print(response.json())
