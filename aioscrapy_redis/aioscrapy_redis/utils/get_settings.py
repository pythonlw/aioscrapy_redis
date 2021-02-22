# -*-coding:utf-8-*-
# Time:2020-02-12-16:21
# Author:lw

import os
import sys
import six
from aioscrapy_redis.utils.basesettings import Settings
from six.moves import cPickle as pickle

ENVVAR = 'SCRAPY_SETTINGS_MODULE'

def closest_scrapy_cfg(path='.', prevpath=None):
    if path == prevpath:
        return ''
    path = os.path.abspath(path)
    cfgfile = os.path.join(str(path), 'settings.py')
    if not os.path.exists(cfgfile):
        if '\\' in path:
            path1 = path + '\\' + str(path.split('\\')[-1])
            cfgfile = os.path.join(str(path1), 'settings.py')
        elif '/' in path:
            path1 = path + '/' + str(path.split('/')[-1])
            cfgfile = os.path.join(str(path1), 'settings.py')
    if os.path.exists(cfgfile):
        return cfgfile
    return closest_scrapy_cfg(os.path.dirname(path), path)

def init_env(project='default', set_syspath=True):
    closest = closest_scrapy_cfg()
    if closest:
        setting = '.'.join(closest.split('\\')[-2:])[:-3]
        os.environ['SCRAPY_SETTINGS_MODULE'] = setting
        projdir = os.path.dirname(closest)
        if set_syspath and projdir not in sys.path:
            sys.path.append(projdir)

def get_project_settings():  #读取项目下面的settings配置文件
    if ENVVAR not in os.environ:
        project = os.environ.get('SCRAPY_PROJECT', 'default')
        init_env(project)
    settings = Settings()
    settings_module_path = os.environ.get(ENVVAR)
    if settings_module_path:
        settings.setmodule(settings_module_path, priority='project')
    pickled_settings = os.environ.get("SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE")
    if pickled_settings:
        settings.setdict(pickle.loads(pickled_settings), priority='project')
    env_overrides = {k[7:]: v for k, v in os.environ.items() if
                     k.startswith('SCRAPY_')}
    if env_overrides:
        settings.setdict(env_overrides, priority='project')
    return settings


from . import settings
class Base_Settings():  #读取默认settings文件中的配置
    @classmethod
    def get(cls,name,default=None):
        dicts = {}
        for key in dir(settings):
            dicts[key] = getattr(settings, key)
        return dicts.get(name,default)



from aioscrapy_redis.aioscrapyredis.utils.misc import load_object
from collections import defaultdict

def get_middlewares(): #读取下载中间件配置
    settting_param=get_project_settings().get('DOWNLOADER_MIDDLEWARES')
    try:
        settting_param=sorted(settting_param.items(),key = lambda x:x[1])
        settting_param=[i[0] for i in settting_param]
    except:
        print('It is error to DOWNLOADER_MIDDLEWARES in the settings configuration')
        return {'process_request':[],'process_response':[],'process_exception':[]}
    methods = defaultdict(list)
    for i in settting_param:
        mw_obj=load_object(i)
        if hasattr(mw_obj,'process_request'):
            methods['process_request'].append(mw_obj().process_request)
        if hasattr(mw_obj,'process_response'):
            methods['process_response'].insert(0,mw_obj().process_response)
        if hasattr(mw_obj,'process_exception'):
            methods['process_exception'].insert(0,mw_obj().process_exception)
    return methods


def get_pipelines(): #读取item_pipeline配置
    setting_pipeline = get_project_settings().get('ITEM_PIPELINES')
    try:
        setting_pipeline=sorted(setting_pipeline.items(),key = lambda x:x[1])
        setting_pipeline = [i[0] for i in setting_pipeline]
    except:
        print('It is error to ITEM_PIPELINES in the settings configuration')
        return {'process_item':[]}
    item_methods = defaultdict(list)
    for i in setting_pipeline:
        mw_obj=load_object(i)
        if hasattr(mw_obj,'process_item'):
            item_methods['process_item'].append(mw_obj().process_item)
    return item_methods






