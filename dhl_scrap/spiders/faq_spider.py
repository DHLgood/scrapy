import os
import shutil
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Request
from scrapy.http import HtmlResponse
from scrapy.dupefilters import RFPDupeFilter
from ..utils import config_utils, data_utils,parse_utils
from dhl_scrap import url_RFPDupeFilter
from scrapy_redis.dupefilter import RFPDupeFilter
from scrapy_redis.spiders import RedisSpider


class InitialSpider(CrawlSpider):
    """A utility class of spider to be inherited
    """
    name = "initial_spider"

    custom_settings = {

        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.CrawlSummaryPipeline": 100,
            "dhl_scrap.pipelines.SaveHtmlPipeline": 110,
            "dhl_scrap.pipelines.JsFilterPipeline": 300,
            "dhl_scrap.pipelines.ExtractTargetDivPipeline": 350,
            "dhl_scrap.pipelines.RemoveResponsePipeline": 999,
        },
    }

    def __init__(self, *a, **kw):
        super(InitialSpider, self).__init__(*a, **kw)

        # prepare fields for command line arguments

        self.config_path = getattr(self, "config_path", config_utils.default_cfg_path(self.name))
        print("############# PATH ###### : {}".format(self.config_path))

        # command line args check
        if self.config_path is None:
            usage = "usage: scrapy crawl %s -a config_path=<job config path> " % self.name
            print(usage)
            return
        # additional spider property: save_dir

        # load job config (defined per site)
        self.job_cfg = config_utils.parse_yaml(self.config_path)

        # init spider-defined fields: `start_urls` & `allowed_domains` can be defined in __init__()
        self.start_urls = self.job_cfg.start_urls
        self.allowed_domains = self.job_cfg.allowed_domains
        if hasattr(self.job_cfg, "further_allowed_domains"):
            self.further_allowed_domains = self.job_cfg.further_allowed_domains
        ts = datetime.now()

        #ubuntu deploy
        self.save_dir = self.save_dir + '/' + self.allowed_domains[0] + ts.strftime("%Y%m%d_%H%M")
        if self.save_dir is None:
            self.save_dir = config_utils.DEFAULT_SAVE_DIR + '/' + self.allowed_domains[0] + ts.strftime("%Y%m%d_%H%M")

        # test
        # self.save_dir = config_utils.DEFAULT_SAVE_DIR + '/' + self.allowed_domains[0] + ts.strftime("%Y%m%d_%H%M")

        os.makedirs(self.save_dir, exist_ok=True)
        # copied the job config file into `save_dir` for archiving purpose

        cfg_f_copied = shutil.copy(self.config_path, self.save_dir)
        self.logger.debug("Job Config file %s backup-ed to %s" % (self.config_path, cfg_f_copied))
        self.logger.info("Data directory: %s" % self.save_dir)
        # 1) no need to specify allowed_domains in _extractor as already specified in spider
        # 2) if URL contains port num and specify allow_domains in _extractor, need to add port-num
        self._extractor = LinkExtractor()

        # self.url_seen_path = self.config_path.split('dhl_scrap')[0]+'opt/dhl/url_seen/faq_conf/'#    it is useful for test    eg:faq  production   complex(单个测试)

        self.url_seen_path = self.config_path.split('opt')[0] + 'opt/dhl/url_seen/' + \
                             self.config_path.split('/')[-2] + '/'        #批量启动

        self.filter_url = url_RFPDupeFilter.SeenURLFilter(path=self.url_seen_path)#TODO
        # self.filter_url = RFPDupeFilter(path=self.url_seen_path)#TODO

    def closed(self, reason):
        # Turn off the driver when the reptile exits
        if reason == "finished":
            self.filter_url.close(reason)#TODO
            print('配置文件为：'+self.config_path+'已爬完--spider closed!')


    def parse(self, response):
        if isinstance(response, HtmlResponse):

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
                        yield Request(url=link.url,meta={"depth": curr_depth + 1},dont_filter=False)
                    else:
                        pass
                else:
                    yield Request(url=link.url,meta={"depth": curr_depth + 1})
        else:
            self.logger.info("parse() ignore links in non-HtmlResponse at %s" % response.url)

    # def closed(self, reason):
    #     if reason == "finished":
    #         data_utils.archive_results_to_s3(self)


class FaqSpider(InitialSpider):
    """A utility to faq

    docker run -d -it -v `pwd`:/opt/dhl/dhl-scrap -v \
    `pwd`/conf/local/web_spider_dhl_ai.yml:/opt/dhl/conf/web_spider.yml \
    dhl-scrap scrapy crawl web_spider

    """
    name = "faq_spider"

    custom_settings = {
        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.FaqPipeline": 100,

        },
    }

    def __init__(self, *a, **kw):
        super(FaqSpider, self).__init__(*a, **kw)
        # All aq's path
        if hasattr(self.job_cfg, "target_faq_div_xpath"):
            self.target_faq_div_xpath = self.job_cfg.target_faq_div_xpath
        else:
            self.target_faq_div_xpath = False


        if hasattr(self.job_cfg, "data_deal"):
            self.data_deal = self.job_cfg.data_deal
        else:
            self.data_deal = True





















            # # Further parse aq
        # if hasattr(self.job_cfg, "faq_detail_parse_xpath"):
        #     self.faq_detail_parse_xpath = self.job_cfg.faq_detail_parse_xpath
        # #  distribution of a_q`s information   a question_answer can be included in a label------Ture
        # # a question_answer can not  be included in a label----False
        # if hasattr(self.job_cfg, "aq_mes"):
        #     self.aq_mes = self.job_cfg.aq_mes
        # else:
        #     self.aq_mes = False
        # # one question_answer(no other) can not be included in a label,
        # # but only all question_answer(no other) can in a label
        # if hasattr(self.job_cfg, "only_all_aq_mes"):
        #     self.only_all_aq_mes = self.job_cfg.only_all_aq_mes
        # else:
        #     self.only_all_aq_mes = False

