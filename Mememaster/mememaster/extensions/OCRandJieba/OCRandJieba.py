import jieba
import json
import random
import os
import base64
import time
import requests
import hmac
import hashlib
import sys
import os
import logging
jieba.setLogLevel(logging.INFO)
realpath=os.path.split(os.path.realpath(__file__))[0]
userDicFile = os.path.join(realpath,r'userdict.txt')#当前该文件为空
jieba.load_userdict(userDicFile)
stopWordPath =os.path.join(realpath,r'stopWord.txt')

def loadStopWords():
    stop = [line.strip() for line in open(stopWordPath,encoding='utf-8').readlines()]
    return stop


# 去除停止词
def cutWord(sentence, stopWords):
    segList = jieba.cut(sentence, cut_all=False)
    leftWords = []
    for i in segList:
        if (i not in stopWords):
            leftWords.append(i)
    return ('/'.join(leftWords))

def cutWord2(sentence, stopWords):
    segList = jieba.cut(sentence, cut_all=False)
    leftWords = []
    for i in segList:
        if (i not in stopWords):
            leftWords.append(i)
    return (leftWords)


def readAndCut(stop, ocrResult):
    data = ocrResult
    cut_result = cutWord(ocrResult, stop)
    return cut_result


def CountWordNum(jiebaResult):
    dictionary = {}
    words = jiebaResult.split("/")
    for word in words:
        if not word in dictionary:
            dictionary[word] = 1
        else:
            dictionary[word] += 1
    return dictionary


def jiebaPython(ocrResult):
    stopWords = loadStopWords()
    jiebaResult = readAndCut(stopWords, ocrResult)

    result = CountWordNum(jiebaResult)
    return result


# acountNumber用于选择不同的上传账号 0金洪 1步顺 2苏子扬 3史一栋
def ocrPython(filePath, acountNumber):
    filename = os.path.basename(filePath)
    acountChoose = acountNumber
    appid = ("1252842119", "1252805577", "1251351627", "1252869276")
    bucket = "tencentyun"
    secret_id = ("AKIDubZJrBQ9nCMHxOAUAakjSxFI7gz2RRnv", "AKIDtGB8C7ATgomZKu7NExeN6qrwqZRARbR7",
                 "AKIDxqY9ZnjhMp6C7qgjsqdEgx2xgEaknW7W", "AKID01rRkBYqpaKCyXiijXCeXK9ECGZoskNC")
    secret_key = (
    "2rSu77uSmrjOs9D1ZsujHZbOwEG3bstf", "iHcs6IJ1gPPG1b2E5qRwHRDvZ7mYDj8R", "LUREpEVpKeqsjOtCKGJDZnpfJl15FIxR",
    "GammX20f6ZBceiso44vUpV1HJ9j37zob")
    expired = time.time() + 2592000
    onceExpired = 0
    current = time.time()
    rdm = ''.join(random.choice("0123456789") for i in range(10))
    userid = "0"
    fileid = "tencentyunSignTest"

    info = "a=" + appid[acountChoose] + "&b=" + bucket + "&k=" + secret_id[acountChoose] + "&e=" + str(
        expired) + "&t=" + str(current) + "&r=" + str(rdm) + "&u=0&f="
    # print(info)
    secret_key_send = bytes(secret_key[acountChoose], 'latin-1')
    info = bytes(info, 'latin-1')
    signindex = hmac.new(secret_key_send, info, hashlib.sha1).digest()  # HMAC-SHA1加密
    sign = base64.b64encode(signindex + info)  # base64转码

    url = "http://recognition.image.myqcloud.com/ocr/general"
    headers = {'Host': 'recognition.image.myqcloud.com',
               "Authorization": sign,
               }
    files = {'appid': (None, appid[acountChoose]),
             'bucket': (None, bucket[acountChoose]),
             'image': ('', '', 'image/jpeg')
             }
    files['image'] = filename, open(filePath, 'rb'), 'image/jpeg'

    r = requests.post(url, files=files, headers=headers)
    responseinfo = r.content
    result_utf8 = responseinfo.decode('utf-8')

    # result_utf8=r'{"code":0,"message":"OK","data":{"recognize_warn_msg":[],"recognize_warn_code":[],"items":[{"itemcoord":{"x":153,"y":6,"width":40,"height":37},"words":[{"character":"好","confidence":0.9980360865592957}],"itemstring":"好"},{"itemcoord":{"x":31,"y":130,"width":131,"height":31},"words":[{"character":"不","confidence":0.9999659061431884},{"character":"愧","confidence":0.9998623132705689},{"character":"是","confidence":0.9999899864196776},{"character":"你","confidence":0.9999901056289672}],"itemstring":"不愧是你"}],"session_id":"1252842119-952963242","angle":1.1328125,"class":[]}}'
    # print(result_utf8)
    result_json = json.loads(result_utf8)

    result = ""

    tempfreq = 0.0
    tempstr = ""
    tempcount = 0

    for key, value in result_json.items():
        if (key == "data"):
            for key2, val2 in value.items():
                if (key2 == "items"):
                    for val3 in val2:
                        for key4, val4 in val3.items():
                            # 计算概率
                            if (key4 == "words"):
                                for val5 in val4:
                                    for key6, val6 in val5.items():
                                        if (key6 == "confidence"):
                                            tempfreq = tempfreq + val6
                                            tempcount = tempcount + 1
                            if (key4 == "itemstring"):
                                tempstr = val4
                        # 判决概率
                        if (tempcount != 0 and tempfreq / tempcount > 0.95):
                            result = result + tempstr
                        tempstr = ""
                        tempfreq = 0.0
                        tempcount = 0
    return filename, result


# filePath，acountNumber用于选择不同的上传账号 0金洪 1步顺 2苏子扬 3史一栋
def OCRandJieba(filePath, acountNumber):
    filename, ocrResult = ocrPython(filePath, acountNumber)
    jiebaResult = jiebaPython(ocrResult)
    return filename, ocrResult, jiebaResult