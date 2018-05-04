from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class URLScanSpider(CrawlSpider):
    """A utility to scan all URLs on the site

    """
    name = "url_scan_spider"

    # rules must be defined as class variable
    all_links_extractor = LinkExtractor(unique=True)
    rules = [
        Rule(link_extractor=all_links_extractor,
             process_links='collect_links',
             follow=True),
    ]

    def __init__(self, *a, **kw):
        super(URLScanSpider, self).__init__(*a, **kw)

        # prepare fields for command line arguments
        self.url = getattr(self, "url", None)
        self.crawl_domain = getattr(self, "crawl_domain", None)
        self.output = getattr(self, "output", None)

        # command line args check
        if self.url is None:
            print("usage: scrapy crawl url_scan_spider "
                  "-a url=<url> -a crawl_domain=<crawl only in domain> "
                  "-a output=<store all links>")
            return

        # setup: `start_urls` & `allowed_domains` can be defined in __init__()
        self.start_urls = [self.url]
        if self.crawl_domain is not None:
            # An optional list of strings containing domains that this spider is allowed to crawl.
            self.allowed_domains = [self.crawl_domain]

        msg = "Start crawling %s " % self.url
        if self.crawl_domain is not None:
            msg += "(restricted to %s)" % self.crawl_domain
        msg += " ..."

        # data holders
        self.urls_found = set()

    def collect_links(self, links):
        if links is not None:
            for l in links:
                self.urls_found.add(l.url)

    def closed(self, reason):
        url_sorted = sorted(list(self.urls_found))

        if self.output is not None:
            with open(self.output, mode="w", encoding="utf-8") as f:
                for ln in url_sorted:
                    f.write(ln + "\n")
            print("URL(s) found in %s is/are saved in %s" % (self.url, self.output))
        else:
            print("URL(s) found in %s:" % self.url)
            for ln in url_sorted:
                print(ln)
