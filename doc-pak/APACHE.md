# HowTo - Hide service behind a apache2 server.

In production mode it is safer to run the service instance behind an apache2 server. Therefor we can use `mod_wsgi` together with a `pyramid.wsgi` configuration. Assumed the `pyramid.wsgi` configuration lies within our project folder. It should contain the following content:

```
import sys, site, os

site.addsitedir('~/vk2-georeference/python_env/lib/python2.7/site-packages')
sys.path.append('~/vk2-georeference/')
os.environ['PYTHON_EGG_CACHE'] = '~/vk2-georeference/'

from pyramid.paster import get_app, setup_logging
application = get_app('~/vk2-georeference/production.ini', 'main')

```

Please use absolute paths instead of realitve once like in this example. We also need a proper `production.ini`. Therefor a template file could be founded in the root directory.

If the `vk2-georeference` application is build correctly as well as the `production.ini` and the `pyramid.wsgi`, add the following configuration to your apache virtualhost configuration:

In case apache2 version <= 2.3:

```
# Use only 1 Python sub-interpreter. Multiple sub-interpreters
WSGIApplicationGroup %{GLOBAL}
WSGIPassAuthorization On
WSGIDaemonProcess pyramid user=www-data group=www-data threads=4 \
	python-path=~/vk2-georeference/python_env/lib/python2.7/site-packages
WSGIScriptAlias /georeference ~/vk2-georeference/pyramid.wsgi

<Directory ~/vk2-georeference>
	WSGIProcessGroup pyramid
	Order allow,deny
	Allow from all
</Directory>
```

In case apache2 version > 2.3:

```
# Use only 1 Python sub-interpreter. Multiple sub-interpreters
WSGIApplicationGroup %{GLOBAL}
WSGIPassAuthorization On
WSGIDaemonProcess pyramid user=www-data group=www-data threads=4 \
	python-path=~/vk2-georeference/python_env/lib/python2.7/site-packages
WSGIScriptAlias /georeference ~/vk2-georeference/pyramid.wsgi

<Directory ~/vk2-georeference>
	WSGIProcessGroup pyramid
	Require all granted
</Directory>
```

