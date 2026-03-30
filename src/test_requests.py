import requests

response = requests.post('http://localhost:5000/register', 
    json={"username": "jerma985", "password": "SchlumBO69"})

print(response.status_code)
print(response.json())
