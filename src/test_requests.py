import requests

url = "http://localhost:5000"
s = requests.Session()

#response = s.post(f'{url}/register', 
#    json={"username": "emma", "password": "123Pass"})

response = s.post(f'{url}/auth/login', 
                  json={"username": "emma", "password": "123Pass"})

#response = s.get(f'{url}/user/summary?username=emma')

#response = s.get(f'{url}/user/portfolio?username=emma')

response = s.get(f'{url}/user/transactions')

print(response)
print(response.status_code)
print(response.json())
