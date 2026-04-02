import requests

s = requests.Session()
#response = s.post('http://localhost:5000/register', 
#    json={"username": "emma", "password": "123Pass"})

response = s.post('http://localhost:5000/auth/login',
                         json={"username": "emma", "password": "123Pass"})

response = s.get('http://localhost:5000/user/summary')


print(response)
print(response.status_code)
print(response.json())
