import numpy as np
import cv2 as cv
import os
import time

from ..settings import  IMAGE_FOLDER


def get_mask(polluted_image,start_x,start_y,end_x,end_y,black_thresold):

    if (end_x < start_x):#异常处理
        start_x = start_x + end_x#交换两个数值
        end_x = start_x - end_x
        start_x = start_x - end_x

    if (end_y < start_y):#异常处理
        start_y = start_y + end_y#交换两个数值
        end_y = start_y - end_y
        start_y = start_y - end_y

    polluted_clone = np.zeros(polluted_image.shape,dtype=np.uint8)#原图片拷贝
    mask_img = np.zeros(polluted_image.shape[:2],dtype=np.uint8)#蒙版图片，用于计算直方图
    polluted_clone = polluted_image.copy()
    for x in range(start_x,end_x):#蒙版图片赋值
        for y in range(start_y,end_y):
            mask_img[y][x] = 255#矩阵行列定义与x,y轴定义相反
    
    #确定阈值
    polluted_clone = cv.cvtColor(polluted_clone,cv.COLOR_BGR2GRAY)#转为灰度图
    thresold = get_thresold(polluted_clone,mask_img,black_thresold)
    print("确定的阈值",thresold)

    if thresold < 255/2:
        flag = cv.THRESH_BINARY_INV#黑字处理方式
    else:
        flag = cv.THRESH_BINARY#白字处理方式

    #-------二值化，获取蒙版图片
    result = np.zeros(polluted_image.shape[:2],dtype=np.uint8)
    _,thresold_img = cv.threshold(polluted_clone,thresold,255,flag)
    #-----膨胀处理
    kernel_width =  int((end_x - start_x) / 33) #根据圈定范围决定膨胀核的体积，这是经验公式
    if (kernel_width <3):
        kernel_width  = 2
        kernel_height = 2
    elif (kernel_width >11):
        kernel_width  = 11
        kernel_height = 10
    else:
        kernel_height = kernel_width -1
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (kernel_width,kernel_height))  # 膨胀核矩形结构
    thresold_img = cv.dilate(thresold_img, kernel)#对Mask膨胀处理
    for x in range(start_x,end_x):
        for y in range(start_y,end_y):
            result[y][x] = thresold_img[y][x]#矩阵行列定义与x,y轴定义相反
    return result


def get_thresold(grey_img,mask_img,black_thresold):#使用直方图的方式获取文字颜色，进而获取阈值
    hist = cv.calcHist([grey_img],[0],mask_img,[256],[0,256])
    lightness = cal_avg_lightness(grey_img)
    if lightness < black_thresold:#背景色是黑色
        font_color_index = 200 + np.argmax(hist[200:])#寻找文字颜色(白色)
        
        i = font_color_index
        while i > 122:#从边缘向中间寻找阈值,低于1/2即可认为是阈值
            if hist[i] < hist[font_color_index] * 0.25:
                break
            else:
                i = i - 1
        return i
    else:
        font_color_index = np.argmax(hist[:122])#寻找文字颜色(黑色)
        i = font_color_index
        while i < 123:#从边缘向中间寻找阈值,低于1/2即可认为是阈值
            if hist[i] < hist[font_color_index] * 0.25:
                break
            else:
                i = i + 1
        return i
        







def cal_avg_lightness(grey_img):
    result = np.average(grey_img.reshape(grey_img.shape[0]*grey_img.shape[1],1)) * 0.8
    print("平均亮度值:",result)
    return result



def get_inpaint_image(img_path,start_x,start_y,end_x,end_y,black_thresold = 124.0):#img_path 
#原图路径,start_x,start_y,end_x,end_y 文字框选区域的两个端点坐标 black_thresold 判断文字属于黑色字还是浅色字，该值越大，越倾向于将文字判断为浅色字
# 返回值 save_path 去除后的路径 -1 源文件不存在 -2 写入生成好的文件失败 -3参数不正确
    if os.path.exists(img_path) == False:
        return -1
    
    raw = cv.imread(img_path,1)
    if (start_x < 0) or (start_x > raw.shape[1]):
        return -3
    if (start_y < 0) or (start_y > raw.shape[0]):
        return -3
    if (end_x < 0) or (end_x > raw.shape[1]):
        return -3
    if (end_y < 0) or (end_y > raw.shape[0]):
        return -3
    draw_pic = np.zeros(raw.shape,dtype=np.uint8)
    draw_pic = raw.copy()
    mask_img = get_mask(raw,start_x,start_y,end_x,end_y,black_thresold)#获得掩膜图片
    dst = cv.inpaint( raw,mask_img,9,cv.INPAINT_TELEA)
    dst = cv.medianBlur(dst, 5)#去除椒盐噪声，主要是由于清理不干净造成的
    result = np.zeros(raw.shape,dtype=np.uint8)
    result = raw.copy()
    for x in range(start_x,end_x):#去燥图片与原图合成
        for y in range(start_y,end_y):
            for z in range(0,3):
                result[y][x][z] = dst[y][x][z]#矩阵行列定义与x,y轴定义相反
    # save_path = 'static/img/' + 'inpaint' + str(time.time())+ '.jpg'
    save_path = os.path.join(IMAGE_FOLDER, "inpaint"+str(time.time()) + '.jpg')
    cv.imwrite(save_path,result)
    if os.path.exists(save_path):#异常处理
        return save_path
    else:
        return -2

