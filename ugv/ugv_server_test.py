import requests

# response = requests.get('http://localhost:3000/ugv/state')
# print(response.text)
# print(response.json()["state"])
# requests.post('http://localhost:3000/ugv/state', json= {"state": "DETACHED"})
# response = requests.get('http://localhost:3000/ugv/state')
# print(response.text)
response = requests.get('http://localhost:3000/ugv/mission/')
print(response.json())