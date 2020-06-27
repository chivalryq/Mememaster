from selenium import webdriver
from bs4 import BeautifulSoup
import random
from time import  sleep
from selenium.webdriver.chrome.options import Options
def get_similar(img):
    options = Options()
    num = str(float(random.randint(500, 600)))
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/{}"
                         " (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/{}".format(num, num))
    # 禁止图片和css加载
    prefs = {'permissions.default.stylesheet': 2}
    options.add_experimental_option("prefs", prefs)
    # options.headless=True
    # chrome_options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(r'C:\Users\jnjga\OneDrive - business\桌面\university\meme_db\chromedriver.exe',options=options)
    driver.get('https://pic.sogou.com/')
    c = driver.find_element_by_class_name('camera-ico')
    c.click()
    p = driver.find_element_by_id('upload_pic_file')
    p.send_keys(img)
    sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    imgs = soup.select('.similar-box a img')
    similar_imgs = [img.get('src') for img in imgs]
    return similar_imgs


def main():
    img=r'C:\Users\jnjga\OneDrive - business\桌面\university\meme_db\SIFT\selenium\test.jpg'
    similar_imgs=get_similar(img)
    print(similar_imgs)

if __name__ == '__main__':
    main()