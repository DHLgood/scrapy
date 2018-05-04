import os
import shutil

from urllib.parse import urlparse, quote
from scrapy.linkextractors import LinkExtractor, IGNORED_EXTENSIONS
from scrapy.spiders import CrawlSpider, Request
from scrapy.http import HtmlResponse

from ..utils import config_utils, data_utils


# pdf_file_ptrn = re.compile(r".*[.]pdf([?])$")


def _url2save_path(base_dir, url, file_ext):
    suffix = "." + file_ext

    url_parsed = urlparse(url)

    domain_base_dir = url_parsed.netloc.replace(':', "_")
    save_dir = os.path.join(base_dir, domain_base_dir)

    inner_path = url_parsed.path

    if len(inner_path) > 0 and inner_path[0] == '/':
        inner_path = inner_path[1:]

    if len(inner_path) == 0:
        inner_path = "html.html"

    if inner_path[-1] == '/':
        inner_path = inner_path[:-1]

    if not inner_path.lower().endswith(suffix):
        inner_path = inner_path + suffix

    # play safe
    inner_path = quote(inner_path)

    return os.path.join(save_dir, inner_path)


class SaveFileSpider(CrawlSpider):
    """A utility to scan and save file on the site

    """
    f_ext = None

    def __init__(self, *a, **kw):
        super(SaveFileSpider, self).__init__(*a, **kw)

        # prepare fields for command line arguments
        self.config_path = getattr(self, "config_path", config_utils.default_cfg_path(self.name))

        # command line args check
        if self.config_path is None:
            print("usage: scrapy crawl %s -a config_path=<job config path>" % self.name)
            return

        print(self.logger)

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

        # predefine _extractor
        deny_exts = [x for x in IGNORED_EXTENSIONS if x.lower() != self.f_ext]

        # 1) no need to specify allowed_domains in _extractor as already specified in spider
        # 2) if URL contains port num and specify allow_domains in _extractor, need to add port-num
        self._extractor = LinkExtractor(deny_extensions=deny_exts)

    def save_file(self, response):
        self.logger.debug("Downloading %s ..." % response.url)

        save_path = _url2save_path(self.save_dir, response.url, self.f_ext)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            try:
                f.write(response.body)
                self.logger.info("Saved %s to %s" % (response.url, save_path))
            except IOError:
                self.logger.error(
                    "Error thrown when writing %s file %s to %s" % (
                        self.f_ext, response.url, save_path),
                    exc_info=True)

    def parse(self, response):
        curr_depth = response.meta.get("depth", 1)

        self.logger.debug("[depth-%d] Looking for %s file(s) in %s ..." % (
            curr_depth, self.f_ext, response.url))

        if isinstance(response, HtmlResponse):
            links = self._extractor.extract_links(response)
            self.logger.debug("[depth-%d] links extracted from %s: %s" % (
                curr_depth, response.url, links))

            for link in links:
                url = link.url
                url_parsed = urlparse(url)

                if url_parsed.path.lower().endswith("." + self.f_ext):
                    yield Request(url=url,
                                  callback=self.save_file,
                                  meta={"depth": curr_depth + 1})
                else:
                    # `callback` defaults to parse() method
                    yield Request(url=url,
                                  meta={"depth": curr_depth + 1})
        else:
            self.logger.info("parse() ignore non-HtmlResponse at %s" % response.url)

    def closed(self, reason):
        if reason == "finished":
            data_utils.archive_results_to_s3(self)


class PDFSpider(SaveFileSpider):
    """A utility to scan and save PDF file on the site

    docker run -d -it -v `pwd`:/opt/dhl/dhl-scrap \
    -v `pwd`/conf/local/pdf_spider_dhl_ai.yml:/opt/dhl/conf/pdf_spider.yml \
    dhl-scrap scrapy crawl pdf_spider

    """
    name = "pdf_spider"
    f_ext = "pdf"
