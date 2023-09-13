import requests

data_person = {
    'user_id': 12345,
    'name': 'test_user',
    'phone': '12345678'
}
data_note = {
    'user_id': 12345,
    'note_type': 0,
    'text': 'afsdfjhdjaksd'
}

url = 'http://localhost:8000/person/'
url = 'http://localhost:8000/note/'
response = requests.post(url=url, data=data_note)
print(response.status_code)
