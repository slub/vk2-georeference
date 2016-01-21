# INSTALL  

The following installation instructions were tested on a `Debian 8` os.

## Install system dependencies

	apt-get install libgdal1-dev python-gdal cgi-mapserver python-mapscript python-dev python-imaging imagemagick python-pyproj gdal-bin
	
## Check out the repository

	git clone https://git.slub-dresden.de/mendt/vk2-georeference
	
## Install python environment	
	
The python dependencies could be installed system width, but it is good style to use [python virtual environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/) with the [virtualenv](https://virtualenv.pypa.io/en/latest/) tool.

Creates the virtual environement.

	virtualenv --no-site-packages python_env

Install the main python dependencies in the virtual environment.
	
	./python_env/bin/easy_install pyramid SQLAlchemy==1.0.11 psycopg2 pyramid_tm requests python-daemon numpy waitress 
		
Some python libraries depend on C libraries, which can not be installed within a `virtualenv`. This is the case for the `gdal`, `mapscript`, `PIL` and `pyproj` dependencies. They were therefor install system wide (see section `Dependencies`) and linked in the virtual environment.

    ln -s /usr/lib/python2.7/dist-packages/gdal* ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/GDAL* ./python_env/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/mapscript.py* ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/_mapscript.so ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/osgeo/ ./python_env/lib/python2.7/site-packages/ 
	ln -s /usr/lib/python2.7/dist-packages/PIL* ./python_env/lib/python2.7/site-packages/
	ln -s /usr/lib/python2.7/dist-packages/pyproj* ./python_env/lib/python2.7/site-packages/
	
# Build pyramid project

The service relies on a the [Python Pyramid Framework](http://www.pylonsproject.org/). For building a `development` or `production` version run:

	./python_env/bin/python setup.py develop (for development)
	./python_env/bin/python setup.py install (for production)
	
***Important*** - Before installing a version please ensure you have create `settings.py` with proper values in the `vk2-georeference/georeference` folder. You can use therefor the `settings.template.py`.

## Remove old installation

For removing files from an old project build.

	rm -r ./georeference.egg-info/
	rm -r ./dist/
	rm -r ./build/lib.linux-x86_64-2.7/georeference/
	rm -r ./python_env/lib/python2.7/site-packages/georeference-0.0-py2.7.egg/

## Known Problems

* In case of producing validation results, try to save them locally. I-/O-Operations does take the most time of the hole georeference process and writing to NFS is much slower than store them locally. 
* Add EPSG:900913 to /usr/share/proj/epsg

```
# Google / OSM
<900913> +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +over no_defs
```


