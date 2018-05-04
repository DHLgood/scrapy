from ..spiders.faq_spider import InitialSpider
from scrapy.dupefilters import RFPDupeFilter


class ProductDescriptionSpider(InitialSpider):
    """A utility to scan and save file on the site

    docker run -d -it -v `pwd`:/opt/dhl/dhl-scrap -v \
    `pwd`/conf/local/product_description_spider_dhl_ai.yml:/opt/dhl/conf/product_description_spider.yml \
    dhl-scrap scrapy crawl product_description_spider

    """
    name = "product_description_spider"

    custom_settings = {
        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.ProductDescriptionPipeline": 100,
        },
    }

    def __init__(self, *a, **kw):
        super(ProductDescriptionSpider, self).__init__(*a, **kw)
        # the label contains target_div and other
        if hasattr(self.job_cfg, "production_description_div"):
            self.production_description_div = self.job_cfg.production_description_div
        # data need deal
        if hasattr(self.job_cfg, "data_deal"):
            self.data_deal = self.job_cfg.data_deal
        else:
            self.data_deal = False
        self.url_seen_path = self.config_path.split('dhl_scrap')[
                                 0] + 'opt/dhl/url_seen/product_description/'  # it is useful for test(单个测试)


class ComplexWebSpider(InitialSpider):
    """A utility spider to complex website

    """

    name = "complex_web_spider"

    custom_settings = {
        'ITEM_PIPELINES': {
            "dhl_scrap.pipelines.JsFilterPipeline": 50,
            "dhl_scrap.pipelines.ComplexWebPipeline": 100,
        },
     }

    def __init__(self, *a, **kw):
        super(ComplexWebSpider, self).__init__(*a, **kw)
        # the label contains target_div and other
        if hasattr(self.job_cfg, "complex_web_target"):
                self.complex_web_target = self.job_cfg.complex_web_target
        if hasattr(self.job_cfg, "data_deal"):
            self.data_deal = self.job_cfg.data_deal
        else:
            self.data_deal = False






