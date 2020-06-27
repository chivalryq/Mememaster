import urllib.request,urllib
import json
import base64

def meme_check(file_stream):#输入二进制流，返回是否属于表情包
    # 配置部分
    API_KEY = 'QiL79ejnS7xpscY1NXaqTW1H'
    SECRECT_KEY = 'lScugwV3ewUN4rAVsKXRjVIizCUtb73d'

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_KEY + '&client_secret=' + SECRECT_KEY
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request).read().decode('utf-8')
    token = json.loads(response)["access_token"]

    #--------------接口部分
    url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/classification/meme-check?access_token=' + token
    base64_data = base64.b64encode(file_stream)#base64编码
    base64_data = base64_data.decode(encoding='utf-8')
    data ="{\"image\":\"" + base64_data + "\",\"top_num\":\"5\"}"
    headers = {
        'Content-Type' : 'application/json'
    }
    data = data.encode('utf-8')
    request = urllib.request.Request(url,data,headers)
    html = urllib.request.urlopen(request).read().decode('utf-8')
    result = json.loads(html)["results"]
    if(result[0]["name"] == 'class0'):
        return True
    else:
        return False

def meme_classify(file_stream):#表情包分类
    API_KEY = 'QiL79ejnS7xpscY1NXaqTW1H'
    SECRECT_KEY = 'lScugwV3ewUN4rAVsKXRjVIizCUtb73d'
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_KEY + '&client_secret=' + SECRECT_KEY
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request).read().decode('utf-8')
    token = json.loads(response)["access_token"]
    #--------------接口部分
    url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/classification/memeClassify?access_token=' + token
    base64_data = base64.b64encode(file_stream)#base64编码
    base64_data = base64_data.decode(encoding='utf-8')
    data ="{\"image\":\"" + base64_data + "\",\"top_num\":\"5\"}"
    headers = {
        'Content-Type' : 'application/json'
    }
    data = data.encode('utf-8')
    request = urllib.request.Request(url,data,headers)
    html = urllib.request.urlopen(request).read().decode('utf-8')
    # print(html)
    result = json.loads(html)["results"][0]['name']
    return result

def spam_check(content):#返回值 ： 0 直接通过 1 直接拒绝保存 2 可以保存，但是不能被他人看见
    API_KEY = '1SiksWwCal365PNSu2HZDehz'
    SECRECT_KEY = 'VK3DQp8O8laGFUKLRTMwuPGtMHZKaRFP'
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_KEY + '&client_secret=' + SECRECT_KEY
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request).read().decode('utf-8')
    token = json.loads(response)["access_token"]
    #--------------接口部分
    url = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam?access_token=' + token
    data = "content=" + content
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded'
    }
    data = data.encode('utf-8')
    request = urllib.request.Request(url,data,headers)
    html = urllib.request.urlopen(request).read().decode('utf-8')
    result = json.loads(html)["result"]
    print("敏感词检测结果",result)
    return result["spam"]