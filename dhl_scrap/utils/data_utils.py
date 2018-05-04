import logging
import os
import re
from datetime import datetime
from . import config_utils


versioned_file_name_re_ptrn = re.compile(r"(?P<f_base>.+)[-](?P<f_ver>[0-9]+)(?P<f_ext>[.]\w+)?$")


logger = logging.getLogger(__name__)


def _stringify_http_header_data(val):
    if isinstance(val, bytes):
        return str(val, encoding="utf-8")
    elif isinstance(val, str):
        return val
    elif isinstance(val, list):
        return [_stringify_http_header_data(val_i) for val_i in val]
    else:
        raise ValueError("Unsupported Value Type %s \"%s\"" % (type(val), val))


def stringify_http_headers(headers):
    str_headers = dict()
    for k, v in headers.items():
        k_str = _stringify_http_header_data(k)

        if v is not None:
            v_str = _stringify_http_header_data(v)
        else:
            v_str = v

        str_headers[k_str] = v_str

    return str_headers


def rename_if_exists(path):
    if os.path.exists(path):
        filename = path[path.rfind(os.path.sep) + 1:]

        versioned_match = re.match(versioned_file_name_re_ptrn, filename)
        if versioned_match is not None:
            new_ver = int(versioned_match.group("f_ver")) + 1
            f_ext = versioned_match.group("f_ext")
            f_ext = f_ext if f_ext is not None else ""

            return path[:-len(filename)] + versioned_match.group("f_base") + "-" + str(new_ver) + f_ext
        else:
            return path + "-2"

    else:
        return path


def archive_to_s3(arc_name, data_dir, bucket_name):
    import shutil
    arc_file_path = shutil.make_archive(base_name="./tmp/" + arc_name,
                                        format='gztar',
                                        root_dir=data_dir)
    arc_file_name = os.path.basename(arc_file_path)
    logger.debug("Crawl result in %s zip into %s" % (data_dir, arc_file_path))

    # if bucket_dir is not None and len(bucket_dir > 0):
    #     bucket_key = bucket_dir + ("" if bucket_dir[-1] == '/' else "/") + arc_name
    # else:
    #     bucket_key = arc_name

    import boto3
    bucket = boto3.resource("s3").Bucket(bucket_name)

    bucket.upload_file(arc_file_path, arc_file_name)
    logger.info("Crawl result in %s successfully uploaded to %s" % (arc_file_path, arc_file_name))

    # verify uploaded
    obj_uploaded = bucket.Object(key=arc_file_name)
    _ = obj_uploaded.content_length
    logger.debug("Crawl result found in s3://%s/%s" % (obj_uploaded.bucket_name, obj_uploaded.key))

    return "s3://%s/%s" % (obj_uploaded.bucket_name, obj_uploaded.key)


def archive_results_to_s3(spider):
    ts = datetime.now()
    arc_name = "%s_%s" % (spider.name, ts.strftime("%Y%m%d_%H%M"))

    s3_path = archive_to_s3(arc_name, spider.save_dir, config_utils.archive_s3_bucket())
    spider.logger.info("Crawled data saved to %s" % s3_path)
