from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dhl_scrap.utils.dotdict import DotDict
from ruamel.yaml.comments import CommentedSeq
from selenium.webdriver.common.keys import Keys




import re
from scrapy.exceptions import IgnoreRequest

def Find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


def get_data_in_middleware_to_save(spider):
    try:
        if spider.get_data_in_middleware:
            for x in spider.get_data_in_middleware:
                dat = spider.driver.find_elements_by_xpath(spider.get_data_in_middleware[x])
                for i in dat:
                    try:
                        spider.middl_data[x].append(i.text)
                        # print(i.text)
                    except:
                        spider.middl_data[x].append(i)
                        # print(i)

    except:
        spider.logger.info('get_data_in_middleware is null or error')


    # try:
    #     if spider.url_refresh_quickly:
    #         content = spider.driver.page_source
    #         soup = BeautifulSoup(content, 'lxml')
    #         for x in spider.get_data_in_middleware_css:
    #             dat = soup.select(x)
    #             for i in dat:
    #                 spider.middl_data.append(i.get_text())
    #     else:
    #         for x in spider.get_data_in_middleware:
    #             dat = spider.driver.find_elements_by_xpath(x)
    #             for i in dat:
    #                 spider.middl_data.append(i.text)
    #
    # except:
    #     spider.logger.info('get_data_in_middleware error')

# 1th
def aims_html_get(aims_dict_or_list,request,spider):
    if type(aims_dict_or_list)== DotDict:
        exc_dict_find(aims_dict_or_list,request,spider)
    elif type(aims_dict_or_list)==CommentedSeq:
        exc_list_find(aims_dict_or_list,request,spider)
    else:
        spider.logger.info('conf aims error,please check it')
        return None


def exc_dict_find(aims_dict, request, spider):
    for aim in aims_dict:
        if aim != '$':
            try:
                WebDriverWait(spider.driver, 5).until(EC.element_to_be_clickable((By.XPATH, aim))).click()
                time.sleep(5)
            except:
                print('Positioning failed,the reason is :1,Non-target page .2,Positioning path is wrong.', aim)
                continue
        # if aim =='$':
        #     if aims_dict[aim][1]>0:
        #         aims_dict[aim][1]=aims_dict[aim][1]-1
        #         while aims_dict[aim][1]>0:
        #             try:
        #                 WebDriverWait(spider.driver, 5).until(EC.element_to_be_clickable((By.XPATH, aim))).click()
        #                 time.sleep(5)
        #                 spider.HTML=spider.HTML+'\n'+spider.driver.page_source
        #                 aims_dict[aim][1] = aims_dict[aim][1] - 1
        #             except:
        #                 print('Positioning failed,the reason is :1,Non-target page .2,Positioning path is wrong.', aim)
        #                 continue
        #     else:
        #         try:
        #             WebDriverWait(spider.driver, 5).until(EC.element_to_be_clickable((By.XPATH, aim))).click()
        #             time.sleep(5)
        #             spider.HTML = spider.HTML + '\n' + spider.driver.page_source
        #         except:
        #             print('Positioning failed,the reason is :1,Non-target page .2,Positioning path is wrong.', aim)
        #             continue


        if type(aims_dict[aim]) == CommentedSeq:
            exc_list_find(aims_dict[aim], request, spider)
        elif type(aims_dict[aim]) == DotDict:
            exc_dict_find(aims_dict[aim],request,spider)
        else:
            spider.logger.info('conf aims error,please check it')
            return None


def two_page_if_same(page_sour_1,page_sour_2):
    return page_sour_1==page_sour_2


def exc_list_find(aims_list,request,spider):
    spider.HTML=spider.HTML+'\n'+spider.driver.page_source
    pagesource = spider.driver.page_source
    if type(aims_list[1])==int and aims_list[1]>0:
        i = 1    # Stop sign
        while i < aims_list[1]:
            # if i==119:
            #     print(spider.middl_data)
            try:
                # Targeting or ajax requests (example: next page)
                try:
                    exc_each_click_get_data(spider)
                    try:
                        next_page=WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.LINK_TEXT,aims_list[0])))
                    except:
                        next_page=WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.XPATH,aims_list[0])))
                except :
                    break
                ActionChains(spider.driver).key_down(Keys.END).perform()
                time.sleep(2)
                next_page.click()
                time.sleep(5)
                exc_each_click_get_data(spider)
                spider.HTML = spider.HTML+'\n'+spider.driver.page_source
                i = i+1
                # print(i)
            except:
                spider.logger.info('conf aims_list[0] error,the reason is :1,Non-target page 2,Positioning path is wrong.:',aims_list[0])
                pass
    else:
        while 1:
            try:
                    # Targeting or ajax requests (example: next page)
                try:
                    exc_each_click_get_data(spider)
                    if aims_list[1]!=0:
                        try:
                            next_=spider.driver.find_elements_by_xpath(aims_list[1])
                            ss=next_[0].split(aims_list[2])
                            if ss[0]==ss[1]:
                                break
                        except:
                            content = spider.driver.page_source
                            soup = BeautifulSoup(content, 'lxml')
                            ss=soup.select(aims_list[1])
                            ss = ss[0].text.split(aims_list[2])
                            if ss[0]==ss[1] or ss[0]>ss[1]:
                                break


                    try:
                        next_page=WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.LINK_TEXT,aims_list[0])))
                    except:
                        next_page=WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.XPATH,aims_list[0])))
                except:
                    next_page=''
                ActionChains(spider.driver).key_down(Keys.END).perform()
                time.sleep(1)
                next_page.click()
                time.sleep(5)
                exc_each_click_get_data(spider)
            except:
                spider.logger.info('find over!')
                break


# 2th  Slider scroll to the lowest end, loading for all information
def scroll_to_the_end_get_data(spider):
    last_height = spider.driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        spider.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(3)
        # Calculate new scroll height and compare with last scroll height
        new_height = spider.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    exc_each_click_get_data(spider)


# Click on the final single data acquisition (No children level need to click)   url no change
def exc_each_click_get_data(spider):
    if spider.job_cfg.each_click:
        for cl in spider.job_cfg.each_click:
            try:
                elements = spider.driver.find_elements_by_xpath(cl)
                for i in elements:
                    i.click()
                    time.sleep(5)
                    get_data_in_middleware_to_save(spider)
                spider.HTML=spider.HTML+'\n'+spider.driver.page_source
            except:
                spider.logger.info('click over or Non-target url!')
                continue
    else:
        get_data_in_middleware_to_save(spider)



# 3th
def multi_level_mixing_click(spider,mult_click_path):
    if type(mult_click_path) == DotDict:
        for x in mult_click_path:
            first_path_click=spider.driver.find_elements_by_xpath(x)
            for click in first_path_click:
                click.click()
                time.sleep(5)
                if type(mult_click_path[x]) == DotDict:
                    multi_level_mixing_click(spider,mult_click_path[x])
                elif type(mult_click_path[x]) == CommentedSeq:
                    list_=mult_click_path[x]
                    if_click_each_get_data_and_next_page(spider,list_)
                else:
                    spider.logger.info('mult_click_path of conf error!')
                    pass
    elif type(mult_click_path) == CommentedSeq:
        if_click_each_get_data_and_next_page(spider,mult_click_path)
    else:
        spider.logger.info('mult_click_path of conf error!')


def if_click_each_get_data_and_next_page(spider,list_):
    next_page=1
    while next_page:
        try:
            try:
                next_page = WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.XPATH,list_[1])))  # list_[1]  next page
            except:
                next_page = WebDriverWait(spider.driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, list_[1])))  # list_[1]  next page
        except:
            next_page=''
            pass

        if list_[0]:
            exc_each_click_get_data(spider)
        else:
            spider.HTML = spider.HTML+'\n'+spider.driver.page_source
        if next_page!='':
            ActionChains(spider.driver).key_down(Keys.END).perform()
            time.sleep(2)
            next_page.click()
            time.sleep(5)


# 4th:change url
def each_click_in_new_url(spider,each_click_path):
    if type(each_click_path)==DotDict:
        for x in each_click_path:
            if x != '$':
                try:
                    spider.driver.find_element_by_xpath(x).click()
                except:
                    pass
                time.sleep(5)
                try:
                    if type(each_click_path[x])==DotDict:
                        each_click_in_new_url(spider,each_click_path[x])
                    elif type(each_click_path[x])==CommentedSeq:
                        list_=each_click_path[x]
                        get_change_url_html(spider,list_)
                    WebDriverWait(spider.driver,10).until(EC.element_to_be_clickable((By.XPATH,x))).click()
                    time.sleep(5)
                except:
                    continue
            else:
                list_=each_click_path[x]
                get_change_url_html(spider,list_)
    elif type(each_click_path)==CommentedSeq:
        get_change_url_html(spider,each_click_path)
    else:
        spider.logger.info('change_url of conf is error!')


def get_change_url_html(spider,list_):
    next_page=1
    while next_page:
        try:
            click_get_data=spider.driver.find_elements_by_xpath(list_[0])
            all_click=len(click_get_data)
            for i in range(all_click):
                spider.driver.find_elements_by_xpath(list_[0])[i].click()
                time.sleep(5)
                if spider.job_cfg.get_data_in_middleware:
                    get_data_in_middleware_to_save(spider)
                else:
                    spider.HTML=spider.HTML+'\n'+spider.driver.page_source
                spider.driver.back()
                time.sleep(5)
            try:
                try:
                    next_page=WebDriverWait(spider.driver,20).until(EC.element_to_be_clickable((By.LINK_TEXT,list_[1])))
                except:
                    next_page = WebDriverWait(spider.driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, list_[1])))


                ActionChains(spider.driver).key_down(Keys.END).perform()
                time.sleep(2)
                next_page.click()
                time.sleep(5)
            except:
                break

        except:
            next_page=''
            pass


def universal_model(spider,universal):
    get_data_in_middleware_to_save(spider)
    if type(universal[0])!=CommentedSeq:
        universal_first_is_not_list(spider,universal,universal[0])
    elif type(universal[0])==CommentedSeq:
        universal_first_is_list(spider,universal,universal[0])



def universal_first_is_list(spider,universal,universal_fir):
    if type(universal_fir)!=CommentedSeq:
        universal_first_is_not_list(spider,universal,universal_fir)
    elif type(universal_fir)==CommentedSeq:
        w_h=spider.driver.current_window_handle
        all_cl_1=spider.driver.find_elements_by_xpath(universal_fir[0])
        for t in range(len(all_cl_1)):
            spider.driver.switch_to.window(w_h)
            spider.driver.find_elements_by_xpath(universal_fir[0])[t].click()
            time.sleep(5)
            all_cl_2=spider.driver.find_elements_by_xpath(universal_fir[1])
            for a in range(len(all_cl_2)):
                try:
                    spider.driver.find_elements_by_xpath(universal_fir[1])[a].click()
                    time.sleep(5)
                    if len(universal_fir)==3:
                        all_cl_3 = spider.driver.find_elements_by_xpath(universal_fir[2])
                        for i in range(len(all_cl_3)):
                            try:
                                spider.driver.find_elements_by_xpath(universal_fir[2])[i].click()
                                time.sleep(5)
                                aim_url_do(spider, universal)
                            except:
                                pass
                    else:
                        aim_url_do(spider, universal)
                except:
                    pass


def universal_first_is_not_list(spider,universal,universal_first):
    if universal_first!= '$':
        all_tag_click = spider.driver.find_elements_by_xpath(universal_first)
        window_han = spider.driver.current_window_handle
        for x in range(len(all_tag_click)):
            try:
                click = spider.driver.find_elements_by_xpath(universal_first)[x]
                click.click()
                time.sleep(5)
                aim_url_do(spider, universal)
                try:
                    spider.driver.switch_to_window(window_han)
                except:
                    spider.driver.back()
            except:
                pass
    else:
        aim_url_do(spider, universal)


def aim_url_do(spider,universal):
    current_window_handle = spider.driver.current_window_handle
    if universal[1] == '$':
        next_page = 1
        while next_page < universal[3]:
            get_data_in_middleware_to_save(spider)
            spider.HTML = spider.driver.page_source
            try:
                try:
                    try:
                        next_page = spider.driver.find_element_by_xpath(universal[2])
                    except:
                        next_page = WebDriverWait(spider.driver, 20).until(
                            EC.element_to_be_clickable(
                                (By.LINK_TEXT, universal[2])))  ###################next page check
                    ActionChains(spider.driver).key_down(Keys.END).perform()
                    time.sleep(2)
                    next_page.click()
                    time.sleep(5)
                    next_page = next_page + 1
                except:
                    next_page = universal[3] + 1
            except:
                next_page = universal[3] + 1
                spider.logger.info('universal of conf is error!')
    else:
        next_page = 1
        curr_win_han=spider.driver.current_window_handle
        while next_page<universal[3]:
            try:
                all_aims_url = spider.driver.find_elements_by_xpath(universal[1])
                if spider.aim_url_in_new_windows:
                    # ActionChains(spider.driver).key_down(Keys.HOME).perform()

                    for i in range(len(all_aims_url)):
                        # ActionChains(spider.driver).key_down(Keys.DOWN).perform()
                        # time.sleep(1)
                        url_click = spider.driver.find_elements_by_xpath(universal[1])[i]
                        url_click.click()
                        time.sleep(10)
                        window_hands=spider.driver.window_handles
                        spider.driver.switch_to_window(window_hands[-1])
                        get_data_in_middleware_to_save(spider)
                        spider.HTML = spider.driver.page_source
                        spider.driver.close()
                        spider.driver.switch_to_window(curr_win_han)
                else:
                    ActionChains(spider.driver).key_down(Keys.HOME).perform()
                    time.sleep(1)
                    # current_window_handle = spider.driver.current_window_handle
                    for i in range(len(all_aims_url)):
                        # ActionChains(spider.driver).key_down(Keys.DOWN).perform()
                        # time.sleep(1)
                        # spider.driver.find_elements_by_xpath(universal[1])[i].click()
                        spider.driver.find_elements_by_xpath(universal[1])[i].click()
                        time.sleep(10)
                        # try:
                        #     iframe = spider.driver.find_element_by_xpath(universal[4])
                        #     spider.driver.switch_to.default_content()
                        #     spider.driver.switch_to.frame(iframe)
                        # except:


                        #     pass
                        get_data_in_middleware_to_save(spider)
                        spider.HTML = spider.driver.page_source
                        spider.driver.back()
                        time.sleep(10)
                        # try:
                        #     iframe = spider.driver.find_element_by_xpath(universal[5])
                        #     spider.driver.switch_to.default_content()
                        #     spider.driver.switch_to.frame(iframe)
                        # except:
                        #     pass

                try:
                    try:
                        next_page=spider.driver.find_element_by_xpath(universal[2])
                    except:
                        next_page = WebDriverWait(spider.driver, 20).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, universal[2])))###################next page check
                    ActionChains(spider.driver).key_down(Keys.END).perform()
                    time.sleep(2)
                    next_page.click()
                    time.sleep(5)
                    next_page=next_page+1
                except:
                    next_page = universal[3]+1
            except:
                next_page = universal[3]+1
                spider.logger.info('universal of conf is error!')




#5th
def js(spider,js):
    if js:
        stop=0
        while stop < js[5]:
            try:
                if js[0]=='tag':
                    iframe_ = spider.driver.find_element_by_tag_name(js[1])
                elif js[0]=='xpath':
                    iframe_ = spider.driver.find_element_by_xpath(js[1])
                elif js[0]=='css':
                    iframe_ = spider.driver.find_element_by_css_selector(js[1])
                else:
                    spider.logger.info('complex[1] is errorl or find over! please check it')
                    spider.HTML = spider.HTML+spider.driver.page_source
                    break
            except:
                spider.HTML=spider.HTML+spider.driver.page_source
                break
            if iframe_:
                spider.HTML = spider.HTML + spider.driver.page_source
                spider.driver.switch_to.default_content()
                spider.driver.switch_to.frame(iframe_)
            else:
                spider.HTML = spider.HTML+spider.driver.page_source
                spider.logger.info('iframe is null')
            if js[2]:# if click     path
                try:
                    clicks=spider.driver.find_elements_by_xpath(js[2])
                    window_handle=spider.driver.current_window_handle
                    ActionChains(spider.driver).key_down(Keys.HOME).perform()
                    time.sleep(2)
                    for x in range(len(clicks)):
                        time.sleep(2)
                        spider.driver.find_elements_by_xpath(js[2])[x].click()
                        time.sleep(3)
                        win_hands = spider.driver.window_handles
                        if js[3]:
                            while len(win_hands)<2:
                                spider.driver.switch_to_window(window_handle)
                                ActionChains(spider.driver).key_down(Keys.DOWN).perform()
                                time.sleep(2)
                                spider.driver.find_elements_by_xpath(js[2])[x].click()
                                time.sleep(3)
                                win_hands = spider.driver.window_handles
                            spider.driver.switch_to_window(win_hands[1])
                            time.sleep(3)
                            spider.HTML = spider.driver.page_source
                            get_data_in_middleware_to_save(spider)
                            spider.driver.close()
                            spider.driver.switch_to_window(window_handle)
                            time.sleep(1)
                        else:
                            spider.HTML = spider.HTML+spider.driver.page_source
                            get_data_in_middleware_to_save(spider)
                            spider.driver.back()
                            time.sleep(1)


                    if js[4]:#next page
                        try:
                            next_page = spider.driver.find_element_by_xpath(js[4])
                        except:
                            try:
                                next_page = spider.driver.find_element_by_css_selector(js[4])
                            except:
                                try:
                                    next_page = spider.driver.find_element_by_link_text(js[4])
                                except:
                                    spider.logger.info('complex[4] is errorl or find over! please check it')
                                    break
                        ActionChains(spider.driver).key_down(Keys.END).perform()
                        time.sleep(3)
                        next_page.click()
                        time.sleep(3)
                        stop=stop+1
                    else:
                        stop=10+js[5]
                except:
                    spider.logger.info('click is error')
            else:
                spider.HTML=spider.HTML+spider.driver.page_source
                get_data_in_middleware_to_save(spider)
                if js[4]: #next page
                    try:
                        next_page = spider.driver.find_element_by_xpath(js[4])
                    except:
                        try:
                            next_page = spider.driver.find_element_by_css_selector(js[4])
                        except:
                            try:
                                next_page = spider.driver.find_element_by_link_text(js[4])
                            except:
                                spider.logger.info('complex[4] is errorl or find over! please check it')
                                break

                    ActionChains(spider.driver).key_down(Keys.END).perform()
                    time.sleep(3)
                    next_page.click()
                    time.sleep(3)
                    stop=stop+1
                else:
                    stop=10+js[5]
    else:
        spider.HTML =spider.HTML+spider.driver.page_source



class PhantomJSMiddleware(object):

    def process_request(self, request, spider):
        if spider.get_data_in_middleware:
            for x in spider.get_data_in_middleware:
                spider.middl_data[x]=[]
        spider.driver.get(request.url)
        time.sleep(5)
        spider.HTML=''
        if spider.job_cfg.aims:
            exc_each_click_get_data(spider)
            aims_html_get(spider.job_cfg.aims, request,spider)
            html=spider.HTML
            current_url=spider.driver.current_url
            # spider.job_cfg.aims=False    # ##########下面不再需要 也可去掉
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        elif spider.job_cfg.scroll:
            scroll_to_the_end_get_data(spider)
            html=spider.driver.page_source
            current_url = spider.driver.current_url
            # spider.job_cfg.scroll=False    # ##########下面不再需要  也可去掉
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        elif spider.job_cfg.mult_click_path:
            multi_level_mixing_click(spider,spider.job_cfg.mult_click_path)
            html=spider.HTML
            current_url = spider.driver.current_url
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        elif spider.job_cfg.change_url:
            each_click_in_new_url(spider,spider.job_cfg.change_url)
            html=spider.HTML
            current_url = spider.driver.current_url
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        elif spider.job_cfg.universal:
            universal_model(spider,spider.job_cfg.universal)
            html = spider.HTML
            current_url = spider.driver.current_url

            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        elif spider.job_cfg.js:
            js(spider,spider.job_cfg.js)
            html=spider.HTML
            current_url = spider.driver.current_url
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)
        else:
            html = spider.driver.page_source
            current_url = spider.driver.current_url
            # spider.driver.close()
            return HtmlResponse(url=current_url, encoding='utf-8', body=html, request=request)


class UrlSaveMiddleware(object): #TODO

    def process_request(self, request, spider):
        if request.url == str(spider.start_urls[0]):
            return None
        else:
            if spider.filter_url.request_seen(request):
                raise IgnoreRequest()
            else:
                return None









# class MultClickMiddleware(object):
#
#     def process_request(self,request, spider):
#         if spider.job_cfg.mult_click_path:
#             multi_level_mixing_click(spider,spider.job_cfg.mult_click_path)
#             html=spider.HTML
#             return HtmlResponse(url=spider.driver.current_url, encoding='utf-8', body=html, request=request)

# class JsScrollMiddleware(object):
#
#     def process_request(self,request, spider):
#         if spider.job_cfg.scroll:
#             spider.driver.get(request.url)
#             scroll_to_the_end_get_data(spider)
#             html=spider.driver.page_source
#             spider.job_cfg.scroll=False    ###########下面不再需要
#             return HtmlResponse(url=spider.driver.current_url, encoding='utf-8', body=html, request=request)

    # @classmethod
    # def process_response(cls, response, spider):


