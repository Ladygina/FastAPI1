import requests
from models import *



# POST-запрос
Andrew = Author(id=1, name='Andrew')
print(Andrew, Andrew.to_dict())

data = {'id':11, "title": "adv1", "description": 'book1', 'price':1000,'author':Andrew.to_dict(),  'created_at': datetime.now().isoformat()}
response = requests.post('http://localhost:8080/advertisement/', json=data)
print(response.json())

# GET-запрос
response = requests.get('http://localhost:8080/advertisement/11')
print(response.json())

# PATCH
data = {'price':1500}
response = requests.patch('http://localhost:8080/advertisement/11', json=data)
print(response.json())

# Delete
response = requests.delete('http://localhost:8080/advertisement/11')
print(response.json())