FROM python:3

LABEL maintainer=""

# install py packages according to dhl-scrap/setup.py
# scrapy command will be installed below
RUN pip install ruamel.yaml
RUN pip install scrapy
RUN pip install bs4
RUN pip install boto3

RUN mkdir -p /opt/data/crawl_results
RUN mkdir -p /opt/dhl/dhl-scrap
RUN mkdir -p /opt/dhl/conf

ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=

ENV dhl_SCRAP_S3_BUCKET=dhl-scrap-results

WORKDIR /opt/dhl/dhl-scrap

# build docker image "dhl-scrap":
#   docker build -t dhl-scrap .
