import os
from scrapyd_api import ScrapydAPI


def scrapyd_start_all(projectname, spider_name, config_path_all, url='http://localhost:6800/', spi_conf_names=None):
    # url:ip:port   scrapyd serve
    # projectname: the project`s name
    # spider_name:  Type of spider  eg :faq_spider
    # config_path_all: Corresponding to the project and spider configuration file path
    # jobid:return value   ,a dict,   name of conf is the spider `s jobid,      eg,   bicc:fjddskjfvndfjdjfkljbnkdfj
    # spi_conf_names: names of conf(The name of the conf to be crawled )(Just the name without a suffix)

    scrapyd = ScrapydAPI(url)
    job_id = {}
    if spi_conf_names:
        for name in spi_conf_names:
            config_path_yml = config_path_all+"/%s.yml" % name
            print('config_path_yml:', config_path_yml)
            job_id[name] = scrapyd.schedule(projectname, spider_name, config_path=config_path_yml)
            print('spider_name:', name, '--', 'job_id:', job_id[name], '\n')
        print('start all ok')
        return job_id
    else:
        conf_names = os.listdir(config_path_all)
        for name in conf_names:
            config_path_yml = config_path_all+"/%s" % name
            print('config_path_yml:', config_path_yml)
            job_id[name.split('.')[0]] = scrapyd.schedule(projectname, spider_name, config_path=config_path_yml)
            print('spider_name:', name.split('.')[0], '--', 'job_id:', job_id[name.split('.')[0]], '\n')
        print('start all ok')
        return job_id


def scrapyd_stop_all( projectname, job_id):
        # job_id is list or dict
    if type(job_id) == dict:
        job_id_=[]
        for k in job_id:
            job_id_.append(job_id[k])
    job_id_ = job_id
    scrapyd = ScrapydAPI('http://localhost:6800/')
    for job_ in job_id_:
        scrapyd.cancel(project=projectname, job=job_)
    print('stop all ok')


