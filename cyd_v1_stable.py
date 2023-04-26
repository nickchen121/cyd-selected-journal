#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
B站搜索，UID383551518，水论文的程序猿，
主页链接更多视频工具: https://space.bilibili.com/383551518

 **个人开发，供粉丝、同学免费使用，盗版侵权必究（传播时功德箱替换图片必定深究）**
"""
import io
import json
import os
import re
import time
import tkinter as tk
from urllib.request import urlopen
import requests
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import urllib

browserType = webdriver.Chrome


class BaiduXueshuAutomatic:

    def __init__(self, chrome_driver_path: str) -> None:
        self.chrome_driver_path = chrome_driver_path
        self.browser: browserType
        self._init_browser()

    def _init_browser(self) -> None:
        options = Options()
        # options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(executable_path=self.chrome_driver_path,
                                        options=options)
        self.browser.implicitly_wait(3)
        self.wait = WebDriverWait(self.browser, 15)
        self.ac = ActionChains(self.browser)

    def _wait_by_xpath(self, patten):
        self.wait.until(EC.presence_of_element_located((By.XPATH, patten)))

    def is_contain_chinese(self, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def run(self, wd, page_num=999, year=2018, fpath='result.txt', pos=0):

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }

        first_paper = ''
        count = 0
        paper_count = 0
        con_count = 0
        chinese_count = 0
        english_count = 0

        all_dic = {'all_paper_num': 0,
                   'English Journal': {},
                   'Chinese Journal': {},
                   'Conference': {},
                   }

        while count <= page_num:
            if pos == 0:
                url = f'https://xueshu.baidu.com/s?wd=intitle:{wd}&pn={count}0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&filter=sc_year%3D%7B{year}%2C%2B%7D&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&bcp=2&sc_hit=1'
            elif pos == 1:
                url = f'https://xueshu.baidu.com/s?wd={wd}&pn={count}0&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&filter=sc_year%3D%7B{year}%2C%2B%7D&sc_f_para=sc_tasktype%3D%7BfirstAdvancedSearch%7D&bcp=2&sc_hit=1'
            else:
                print('别瞎搞，检索词只能是位于标题或者文章内，只能填0或1，按ctrl+c终止终端可重新查询\n')
                return

            url= urllib.request.quote(url, safe=";/?:@&=+$,", encoding="utf-8")

            try:
                self.browser.get(url)
            except:
                print(f'谷歌浏览器被异常关闭，按ctrl+c终止终端可重新进入软件点击运行\n')
                time.sleep(5)
                continue


            print(f'百度学术搜索第{count + 1}页（无搜索结果可以复制粘贴链接去浏览器查看）:\n {url}\n')
            time.sleep(1)

            # 课程学习内部
            try:
                first_urls = self.browser.find_elements_by_xpath(
                    '/html/body/div[1]/div[4]/div[3]/div[2]/div/div[@class="result sc_default_result xpath-log"]')
            except:
                print('请检查软件打开的浏览器被人为（异常）终止，是的话，按ctrl+c，重新运行软件，期间不要关闭浏览器。\n')
                continue

            if not first_urls:
                print(f'没有搜索结果，提前结束，按ctrl+c终止终端可重新查询\n')
                with open(fpath, 'w', encoding='utf8') as fw:
                    fw.write(json.dumps(all_dic, ensure_ascii=False))
                    fw.flush()
                return

            for ii, first_url in enumerate(first_urls):

                if count == 0 and ii == 0:
                    with open(fpath, 'w', encoding='utf8') as fw:
                        fw.write(json.dumps(all_dic, ensure_ascii=False))
                        fw.flush()
                else:
                    with open(fpath, 'r', encoding='utf8') as fr:
                        all_dic = json.loads(fr.read())
                try:
                    paper_name = first_url.find_element_by_xpath('div[1]/h3/a')
                    paper_link = paper_name.get_attribute("href")
                    paper_name = paper_name.text
                except:
                    print('请检查软件打开的谷歌浏览器是否被人为（异常）终止，程序运行期间不要关谷歌闭浏览器，谢谢配合。\n')
                    break

                if paper_link == first_paper:
                    count = 9999
                    break

                if ii == 0:
                    first_paper = paper_link

                try:
                    res1 = requests.get(paper_link, headers=headers).text
                except:
                    print(f'百度禁掉了你的网络，等一会，按ctrl+c终止终端可重新查询\n')
                    time.sleep(5)
                    continue

                journal_name = re.findall('<a class="journal_title".*?>(.*?)</a>', res1, re.S)

                if not journal_name:
                    continue
                journal_name = journal_name[0]

                paper_count += 1

                print(f'第{paper_count}篇论文')

                if ': ' in journal_name:
                    journal_name = journal_name.split(': ')[0]

                if '&amp;' in journal_name:
                    journal_name = journal_name.replace('&amp;', '&')

                if '&#039;' in journal_name:
                    journal_name = journal_name.replace('&#039;', "'")

                if self.is_contain_chinese(journal_name):
                    print("Chinese journal don't check.")

                    journal_name = f'{journal_name}'
                    print(paper_name)
                    print(paper_link)
                    print(journal_name)
                    print('\n')

                    if not all_dic['Chinese Journal'].get(journal_name):
                        all_dic['Chinese Journal'][journal_name] = []

                    all_dic['Chinese Journal'][journal_name].append({paper_name: paper_link})

                    chinese_count += 1

                    all_dic['all_paper_num'] = {
                        'all_count': paper_count,
                        'English Journal count': english_count,
                        'Chinese Journal count': chinese_count,
                        'Conference count': con_count
                    }

                    for i in list(all_dic['Chinese Journal'].keys()):
                        if '共' in all_dic['Chinese Journal'][i][0]:
                            all_dic['Chinese Journal'][i][0] = f'共{len(all_dic["Chinese Journal"][i])-1}篇'
                        else:
                            all_dic['Chinese Journal'][i].insert(0, f"共1篇")

                    all_dic['Chinese Journal'] = {key: all_dic['Chinese Journal'][key] for key, value in
                                                  sorted(all_dic['Chinese Journal'].items(), key=lambda x: x[1][0],
                                                         reverse=True)}

                    all_dic = json.dumps(all_dic, ensure_ascii=False)
                    with open(fpath, 'w', encoding='utf8') as fw:
                        fw.write(all_dic)
                        fw.flush()

                    time.sleep(2)
                    continue

                if 'Conference' in journal_name:
                    print("Conference don't check.")

                    journal_name = f'{journal_name}'
                    print(paper_name)
                    print(paper_link)
                    print(journal_name)
                    print('\n')

                    if not all_dic['Conference'].get(journal_name):
                        all_dic['Conference'][journal_name] = []

                    all_dic['Conference'][journal_name].append({paper_name: paper_link})

                    con_count += 1

                    all_dic['all_paper_num'] = {
                        'all_count': paper_count,
                        'English Journal count': english_count,
                        'Chinese Journal count': chinese_count,
                        'Conference count': con_count
                    }

                    for i in list(all_dic['Conference'].keys()):
                        if '共' in all_dic['Conference'][i][0]:
                            all_dic['Conference'][i][0] = f'共{len(all_dic["Conference"][i])-1}篇'
                        else:
                            all_dic['Conference'][i].insert(0, f"共1篇")

                    all_dic['Conference'] = {key: all_dic['Conference'][key] for key, value in
                                             sorted(all_dic['Conference'].items(), key=lambda x: x[1][0], reverse=True)}

                    all_dic = json.dumps(all_dic, ensure_ascii=False)
                    with open(fpath, 'w', encoding='utf8') as fw:
                        fw.write(all_dic)
                        fw.flush()

                    time.sleep(2)
                    continue

                status_code = True
                cite_score = ''
                journal_split = ''
                journal_date = ''

                while status_code:
                    try:
                        post_dic = {'searchname': journal_name, 'searchsort': 'relevance'}
                        search_url = 'http://www.letpub.com.cn/index.php?page=journalapp&view=search'
                        res = requests.post(search_url, post_dic, headers=headers)
                    except:
                        print(f'letpub禁掉了你的网络，等一会，按ctrl+c终止终端可重新查询')
                        time.sleep(5)
                        continue

                    if res.status_code == 200:
                        status_code = False
                    else:
                        print(f'letpub禁掉了你的网络，等一会，{journal_name}')
                        time.sleep(5)
                        continue

                    second_search = re.findall('</style>.*?<tr>(.*?)</tr>', res.text, re.S)[0]
                    cite_score = re.findall('CiteScore:(\d+.\d+)', second_search, re.S)
                    journal_split = re.findall('(\d区)</td>', second_search, re.S)

                    journal_date = ''
                    fourth_search = re.findall('(<td.*?</td>)', second_search, re.S)
                    for i in fourth_search:
                        l = ['月', '周', 'eeks']
                        for j in l:
                            if j in i:
                                journal_date = re.findall('>(.*?)</td>', i, re.S)
                                break

                if cite_score and journal_split and journal_date:
                    journal_name = f'{journal_split[0]} Citescore:{cite_score[0]} 审稿周期:{journal_date[0]} {journal_name}'
                elif cite_score and journal_split:
                    journal_name = f'{journal_split[0]} Citescore:{cite_score[0]} 审稿周期:无记录 {journal_name}'
                elif cite_score:
                    journal_name = f'未收录 Citescore:{cite_score[0]} 审稿周期:无记录 {journal_name}'
                else:
                    journal_name = f'未收录 无Citescore 审稿周期:无记录 {journal_name}'

                print(paper_name)
                print(paper_link)
                print(journal_name)
                print('\n')

                if not all_dic['English Journal'].get(journal_name):
                    all_dic['English Journal'][journal_name] = []

                all_dic['English Journal'][journal_name].append({paper_name: paper_link})

                english_count += 1

                all_dic['all_paper_num'] = {
                    'all_count': paper_count,
                    'English Journal count': english_count,
                    'Chinese Journal count': chinese_count,
                    'Conference count': con_count
                }

                all_dic['English Journal'] = {key: all_dic['English Journal'][key] for key in
                                              sorted(all_dic['English Journal'].keys())}

                for i in list(all_dic['English Journal'].keys()):
                    if '共' in all_dic['English Journal'][i][0]:
                        all_dic['English Journal'][i][0] = f'共{len(all_dic["English Journal"][i])-1}篇'
                    else:
                        all_dic['English Journal'][i].insert(0, f"共1篇")

                all_dic = json.dumps(all_dic, ensure_ascii=False)
                with open(fpath, 'w', encoding='utf8') as fw:
                    fw.write(all_dic)
                    fw.flush()

                time.sleep(5)
            count += 1

        print('成功获取所有期刊，成功使用记得打赏哦，谢谢！~')
        return 0


root = tk.Tk()
root.geometry('1200x850')
root.title('cyd的百宝箱，B站搜索，UID383551518，水论文的程序猿')


def wd_split_dou(wd, num=1):
    wd_new = ''
    if ',' in wd:
        wd_lis = wd.split(',')
    elif '，' in wd:
        wd_lis = wd.split('，')
    else:
        # if '+' in wd:
        #     wd=wd.replace('+','%2B')
        # elif ' ' in wd:
        #     wd=wd.replace('+','%20')

        return f'("{wd}")'


    if num == 1:
        for i in range(len(wd_lis)):
            # if '+' in wd_lis[i]:
            #     wd_lis[i]=wd_lis[i].replace('+', '%2B')
            # elif ' ' in wd_lis[i]:
            #     wd_lis[i]=wd_lis[i].replace(' ', '%20')

            if i == 0:
                wd_new = f'"{wd_lis[i].strip()}"'
            else:
                wd_new = wd_new + ' + '+ f'"{wd_lis[i].strip()}"'

    elif num == 2:
        wd_lis.reverse()
        for i in range(len(wd_lis)):
            # if '+' in wd_lis[i]:
            #     wd_lis[i]=wd_lis[i].replace('+', '%2B')
            # elif ' ' in wd_lis[i]:
            #     wd_lis[i] = wd_lis[i].replace(' ', '%20')

            if i == 0:
                wd_new = wd_lis[i].strip()
            else:
                wd_new = wd_new + ' | '+ wd_lis[i].strip()

    return f'({wd_new})'


# 按扭调用的函数，
def reg():
    wd1 = e_keyword1.get()
    wd2 = e_keyword2.get()

    if wd1:
        wd = wd_split_dou(wd1, num=1)
    elif wd2:
        wd = wd_split_dou(wd2, num=2)
    else:
        wd = '("video+captioning")'



    pos = e_pos.get()
    if pos:
        pos = int(pos)
    else:
        pos = 0

    year = e_year.get()
    if not year:
        year = '2018'

    chrome_driver_path = e_path1.get()
    chrome_driver_path = fr'{chrome_driver_path}'
    if not chrome_driver_path:
        dir = os.path.dirname(os.path.abspath(__file__))
        chrome_driver_path = os.path.join(dir, 'chromedriver')
    else:
        chrome_driver_path = os.path.join(chrome_driver_path, 'chromedriver')

    now_time = str(time.strftime("%H_%M_%S", time.localtime(time.time())))
    fpath = e_fpath2.get()
    fpath = fr'{fpath}'

    print(f'\n如果路径无用，检查路径，{fpath}是否存在\n')
    if not fpath:
        dir = os.path.dirname(os.path.abspath(__file__))
        fpath = os.path.join(dir, f'result_{now_time}.txt')
        # fpath = os.path.join(chrome_driver_path, f'result_{now_time}.txt')
    else:
        fpath = os.path.join(fpath, f'result_{now_time}.txt')

    page_num = 999
    try:
        d = BaiduXueshuAutomatic(chrome_driver_path=chrome_driver_path)
    except Exception as e:
        print(f'{chrome_driver_path} 目录下没有chromedriver\n')
        print('停止运行，请看软件视频（文本）使用指南，下载（更新）谷歌浏览器，并配置chromedriver的正确路径\n')
        print(f'错误信息：{e}\n')
        return

    time.sleep(1)
    try:
        code = d.run(wd, page_num, year, fpath, pos)
        if code == 0:
            l_msg['text'] = '成功获取所有期刊，成功使用记得打赏哦，谢谢！~\n'
        else:
            l_msg['text'] = f'异常终止，如果是手动强制停止请忽视\n'
    except KeyboardInterrupt:
        print('手动终止，可以前往软件重新输入检索词，重新运行软件\n')

l_1 = tk.Label(root, text='B站主页链接更多视频工具（点击链接可复制）\n **个人开发，供粉丝/同学免费使用，侵权盗版必究**\n')
l_1.config(fg='blue')
l_1.grid(row=0, sticky=tk.W)

l_7 = tk.Text(root, height=1)
l_7.grid(row=0, column=1, sticky=tk.W)
l_7.insert('1.0', 'https://space.bilibili.com/383551518')
# l_7.config(font=20)

l_keyword1 = tk.Label(root, text='包含精确检索词\n(多个检索词以逗号，分隔）：')
l_keyword1.grid(row=1, sticky=tk.W)
e_keyword1 = tk.Entry(root)
e_keyword1.grid(row=1, column=1, sticky=tk.W)

l_keyword2 = tk.Label(root, text='包含至少一个检索词\n(多个检索词以逗号，分隔）：')
l_keyword2.grid(row=2, sticky=tk.W)
e_keyword2 = tk.Entry(root)
e_keyword2.grid(row=2, column=1, sticky=tk.W)

l_pos = tk.Label(root, text='出现检索词的位置在\n（输入0为位于标题，默认为0\n输入1为位于文章任何位置）')
l_pos.grid(row=3, sticky=tk.W)
e_pos = tk.Entry(root)
e_pos.grid(row=3, column=1, sticky=tk.W)

l_year = tk.Label(root, text='多少年之后\n（默认2018年之后）：')
l_year.grid(row=4, sticky=tk.W)
e_year = tk.Entry(root)
e_year.grid(row=4, column=1, sticky=tk.W)

l_path1 = tk.Label(root, text='chromedriver保存的文件夹地址 \n（****必填****）：')
l_path1.grid(row=5, sticky=tk.W)
e_path1 = tk.Entry(root)
e_path1.grid(row=5, column=1, sticky=tk.W)

l_fpath2 = tk.Label(root, text='结果文件存放的文件夹地址 \n（****必填****）：')
l_fpath2.grid(row=6, sticky=tk.W)
e_fpath2 = tk.Entry(root)
e_fpath2.grid(row=6, column=1, sticky=tk.W)


b_l = tk.Label(root, text='程序启动后不要关掉谷歌浏览器\n关掉它程序会立马停止')
b_l.config(fg='red',font=18)
b_l.grid(row=7, sticky=tk.W)
b_login = tk.Button(root, text='点击运行软件（运行期间程序会假死，终端会打印结果，ctrl+c 关闭终端运行即恢复）', command=reg)
b_login.grid(row=7, column=1, sticky=tk.W)
b_login.config(fg='red')

l_5 = tk.Label(root, text='')
l_5.grid(row=8, sticky=tk.W)

l_6 = tk.Label(root, text='程序制作不易\n可前往功德箱自行打赏')
l_6.grid(row=9, sticky=tk.W)
l_6.config(fg='blue')

# 保护区
#########################################################################
########################################################################
#######################################################################
## 软件传播时功德箱图片不可替换，如有替换，必定深究#############################
url = "https://imgmd.oss-cn-shanghai.aliyuncs.com/gongde2.jpg"########
#####################################################################
####################################################################
###################################################################

image_bytes = urlopen(url).read()
data_stream = io.BytesIO(image_bytes)
pil_image = Image.open(data_stream)
w, h = pil_image.size
fname = url.split('/')[-1]
tk_image = ImageTk.PhotoImage(pil_image)
label6 = tk.Label(root, image=tk_image, bg='brown')
label6.grid(row=9, column=1, sticky=tk.W)

l_88 = tk.Label(root, text='')
l_88.grid(row=10, sticky=tk.W)

l_66 = tk.Label(root, text='使用前一定要看视频(文本)指南!!!')
l_66.grid(row=11, sticky=tk.W)
l_66.config(fg='red',font=15)

l_66 = tk.Label(root, text='使用指南视频链接（点击链接可复制）：')
l_66.grid(row=12, sticky=tk.W)
l_7 = tk.Text(root, height=1)
l_7.grid(row=12, column=1, sticky=tk.W)
l_7.insert('1.0', 'https://www.bilibili.com/video/BV1TP411U7P8')
# l_7.config(font=18)

l_66 = tk.Label(root, text='使用指南文本下载链接（点击链接可复制）：')
l_66.grid(row=13, sticky=tk.W)
l_7 = tk.Text(root, height=1)
l_7.grid(row=13, column=1, sticky=tk.W)
l_7.insert('1.0', 'https://imgmd.oss-cn-shanghai.aliyuncs.com/qikan-sousuo-zhinan.pdf')
# l_7.config(font=20)

l_66 = tk.Label(root, text='软件问题汇总及解决方法(实时更新)：')
l_66.grid(row=14, sticky=tk.W)
l_7 = tk.Text(root, height=1)
l_7.grid(row=14, column=1, sticky=tk.W)
l_7.insert('1.0', 'https://imgmd.oss-cn-shanghai.aliyuncs.com/xk-problem-sum.pdf')
# l_7.config(font=20)



l_msg = tk.Label(root, text='')
l_msg.grid(row=15)
l_msg.config(fg='red', font=35)


root.mainloop()


