import requests

url = "http://localhost:5000"
s = requests.Session()

response = s.post(f'{url}/auth/register', 
    json={"username": "emma", "password": "123Pass"})

#response = s.post(f'{url}/auth/login', 
#                  json={"username": "emma", "password": "123Pass"})

response = s.get(f'{url}/screeners')

print(f"Status Code: {response.status_code}\n")

try:
    response_body = response.json()
    
    # Check if the body is a dictionary
    if isinstance(response_body, dict):
        for k, v in response_body.items():
            print(f"Key: {k}")
            # Only loop if v is actually a list or tuple
            if isinstance(v, (list, tuple)):
                for item in v:
                    print(f"  - {item}")
            else:
                print(f"  - {v}")
                
    # Check if the body is a list
    elif isinstance(response_body, list):
        for item in response_body:
            print(item)
            
    else:
        print(response_body)

except requests.exceptions.JSONDecodeError:
    print("Response is not valid JSON:")
    print(response.text)