mkdir log
nohup python manage.py runserver 0.0.0.0:8080 > log/django_server.log &
cd spider
nohup python run.py ../temp/ > ../log/spider_run.log &
cd ..
