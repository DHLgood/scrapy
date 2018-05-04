# -*- coding: utf-8 -*-
import sys
import os
import socket
from scrapy.crawler import CrawlerProcess
from dhl_scrap.spiders.faq_spider import FaqSpider
from dhl_scrap.spiders.product_description_spider import ComplexWebSpider,ProductDescriptionSpider
from dhl_scrap.spiders.js_spider import JS_spider
from scrapy.utils.project import get_project_settings


process = CrawlerProcess(get_project_settings()) #加载项目设置
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
# project dir




project_dir=os.path.dirname(os.path.abspath(__file__))


# product_description_files_dir=project_dir+'/opt/dhl/conf/product_description'
# product_description_files_list_path=os.listdir(product_description_files_dir)
#
# faq_files_dir=project_dir+'/opt/dhl/conf/faq_conf'
# faq_files_list_path=os.listdir(faq_files_dir)
#
# complex_target_div_web_files_dir=project_dir+'/opt/dhl/conf/complex_target_div_web'
# complex_target_div_web_files_list_path=os.listdir(complex_target_div_web_files_dir)
#
#
#
# static
# for filename_path in product_description_files_list_path:
#     process.crawl(ProductDescriptionSpider,config_path=product_description_files_dir+'/'+filename_path,save_dir=project_dir+'/'+'opt/data/crawl_results/production')
#
# for filename_path in faq_files_list_path:
#     process.crawl(FaqSpider,config_path=faq_files_dir+'/'+filename_path,save_dir=project_dir+'/'+'opt/data/crawl_results/faq')
#
# for filename_path in complex_target_div_web_files_list_path:
#     process.crawl(ComplexWebSpider,config_path=complex_target_div_web_files_dir+'/'+filename_path,save_dir=project_dir+'/'+'opt/data/crawl_results/complex')




#dynamic
js_div_web_files_dir=project_dir+'/opt/dhl/conf/js_conf'
js_div_web_files_list_path=os.listdir(js_div_web_files_dir)




for filename_path in js_div_web_files_list_path:
    process.crawl(JS_spider,config_path=js_div_web_files_dir+'/'+filename_path,save_dir=project_dir+'/'+'opt/data/crawl_results/js')




process.start()


print('--------------------------------------spider closed------------------------------------------------')



















#
#
#
#
#
#

# #
# from scrapy.cmdline import execute
# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# # # execute(["scrapy", "crawl", "product_description_spider"])
# execute(["scrapy", "crawl", "js_spider"])
# # # execute(["scrapy", "crawl", "faq_spider"])
# # execute(["scrapy", "crawl", "complex_web_spider"])
# # #
# #
#
