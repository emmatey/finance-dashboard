import requests

url = "http://localhost:5000"
s = requests.Session()

#response = s.post(f'{url}/auth/register', 
#    json={"username": "emma", "password": "123Pass"})

response = s.post(f'{url}/auth/login', 
                  json={"username": "emma", "password": "123Pass"})

#response = s.get(f'{url}/user/summary?username=emma')

#response = s.get(f'{url}/user/portfolio?username=emma')

#response = s.get(f'{url}/user/transactions')

#response = s.get(f'{url}/user/balance_snapshots?username=emmma')

#response = s.get(f'{url}/trade?ticker=m')

response = s.post(f'{url}/trade',
                  json = {"ticker": "bbdgdgfdby", "qty": "3", "transaction_type": "sell"})

print(response)
print(response.status_code)
print(response.json())
