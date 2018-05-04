import os
import shutil

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Request
from scrapy.http import HtmlResponse

from ..utils import config_utils, data_utils


class WebSpider(CrawlSpider):
    """A utility to scan and save file on the site

    docker run -d -it -v `pwd`:/opt/dhl/dhl-scrap -v \
    `pwd`/conf/local/web_spider_dhl_ai.yml:/opt/dhl/conf/web_spider.yml \
    dhl-scrap scrapy crawl web_spider

    """
    name = "web_spider"

    custom_settings = {
        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.CrawlSummaryPipeline": 100,
            "dhl_scrap.pipelines.SaveHtmlPipeline": 110,
            "dhl_scrap.pipelines.RemoveResponsePipeline": 999,
        },
    }

    def __init__(self, *a, **kw):
        super(WebSpider, self).__init__(*a, **kw)

        # prepare fields for command line arguments
        self.config_path = getattr(self, "config_path", config_utils.default_cfg_path(self.name))

        # command line args check
        if self.config_path is None:
            usage = "usage: scrapy crawl %s -a config_path=<job config path> " % self.name
            print(usage)
            return

        # load job config (defined per site)
        self.job_cfg = config_utils.parse_yaml(self.config_path)

        # init spider-defined fields: `start_urls` & `allowed_domains` can be defined in __init__()
        self.start_urls = self.job_cfg.start_urls
        self.allowed_domains = self.job_cfg.allowed_domains

        # additional spider property: save_dir
        self.save_dir = config_utils.DEFAULT_SAVE_DIR
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
                yield Request(url=link.url,
                              meta={"depth": curr_depth + 1})

        else:
            self.logger.info("parse() ignore links in non-HtmlResponse at %s" % response.url)

    def closed(self, reason):
        if reason == "finished":
            data_utils.archive_results_to_s3(self)


class TargetDivWebSpider(WebSpider):
    """A utility to scan and save file on the site

    docker run -d -it -v `pwd`:/opt/dhl/dhl-scrap -v \
    `pwd`/conf/local/target_div_spider_dhl_ai.yml:/opt/dhl/conf/target_div_spider.yml \
    dhl-scrap scrapy crawl target_div_spider

    """
    name = "target_div_spider"

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
        super(TargetDivWebSpider, self).__init__(*a, **kw)

        # additional spider property: target_div
        if hasattr(self.job_cfg, "target_div"):
            self.target_div = self.job_cfg.target_div

