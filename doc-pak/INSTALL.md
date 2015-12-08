# INSTALL instructions 

The deployment of the `vk2-georeference` service was tested on a debian 7 system. It is a [python](https://www.python.org/) and relies partly of C-libraries like [gdal](http://www.gdal.org/) and [mapserver](http://mapserver.org/).

## Dependencies

	* postgresql-9.1 (>9.1) / postgis (1.5)
	* libgdal1  (1.9) / libgdal1-dev / python-gdal 
	* python-mapscript (6.4.1-2)
	* python-dev (2.7.5)
	* python-pyroj (1.8.9-1+b1)
	* python-imaging (1.1.7-4+deb7u1)
	* cgi-mapserver (6.4.1-2)
	* imagemagick (8:6.7.7.10)
	
## Install python environment	
	
All python dependencies could be installed system width, but it is good style to use [python virtual environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/). We therefor use the tool [virtualenv](https://virtualenv.pypa.io/en/latest/). 

Creates the virtual environement.

	virtualenv --no-site-packages python_env

Install the main python dependencies in the virtual environment.
	
	./python_env/bin/easy_install pyramid SQLAlchemy==0.8.3 psycopg2 pyramid_tm requests lockfile python-daemon numpy waitress
	
Some python libraries depend on C libraries, which can not be installed within a `virtualenv`. This is the case for the `gdal`, `mapscript`, `PIL` and `pyproj` dependencies. We therefor install them system wide (see section `Dependencies`) and link them in our virtual environment.

    ln -s /usr/lib/python2.7/dist-packages/gdal* ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/MapScript-6.0.1.egg-info ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/GDAL-1.9.0.egg-info ./python_env/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/mapscript.py* ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/_mapscript.so ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/osgeo/ ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/PIL* ./python_env/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/pyproj* ./python_env/lib/python2.7/site-packages/

Now all dependencies have been installed. Because the service relies on a the [Python Pyramid Framework](http://www.pylonsproject.org/) we have to build a proper version of our python projection. Run therefor:

	./python_env/bin/python setup.py install (for production)
	./python_env/bin/python setup.py develop (for development)
	
## Use vk2-georeference service with apache2

In production mode the service should be run behind an apache2 instance. 	

