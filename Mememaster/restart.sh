pid=`cat run.pid`
echo ${pid}
kill -9 ${pid}
source venv/bin/activate
gunicorn run:app -p run.pid -b 127.0.0.1:5123 -w 4 --worker-class gevent  -D
deactivate
