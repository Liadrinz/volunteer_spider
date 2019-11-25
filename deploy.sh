sudo pkill -f uwsgi -9
sudo service nginx stop
nohup uwsgi uwsgi.ini > nohup.log &
sudo service nginx start

