import os
import ruamel.yaml
import sys
from .dotdict import DotDict


import pkg_resources
DEFAULT_SAVE_DIR = "./opt/data/crawl_results"
# _LOCAL_PATH = pkg_resources.resource_filename('dhl_scrap', "opt/dhl/conf/faq_spider.yml")


def default_cfg_path(spider_name):
    resource = "../opt/dhl/conf/%s.yml" % spider_name
    ps=pkg_resources.resource_filename('dhl_scrap', resource)
    return ps



def archive_s3_bucket():
    return os.environ["dhl_SCRAP_S3_BUCKET"]


def parse_yaml(fpath):
    """Parse YAML file into `Config` object.
        Args:
            fpath: string, file path

    """
    config = DotDict()
    with open(fpath, 'r',encoding='utf-8') as f:
        yaml_obj = ruamel.yaml.load(f, ruamel.yaml.RoundTripLoader, preserve_quotes=True)
        parse_yaml_item(config, yaml_obj)
    return config


def parse_yaml_item(config, yaml_obj):
    for key, value in yaml_obj.items():
        if isinstance(value, ruamel.yaml.comments.CommentedMap):
            config[key] = DotDict()
            parse_yaml_item(config[key], value)
        else:
            config[key] = value
    return config


if __name__ == '__main__':
    yaml_text = """
    root:
        child_1:
            grand_child_1: value_1
            grand_child_2: value_2
        child_2: value_3
        child_3:
            grand_child_3:
                grand_grand_child_1: 100
    """
    config = parse_yaml('/opt/dhl/conf/dhl_core/dhl_reason.yaml')
    print(config)
