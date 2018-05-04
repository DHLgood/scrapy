BOT_NAME = 'dhl_scrap'

SPIDER_MODULES = ['dhl_scrap.spiders']

USER_AGENT = 'dhl (+https://dhl.ai)'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 5
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3

HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 3600

LOG_ENABLED = True
LOG_LEVEL = "INFO"
# LOG_LEVEL = "DEBUG"3
# DUPEFILTER_DEBUG = True

CONCURRENT_REQUESTS = 2
FEED_EXPORT_ENCODING = 'utf-8'
# Listen to port number assignment
TELNETCONSOLE_PORT = [10000, 10060]



DUPEFILTER_CLASS ='scrapy.dupefilters.RFPDupeFilter'

DOWNLOADER_MIDDLEWARES = {
    "dhl_scrap.JSMiddleware.PhantomJSMiddleware": 100,
    # "dhl_scrap.JSMiddleware.JsScrollMiddleware": 150,
    # "dhl_scrap.JSMiddleware.MultClickMiddleware": 160,
    "dhl_scrap.JSMiddleware.UrlSaveMiddleware": 50, #TODO
}