import sys, site, os

site.addsitedir('~/vk2-georeference/python_env/lib/python2.7/site-packages')
sys.path.append('~/vk2-georeference/')
os.environ['PYTHON_EGG_CACHE'] = '~/vk2-georeference/'

from pyramid.paster import get_app, setup_logging
application = get_app('~/vk2-georeference/production.ini', 'main')

