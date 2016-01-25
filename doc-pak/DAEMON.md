## Install georeference DAEMON

The georeference daemons runs in the background of your system and regulary (default is every 5 minutes) checks for updates in the database. If he find some updates in the database he triggers an update of the database in the connected services. The daemon has been tested in an linux environment. Because of a bug in the python-daemon>=2.1 library it has to run as a root user.

The daemon could be started and stoped with:

	python_env/bin/python georeference/persistent/dataupdaterunner.py start/stop
	
It has to be 
	
The settings for the daemon could be found in the:

	georeference/settings.py

