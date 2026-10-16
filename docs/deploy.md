## Deploying Flask application on an Apache web server

Deploying a Flask application on an Apache web server is typically accomplished using mod_wsgi an Apache module that acts as a bridge to host Python web applications.

Below is a complete, step-by-step guide to deploying a production-ready Flask application using Apache on an Ubuntu/Debian system.

### Step 1: Install System Packages
First, update your package repository and install Apache, the `mod_wsgi` module for Python 3, and Python utility tools.

```shell
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip python3-venv -y
```

### Step 2: Set Up the Directory & Virtual Environment
It is best practice to place your application directory under `/var/www/` and isolate your Python dependencies inside a virtual environment.

1. Create the project directory:
  
    ```shell
    sudo mkdir -p /var/www/myflaskapp
    sudo chown -R $USER:$USER /var/www/myflaskapp
    cd /var/www/myflaskapp
    ```
2. Create and activate a virtual environment:

    ```shell
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install Flask inside the virtual environment:
    ```shell
    pip install Flask
    ```
### Step 3: Create the Flask App File
Create your main entry file, usually named `__init__.py` or `app.py`.

Let's create an app.py:
```shell
nano app.py
```

Paste the following basic Flask logic inside:
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Flask is running successfully on Apache2!"

if __name__ == '__main__':
    app.run()
```

### Step 4: Create the WSGI Entry Point
Apache uses a `.wsgi` file to find and point to your Flask application wrapper.

Create a file named `wsgi.py` in your application root directory:
```shell
nano wsgi.py
```
Paste the following configuration, which ensures your project paths are added to the Python system path:
```python
import sys
import logging

# Set up logging to track application errors
logging.basicConfig(stream=sys.stderr)

# Insert project directory path into system path
sys.path.insert(0, "/var/www/myflaskapp")

from app import app as application
```

### Step 5: Configure Apache Virtual Host
Now, create a configuration file instructing Apache how to map requests to your WSGI bridge.
```shell
sudo nano /etc/apache2/sites-available/myflaskapp.conf
```

Paste the following XML-like directives (replace your_domain_or_IP with your actual domain name or server IP address):
```apache
<VirtualHost *:80>
    ServerName your_domain_or_IP
    ServerAdmin admin@example.com

    # Point to your WSGI entry script
    WSGIScriptAlias / /var/www/myflaskapp/wsgi.py

    # Map WSGI to use your project's isolated Python Virtual Environment
    WSGIDaemonProcess myflaskapp python-home=/var/www/myflaskapp/venv
    WSGIProcessGroup myflaskapp

    <Directory /var/www/myflaskapp>
        Require all granted
    </Directory>

    # Error logging paths
    ErrorLog ${APACHE_LOG_DIR}/myflaskapp_error.log
    CustomLog ${APACHE_LOG_DIR}/myflaskapp_access.log combined
</VirtualHost>
```

### Step 6: Enable the Configuration & Restart Apache
Enable your newly created configuration file, disable Apache's default placeholder site, and restart the service to apply the setup.
```shell
sudo a2ensite myflaskapp.conf
sudo a2dissite 000-default.conf
sudo systemctl restart apache2
```

### Troubleshooting Tips
If you open your web browser to your server's IP address and encounter an issue, verify the following:
- **Check the Logs**: Run `sudo tail -f /var/www/myflaskapp/myflaskapp_error.log` or the default `/var/log/apache2/error.log` to view Python traceback syntax errors.
  
- **Permissions**: Make sure Apache's system user (`www-data`) has read permissions to your project folder hierarchy.