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

Copy `example.env` and rename to `.env`. Supply values in accordance with [django-environ](https://django-environ.readthedocs.io/en/latest/).

# Deploying

## Dreamhost

### Initial deploy
[Follow these instructions to create a Django 2 project](https://help.dreamhost.com/hc/en-us/articles/216385637-How-do-I-enable-Passenger-on-my-domain-), but instead of installing Django and creating a new project, `git clone` this repository and `pip3 install - r requirements.txt`.

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
1. `git fetch` and `git pull` to update the codebase on the server
2. Activate the virtual environment
3. Update `.env` as necessary from the update
4. Run `manage.py migrate` from the project directory
4. Run `manage.py collectstatic` from the project directory (is this a required step?)
6. Run `touch tmp/restart.txt` from the site root to restart Passenger