import requests

#response = requests.post('http://localhost:5000/register', 
#    json={"username": "emma", "password": "123Pass"})

response = requests.post('http://localhost:5000/login',
                         json={"username": "emma", "password": "123Pass"})

print(response.status_code)
print(response.json())
