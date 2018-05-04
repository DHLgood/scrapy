import os
import shutil
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Request
from scrapy.http import HtmlResponse
from urllib.parse import urlparse, quote
from ..utils import config_utils, data_utils,parse_utils
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import ActionChains
from scrapy.dupefilters import RFPDupeFilter
from dhl_scrap import url_RFPDupeFilter

# option=webdriver.FirefoxOptions()
# option.set_headless()
# profile = webdriver.FirefoxProfile()
# profile.set_preference('browser.download.dir', "./opt/data/crawl_results")
# profile.set_preference('browser.download.folderList', 2)
# profile.set_preference('browser.download.manager.showWhenStarting', False)
# profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/zip')


class Initial_JS_Spider(CrawlSpider):
    """A utility class of spider to be inherited for complex
    """
    name = "initial_js_spider"

    custom_settings = {

        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.JsPipeline": 100,
        },
    }

    def __init__(self, *a, **kw):
        super(Initial_JS_Spider, self).__init__(*a, **kw)


        # prepare fields for command line arguments

        self.config_path = getattr(self, "config_path", config_utils.default_cfg_path(self.name))
        ts = datetime.now()
        # command line args check
        if self.config_path is None:
            usage = "usage: scrapy crawl %s -a config_path=<job config path> " % self.name
            print(usage)
            return

        # load job config (defined per site)
        self.job_cfg = config_utils.parse_yaml(self.config_path)
        #  Configuration parameters of phantomjs
        if hasattr(self.job_cfg, "desired_capabilities"):
            self.desired_capabilities = self.job_cfg.desired_capabilities
        else:
            self.desired_capabilities=DesiredCapabilities.PHANTOMJS
        if hasattr(self.job_cfg, "service_args"):
            self.service_args = self.job_cfg.service_args
        else:
            self.service_args=['--ignore-ssl-errors=true']
        if hasattr(self.job_cfg, "service_log_path"):
            self.service_log_path = self.job_cfg.service_log_path
        else:
            self.service_log_path=None
        if hasattr(self.job_cfg, "port"):
            self.port = self.job_cfg.port
        else:
            self.port=0

        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.add_argument("--headless")
        # self.driver = webdriver.Firefox(firefox_options=options)
        exe_path=self.config_path.split('opt')[0]+'geckodriver'
        self.driver = webdriver.Firefox(executable_path=exe_path, options=options)
        # self.driver = webdriver.Firefox(executable_path=exe_path)
        # self.driver=webdriver.Firefox(executable_path='/home/donghonglin/geckodriver',options=options)
        # self.driver=webdriver.PhantomJS(desired_capabilities=self.desired_capabilities,
        #                                 port=self.port,service_args=self.service_args,service_log_path=self.service_log_path)
        self.driver.maximize_window()
        if hasattr(self.job_cfg, "aims"):
            self.aims = self.job_cfg.aims # Click  operation  and  end mark
        else:
            self.aims=False
        if hasattr(self.job_cfg, "scroll"):
            self.scroll = self.job_cfg.scroll
        else:
            self.scroll=False
        # Click on the final single data acquisition (No children level need to click)
        if hasattr(self.job_cfg, "each_click"):
            self.each_click = self.job_cfg.each_click
        else:
            self.each_click=False
        # Mixed multi-level click parameters (target url always the same)
        if hasattr(self.job_cfg, "mult_click_path"):
            self.mult_click_path = self.job_cfg.mult_click_path
        else:
            self.mult_click_path=False
        # if get data in the download middleware
        if hasattr(self.job_cfg, "get_data_in_middleware"):
            self.get_data_in_middleware = self.job_cfg.get_data_in_middleware
        else:
            self.get_data_in_middleware=False
        # Need to get in the middleware data,
        self.middl_data={}
        # All dynamic html
        self.HTML=''


        if hasattr(self.job_cfg, "change_url"):
            self.change_url = self.job_cfg.change_url
        else:
            self.change_url=False

        if hasattr(self.job_cfg, "universal"):
            self.universal = self.job_cfg.universal
        else:
            self.universal=False
            #
        if hasattr(self.job_cfg, "aim_url_in_new_windows"):
            self.aim_url_in_new_windows = self.job_cfg.aim_url_in_new_windows
        else:
            self.aim_url_in_new_windows=False


        if hasattr(self.job_cfg, "js"):
            self.js = self.job_cfg.js
        else:
            self.js=False

        # init spider-defined fields: `start_urls` & `allowed_domains` can be defined in __init__()
        self.start_urls = self.job_cfg.start_urls
        self.allowed_domains = self.job_cfg.allowed_domains
        if hasattr(self.job_cfg, "further_allowed_domains"):
            self.further_allowed_domains = self.job_cfg.further_allowed_domains
        # one question_answer(no other) can not be included in a label,
        # but only all question_answer(no other) can in a label
        # additional spider property: save_dir
        url_parsed=urlparse(self.allowed_domains[0])
        ss=url_parsed.path.replace('.','-')
        self.save_dir = config_utils.DEFAULT_SAVE_DIR+'/js/'+ss+ts.strftime("%Y%m%d_%H%M")
        if hasattr(self.job_cfg, "save_dir"):
            self.save_dir = self.job_cfg.save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        # copied the job config file into `save_dir` for archiving purpose
        cfg_f_copied = shutil.copy(self.config_path, self.save_dir)
        self.logger.debug("Job Config file %s backup-ed to %s" % (self.config_path, cfg_f_copied))
        self.logger.info("Data directory: %s" % self.save_dir)
        # 1) no need to specify allowed_domains in _extractor as already specified in spider
        # 2) if URL contains port num and specify allow_domains in _extractor, need to add port-num
        self._extractor = LinkExtractor()

        # self.url_seen_path = self.config_path.split('dhl_scrap')[0]+'opt/dhl/url_seen/js_conf/'#    it is useful for test    eg:faq  production   complex(单个测试)
        #
        self.url_seen_path = self.config_path.split('opt')[0] + 'opt/dhl/url_seen/' + \
                             self.config_path.split('/')[-2] + '/'  # 批量启动

        self.filter_url = url_RFPDupeFilter.SeenURLFilter(path=self.url_seen_path)  # TODO












    def closed(self,reason):
        # Turn off the driver when the reptile exits
        if reason == "finished":
            self.filter_url.close(reason)#TODO
            self.driver.quit()
            print('配置文件为:'+self.config_path+'的爬虫结束.spider closed!')

    def parse(self, response):
        if isinstance(response, HtmlResponse):
            print(response.url)

            # yield item raw response obj to configurable item pipeline
            yield {
                # "html_processed" will be processed in pipelines
                "html_processed": response.text,

                # convenient way for pipeline to handle
                # use dhl_scrap.pipelines.RemoveResponsePipeline to take it out
                "response": response,
            }

            curr_depth = response.meta.get("depth", 1)

            links = self._extractor.extract_links(response)
            self.logger.debug("[depth-%d] links extracted from %s: %s" % (
                curr_depth, response.url, links))

            for link in links:
                # `callback` defaults to parse() method
                if hasattr(self.job_cfg, "further_allowed_domains"):
                    if parse_utils.further_allowed_domains_confirm(self.further_allowed_domains, link.url):
                        yield Request(url=link.url,meta={"depth": curr_depth + 1})
                    else:
                        pass
                else:
                    yield Request(url=link.url,meta={"depth": curr_depth + 1})

        else:
            self.logger.info("parse() ignore links in non-HtmlResponse at %s" % response.url)

    # def closed(self, reason):
    #     if reason == "finished":
    #         data_utils.archive_results_to_s3(self)


class JS_spider(Initial_JS_Spider):
    """A utility class of spider to be inherited for complex
    """
    name = "js_spider"

    custom_settings = {

        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.JsPipeline": 300,

        },
        'DOWNLOADER_MIDDLEWARES':{
            "dhl_scrap.JSMiddleware.PhantomJSMiddleware": 100,
        },
    }

    def __init__(self, *a, **kw):
        super(JS_spider, self).__init__(*a, **kw)
        if hasattr(self.job_cfg, "complex_web_target_div_xpath"):
            self.complex_web_target_div_xpath = self.job_cfg.complex_web_target_div_xpath
        else:
            self.complex_web_target_div_xpath = False































