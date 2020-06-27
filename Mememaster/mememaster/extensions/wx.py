import json
import requests
import datetime
APPID="wxc951eb5ff4b76039"
SECRET="06f867f86c74eb1ba4034a258d0d29a1"

def getuserinfo(code):
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (
    APPID, SECRET, code)
    response = requests.get(url)
    info = response.text
    log = open('log', 'a+')
    log.write(str(datetime.datetime.now()) + "------>" + json.loads(info)+'\n')
    log.close()
    if response.status_code == 200:
        info = response.text
        return json.loads(info)


