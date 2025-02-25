## Virtual Web Server

###### tags:  python, flask, AWS, Linode



AWS:  https://medium.com/@samuel.ngigi/deploying-python-flask-to-aws-and-installing-ssl-1216b41f8511

##### Modifying Database

###### password requires python for hash

```sql snippets
SELECT * FROM user WHERE name='Brad';
UPDATE user SET projects='test, baseball, dash' WHERE name='Brad';
DELETE FROM trailers WHERE trailerID =  
UPDATE trailers SET Width='102' WHERE trailerID =  
UPDATE trailers SET Model='8.5x20DODT10K' WHERE trailerID = 107 
```

```
sqlite3 ./<filename>
.exit		# exits sqlite3

.databases
.tables		# list of tables
.schema
.schema <tablename>
```



##### Analysis and Data ideas

article on predicting stock using news articles:  https://towardsdatascience.com/making-a-continual-ml-pipeline-to-predict-apple-stock-with-global-news-python-90e5d6610b21







##### Set up nginx server and flask

###### Packages must be loaded as SUDO

if not, it will work internally but not from external

###### S/W updates might require stop/start uwsgi.service

it would be worth testing this.  Do I need to start/stop?  Or just reload browser?

###### internal server error:

```
sudo systemctl stop uwsgi.service	# stop uwsgi
sudo systemctl start uwsgi.service 	# start uwsgi
sudo systemctl status uwsgi.service	# check log for errors

# if permission errors:
sudo chown www-data /home/raven/adittools	# this directory and applications?

sudo chmod 755 <filename>	# if a single file is mentioned in status

```



go to the section where you turn uwsgi.service on and off

Turn it off then back on, check status, you will see errors



note on changing directories or projects:  easiest to just follow through this process and undo as you go.  One key is to make sure the _proxy file is completely deleted in the sites-enabled

https://www.raspberrypi-spy.co.uk/2018/12/running-flask-under-nginx-raspberry-pi/

```install software
sudo apt-get install nginx
sudo pip3 install flask uwsgi	# these must be installed together

```

###### uninstalling nginx

```
sudo apt-get purge nginx nginx-common	# removes everything including config
sudo apt-get autoremove		# removes dependencies
#make sure /etc/nginx is removed
```





###### setup directory (flasktest) for flask operation

```
sudo chown www-data /home/raven/adittools		# change permissions flask folder

# test the nginx server by going to IP address from web browser on computer
# now test uwsgi.  You must be in the directory!
uwsgi --socket 0.0.0.0:8000 --protocol=http -w app:app

# now go through browser to IP address:8000 , this is the socket
192.168.1.210:8000


```

###### create uwsgi initialization file

note the last line of the file reloads when changes are made, it was added in the process after everything was working.

```
sudo nano uwsgi.ini
```

```
[uwsgi]

chdir = /home/raven/adittools
module = app:app

master = true
processes = 1
threads = 2

uid = www-data
gid = www-data

socket = /tmp/adittools.sock
chmod-socket = 664
vacuum = true

die-on-term = true
touch-reload = /home/raven/adittools/app.py
```

###### test .ini

```
uwsgi --ini uwsgi.ini

# the server is not visible but use second ssh terminal to check:

ls /tmp		# should see a adittools.sock file only when running

```

###### configure nginx to use uwsgi

```
sudo rm /etc/nginx/sites-enabled/default	# delete the default site

# create flasktest_proxy file
sudo nano /etc/nginx/sites-available/adittools_proxy

# create link from this file to sites-enabled directory
sudo ln -s /etc/nginx/sites-available/adittools_proxy /etc/nginx/sites-enabled

# restart nginx server
sudo systemctl restart nginx
```

contents of adittools_proxy:

```
server {
listen 80;
server_name localhost;

location / { try_files $uri @app; }
location @app {
include uwsgi_params;
uwsgi_pass unix:/tmp/adittools.sock;
}
}
```

###### create auto start file

create uwsgi.service in cd /etc/systemd/system

```
[Unit]
Description=uWSGI Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/raven/adittools/
ExecStart=/usr/local/bin/uwsgi --ini /home/raven/adittools/uwsgi.ini
PrivateTmp=false

[Install]
WantedBy=multi-user.target
```



###### test the auto start

```
sudo systemctl daemon-reload		# restart daemon so it picks up service
sudo systemctl start uwsgi.service	# start the service
sudo systemctl status uwsgi.service	# check status of service, should be active
sudo systemctl enable uwsgi.service # enables service to run on every reboot
```

At this point it should work directly from pi ip address

##### Duck DNS set up

these are good instructions but they are augmented by the actual duckdns link.  Note they give you your text for duck.sh which you can copy:  https://tinklr.net/raspberrypi/2017/03/12/setup-dynamic-dns.html

Port forwarding:  https://www.noip.com/support/knowledgebase/setting-port-forwarding-netgear-router-genie-firmware/

