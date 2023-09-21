from datetime import datetime, timedelta
import requests

'2023-09-20 22:29:09.086886'

date_1 = datetime.strptime('2023-09-20 22:29:09.086886', "%Y-%m-%d %H:%M:%S.%f")

date = datetime.now()

url = 'http://localhost:14141/file/'
data = {
    "user_id": 1953960185,
    "file_name": "BSRT00200_R_20230020000_01H_01S_MO.rnx",
    "datetime": date,
}

responce = requests.post(url=url, data=data)
print(responce)
