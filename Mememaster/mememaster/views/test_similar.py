'''
@Author: chivalryq
@Date: 2020-03-28 11:05:45
@Description: file content
'''
import requests

url = "https://www.myworkroom.cn:5000/similar"

payload = {}
files = [
    ('file', open('C:/Users/jnjga/OneDrive - business/桌面/university/meme_db/pic/90度谢谢/90度谢谢_4.jpeg', 'rb'))
]
headers = {

}

response = requests.post(url, headers=headers, data=payload, files=files)

print(response.text.encode('utf8'))
