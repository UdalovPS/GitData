import requests

# data_person = {
#     'user_id': 12345,
#     'name': 'test_user',
#     'phone': '12345678'
# }
# data_note = {
#     'user_id': 12345,
#     'username': 'udalov',
#     'note_type': 0,
#     'text': 'afsdfjhdjaksd'
# }
#
# url = 'http://localhost:8000/person/'
# url = 'http://localhost:8000/note/'
# response = requests.post(url=url, data=data_note)
# print(response.status_code)


# url = "http://212.220.202.105:8080/RINEX/RINEX/2023/001(0101)/TOUR/TOUR00100_R_20230010000_01H_MN.rnx"
# responce = requests.get(url=url)
# with open(f"./file.rnx", 'wb') as file:
#     file.write(responce.content)
# print(responce.status_code)
# print(responce.headers['content-type'])
# print(responce.encoding)


# TOKEN = "1955432392:AAFIKGS33j1DsT-zsWIAc_fs6ckOX4yjLQY"
# method = 'sendDocument'
# file = open('small.txt', 'rb')
# response = requests.post(
#         url=f'https://api.telegram.org/bot{TOKEN}/{method}',
#         data={'chat_id': 1953960185, 'text': '/check'},
#         files={'document': file}
#     ).json()
#
# print(response)

url = "http://localhost:8000/file/"
data = {'url': 'urll'}
responce = requests.get(url=url, params=data)
print(responce.json())
