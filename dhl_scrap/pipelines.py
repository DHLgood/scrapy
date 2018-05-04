import os
import logging
from scrapy.exceptions import DropItem
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
import json
from scrapy.http import HtmlResponse

from .utils.data_utils import rename_if_exists, stringify_http_headers
from datetime import datetime
import time
from scrapy.spiders import  Request




class CrawlSummaryPipeline(object):
    """Capture summary information of this page crawl (request, response, etc)

    """

    def process_item(self, item, spider):
        response = item.get("response", None)

        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)

        # 1. request summary
        item["request_summary"] = {
            "url": response.request.url,
            "method": response.request.method,
            "headers": stringify_http_headers(response.request.headers),
        }

        # 2. request summary
        item["response_summary"] = {
            "url": response.url,
            "status": response.status,
            "headers": stringify_http_headers(response.headers),
        }

        # 3. crawling meta and flags
        item["crawl_meta"] = response.meta
        item["crawl_flags"] = response.flags

        spider.logger.debug("Added crawl summary data into the item %s" % item)

        return item


class JsFilterPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)

        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)

        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))

        url = response.url
        if isinstance(response, HtmlResponse):
            html = response.text

            spider.logger.debug("Processing JS filter for item: %s", url)
            soup = BeautifulSoup(html, 'lxml')
            for script in soup(["script", "style"]):
                script.extract()
            item["html_processed"] = soup.text

        return item


def _save_html_path(base_dir, url):
    url_parsed = urlparse(url)

    domain_base_dir = url_parsed.netloc.replace(':', "_")
    save_dir = os.path.join(base_dir, domain_base_dir)

    inner_path = url_parsed.path

    if len(inner_path) > 0 and inner_path[0] == '/':
        inner_path = inner_path[1:].replace('/','')

    if len(inner_path) == 0:
        inner_path = "html.html"

    if inner_path[-1] == '/':
        inner_path = inner_path[:-1]

    inner_path_lower = inner_path.lower()
    if not inner_path_lower.endswith(".html") and not inner_path_lower.endswith(".htm"):
        inner_path = inner_path + ".html"

    # play safe
    time.sleep(1)
    inner_path = quote(inner_path+datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

    return rename_if_exists(os.path.join(save_dir, inner_path))


class RemoveResponsePipeline(object):

    def process_item(self, item, spider):

        # Object is not serializable so take it out, otherwise exception
        if "response" in item:
            del item["response"]

        return item


class SaveHtmlPipeline(object):
    """Assume it is raw HTML

    """

    def process_item(self, item, spider):
        response = item.get("response", None)

        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)

        if isinstance(response, HtmlResponse):
            # assume spider has this field
            h_save_dir = os.path.join(spider.save_dir, "html")

            save_path = _save_html_path(h_save_dir, response.url)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                try:
                    f.write(response.text)
                    spider.logger.info("Saved %s to %s" % (response.url, save_path))
                except IOError:
                    spider.logger.error(
                        "Error thrown when writing html file %s to %s" % (response.url, save_path),
                        exc_info=True)

        return item


class ExtractTargetDivPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)

        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)

        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))

        # assume spider has this field
        h_save_dir = os.path.join(spider.save_dir, "extracted")

        save_path = _save_html_path(h_save_dir, response.url) + ".json"

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            try:
                if hasattr(spider, "target_div"):
                    div_id = spider.target_div
                    if div_id[0] != '#':
                        div_id = '#' + div_id

                    # 1. bs text target div
                    for content in BeautifulSoup(response.text, "lxml").select(div_id):
                        item["bs_target_div"] = content.text

                    # 2. json target div
                    item["css_target_div"] = response.css(div_id).xpath(
                        '//*[not(self::script or self::style)]/text()[normalize-space(.)]').extract()

                # 3. json all
                item["xpath_all_text"] = response.xpath(
                    '//body//*[not(self::script or self::style)]/text()[normalize-space(.)]').extract()

                # 4. bs text all
                item["bs_all_text"] = BeautifulSoup(html, 'lxml').get_text()
                page_json = dict(item)
                del page_json["response"]
                del page_json["html_processed"]

                json_cnt = json.dumps(page_json, indent=2, ensure_ascii=False)
                # print(json_cnt)
                f.write(json_cnt)

                spider.logger.info(
                    "Extract data from %s and saved to %s" % (response.url, save_path))
            except IOError:
                spider.logger.error(
                    "Error thrown when writing html file %s to %s" % (response.url, save_path),
                    exc_info=True)

        return item


class FaqPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)
        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)
        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))
        # assume spider has this field
        h_save_dir = os.path.join(spider.save_dir)
        html_dir_name = str(h_save_dir).split('/')[-1]
        if_target_get=False
        try:
            if hasattr(spider, "target_faq_div_xpath"):
                target_div = spider.target_faq_div_xpath
                item['target_faq_div_xpath'] = {}
                if spider.data_deal:
                    for each_target in target_div:
                        item['target_faq_div_xpath'][each_target]=[]
                        qq = response.xpath(target_div[each_target])
                        for q in qq:
                            if type(q)==str:
                                ss = q.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            else:
                                s = q.xpath('string(.)').extract()
                                ss = ''.join(s)
                                ss=ss.replace('\n','').replace(' ','').replace('\t', '').replace('\r', '')
                            item['target_faq_div_xpath'][each_target].append(ss)
                        if len(item['target_faq_div_xpath'][each_target])==0:
                            del item['target_faq_div_xpath'][each_target]
                    if item['target_faq_div_xpath']:
                        if_target_get = True
                else:
                    for each_target in target_div:
                        item['target_faq_div_xpath'][each_target]=[]
                        qq = response.xpath(target_div[each_target]).extract()
                        for q in qq:
                            qx=q.strip()
                            if qx:
                                item['target_faq_div_xpath'][each_target].append(qx)
                        if len(item['target_faq_div_xpath'][each_target])==0:
                            del item['target_faq_div_xpath'][each_target]
                    if item['target_faq_div_xpath']:
                        if_target_get = True
            else:
                spider.logger.info(" %s :target_faq_div_xpath is None or error 。" % response.url)
            if if_target_get :
                save_path = _save_html_path(h_save_dir, response.url) + "-FAQ.json"
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                save_html_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/opt/data/save_html/faq/'+html_dir_name+'/'+response.url.replace(':','').replace('/','')+'.html'
                os.makedirs(os.path.dirname(save_html_path), exist_ok=True)
                with open(save_path, "w", encoding='utf-8') as f:
                    item['faq_url']=response.url
                    item['type'] = 'faq'
                    page_json = dict(item)
                    del page_json["response"]
                    del page_json["html_processed"]
                    json_cnt = json.dumps(page_json, indent=2, ensure_ascii=False)
                    f.write(json_cnt)
                    f.close()
                    spider.logger.info(
                        "Target_faq_extracted data from %s and saved to %s" % (response.url, save_path))

                with open(save_html_path, "w", encoding='utf-8') as ff:
                    ff.write(response.text)
                    ff.close()
        except IOError:
            spider.logger.error(
                "Error thrown when getting data and writing faq file .now ,url: %s" % (response.url),
                exc_info=True)
        return item


class ProductDescriptionPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)

        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)

        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))
        # assume spider has this field
        h_save_dir = os.path.join(spider.save_dir)
        html_dir_name = str(h_save_dir).split('/')[-1]
        if_target_get = False
        try:
            if hasattr(spider, "production_description_div"):
                target_div = spider.production_description_div
                item['production_description_div'] = {}
                if spider.data_deal:
                    for each_target in target_div:
                        item['production_description_div'][each_target]=[]
                        qq = response.xpath(target_div[each_target])
                        for q in qq:
                            if type(q)==str:
                                ss = q.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            else:
                                s = q.xpath('string(.)').extract()
                                ss = ''.join(s)
                                ss=ss.replace('\n','').replace(' ','').replace('\t', '').replace('\r', '')
                            item['production_description_div'][each_target].append(ss)
                        if len(item['production_description_div'][each_target])==0:
                            del item['production_description_div'][each_target]
                    if item['production_description_div']:
                        if_target_get = True
                else:
                    for each_target in target_div:
                        item['production_description_div'][each_target]=[]
                        qq = response.xpath(target_div[each_target]).extract()
                        for q in qq:
                            qx=q.strip()
                            if qx:
                                item['production_description_div'][each_target].append(qx)
                        if len(item['production_description_div'][each_target])==0:
                            del item['production_description_div'][each_target]
                    if item['production_description_div']:
                        if_target_get = True
            else:
                spider.logger.info(" %s :production_description_div is None or error 。" % response.url)

            if if_target_get :
                save_path = _save_html_path(h_save_dir, response.url) + "-Description.json"
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                save_html_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/opt/data/save_html/production/'+html_dir_name+'/'+response.url.replace(':','').replace('/','')+'.html'
                os.makedirs(os.path.dirname(save_html_path), exist_ok=True)
                with open(save_path, "w", encoding='utf-8') as f:
                    item['production_description_url']=response.url
                    item['type'] = 'production-description'
                    page_json = dict(item)
                    del page_json["response"]
                    del page_json["html_processed"]
                    json_cnt = json.dumps(page_json, indent=2, ensure_ascii=False)
                    f.write(json_cnt)
                    f.close()
                    spider.logger.info(
                        "production_description_div data from %s and saved to %s" % (response.url, save_path))

                with open(save_html_path, "w", encoding='utf-8') as ff:
                    ff.write(response.text)
                    ff.close()
        except IOError:
            spider.logger.error(
                "Error thrown when writing production_description_div file %s to %s" % (response.url, save_path),
                exc_info=True)
        return item


class ComplexWebPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)
        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)
        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))
        # assume spider has this field
        h_save_dir = os.path.join(spider.save_dir)
        html_dir_name = str(h_save_dir).split('/')[-1]
        if_target_get = False
        try:
            if hasattr(spider, "complex_web_target"):
                target_div = spider.complex_web_target
                item['complex_web_target'] = {}
                if spider.data_deal:
                    for each_target in target_div:
                        item['complex_web_target'][each_target] = []
                        qq = response.xpath(target_div[each_target])
                        for q in qq:
                            if type(q) == str:
                                ss = q.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            else:
                                s = q.xpath('string(.)').extract()
                                ss = ''.join(s)
                                ss = ss.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            item['complex_web_target'][each_target].append(ss)
                        if len(item['complex_web_target'][each_target]) == 0:
                            del item['complex_web_target'][each_target]
                    if item['complex_web_target']:
                        if_target_get = True
                else:
                    for each_target in target_div:
                        item['complex_web_target'][each_target] = []
                        qq = response.xpath(target_div[each_target]).extract()
                        for q in qq:
                            qx = q.strip()
                            if qx:
                                item['complex_web_target'][each_target].append(qx)
                        if len(item['complex_web_target'][each_target]) == 0:
                            del item['complex_web_target'][each_target]
                    if item['complex_web_target']:
                        if_target_get = True
            else:
                spider.logger.info(" %s :complex_web_target is None or error 。" % response.url)

            if if_target_get:
                save_path = _save_html_path(h_save_dir, response.url) + "-Complex.json"
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                save_html_path = os.path.dirname(os.path.dirname(os.path.abspath(
                    __file__))) + '/opt/data/save_html/complex/' + html_dir_name + '/' + response.url.replace(':',
                                                                                                                 '').replace(
                    '/', '') + '.html'
                os.makedirs(os.path.dirname(save_html_path), exist_ok=True)
                with open(save_path, "w", encoding='utf-8') as f:
                    item['complex_web_target_url'] = response.url
                    item['type'] = 'complex_get_data'
                    page_json = dict(item)
                    del page_json["response"]
                    del page_json["html_processed"]
                    json_cnt = json.dumps(page_json, indent=2, ensure_ascii=False)
                    f.write(json_cnt)
                    f.close()
                    spider.logger.info(
                        "complex_web_target data from %s and saved to %s" % (response.url, save_path))

                with open(save_html_path, "w", encoding='utf-8') as ff:
                    ff.write(response.text)
                    ff.close()

        except IOError:
            spider.logger.error(
                "Error thrown when writing product_description_Target file %s to %s" % (response.url, save_path),
                exc_info=True)
        return item


class JsPipeline(object):

    def process_item(self, item, spider):
        response = item.get("response", None)
        if response is None:
            raise DropItem("[%s] `response` not found in `item`''" % spider.name)
        html = item.get("html_processed", None)
        if html is None:
            raise DropItem("[%s] Missing `html_processed` in item for %s" % (spider.name, response.url))
        # assume spider has this field
        h_save_dir = os.path.join(spider.save_dir)
        save_path = _save_html_path(h_save_dir, response.url) + ".json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        item["target"] = []
        item["middl_data"] = spider.middl_data
        if_target_get=False
        try:
            if hasattr(spider, "complex_web_target_div_xpath"):
                target_div = spider.complex_web_target_div_xpath
                if target_div:
                    item['complex_web_target_js'] = {}
                    for each_target in target_div:
                        item['complex_web_target_js'][each_target] = []
                        qq = response.xpath(target_div[each_target])
                        for q in qq:
                            if type(q) == str:
                                ss = q.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            else:
                                s = q.xpath('string(.)').extract()
                                ss = ''.join(s)
                                ss = ss.replace('\n', '').replace(' ', '').replace('\t', '').replace('\r', '')
                            item['complex_web_target_js'][each_target].append(ss)
                        if len(item['complex_web_target_js'][each_target]) == 0:
                            del item['complex_web_target_js'][each_target]
                    if item['complex_web_target_js']:
                        if_target_get = True
                if spider.middl_data:
                    if_target_get=True

            else:
                spider.logger.info(" %s :complex_web_target_js is None or error 。" % response.url)

            if if_target_get:
                save_path = _save_html_path(h_save_dir, response.url) + "-JS.json"
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                html_dir_name = str(h_save_dir).split('/')[-1]
                save_html_path = os.path.dirname(os.path.dirname(os.path.abspath(
                    __file__))) + '/opt/data/save_html/js/' + html_dir_name + '/' + response.url.replace(':',
                                                                                                              '').replace(
                    '/', '') + '.html'
                os.makedirs(os.path.dirname(save_html_path), exist_ok=True)
                with open(save_path, "w", encoding='utf-8') as f:
                    item['complex_web_target_js_url'] = response.url
                    item['type'] = 'js'
                    page_json = dict(item)
                    del page_json["response"]
                    del page_json["html_processed"]
                    json_cnt = json.dumps(page_json, indent=2, ensure_ascii=False)
                    f.write(json_cnt)
                    f.close()
                    spider.logger.info(
                        "complex_web_target_js data from %s and saved to %s" % (response.url, save_path))

                with open(save_html_path, "w", encoding='utf-8') as ff:
                    ff.write(response.text)
                    ff.close()

        except IOError:
            spider.logger.error(
                "Error thrown when writing JS_Target file %s to %s" % (response.url, save_path),
                exc_info=True)
        return item


