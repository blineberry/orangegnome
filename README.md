# Getting Started

Set up a virtual environment at the root of the project:
```
python3 -m venv venv
```

Activate the virtual environment:
```
source venv/bin/activate
```

Install dependencies:
```
pip3 install -r requirements.txt
```

`mysqlclient` depends on `mysql-client` being available.
```
brew install mysql-client
```

Copy `example.env` and rename to `.env`. Supply values in accordance with [django-environ](https://django-environ.readthedocs.io/en/latest/).

# Deploying

## Dreamhost

### Initial deploy
[Follow these instructions to create a Django 2 project](https://help.dreamhost.com/hc/en-us/articles/360002341572), but instead of installing Django and creating a new project, `git clone` this repository and `pip3 install - r requirements.txt`.

A working `passenger_wsgi.py` file looks something like this
```
import sys, os
INTERP = "/home/USERNAME/SITENAME.com/venv/bin/python3"
#INTERP is present twice so that the new python interpreter 
#knows the actual executable path 
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/PROJECTNAME')  #You must add your project here

sys.path.insert(0,cwd+'/venv/bin')
sys.path.insert(0,cwd+'/venv/lib/python3.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "PROJECTNAME.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

In the project directory, copy `example.env` to `.env` and supply the production values.

### Updates
To deploy updates:
1. [Back up database](https://help.dreamhost.com/hc/en-us/articles/221686207-SSH-Backing-up-your-database)
2. `git fetch` and `git pull` to update the codebase on the server
3. Update `.env` as necessary from the update
4. Activate the virtual environment
5. Run `pip install -r requirements.txt`
6. Run `python manage.py migrate` from the project directory
7. Run `python manage.py collectstatic` from the project directory (is this a required step?)
8. Run `systemctl --user restart orangegnome` to restart the gunicorn service
