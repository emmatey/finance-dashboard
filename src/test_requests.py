import requests

response = requests.post('http://localhost:5000/register', 
    json={"username": "emma", "password": "hunter2"})

print(response.status_code)
print(response.json())
