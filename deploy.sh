sudo pkill -f uwsgi -9
sudo service nginx stop
uwsgi uwsgi.ini
sudo service nginx start
