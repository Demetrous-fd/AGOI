## WEB-Приложение для инвентаризации имеющегося и поступающего оборудования с использованием QR-меток (Дипломный проект)

Django приложение помогает сотрудникам вести историю перемещения имеющегося оборудования, ставить на учет поступающее оборудование с созданием уникальных QR-меток и получать полную информацию оборудовании по QR-метке. 

### Технологии:
- FrontEnd: 
  - Vue3; 
  - PWA; 
  - WebSockets. 
- BackEnd: 
  - Python 3.10; 
  - Django Admin; 
  - Django-DRF; 
  - Django-WebSockets. 

### Возможности проекта:
- Предоставление информации по QR-коду; 
- Установка WEB-приложения на телефон; 
- Проведение инвентаризации:
  - В режиме реального времени с другими сотрудниками; 
  - В автономном режиме. 
- Просмотр отчётов; 
- Скачивание отчёта в формате excel файла. 

### Deploy
#### Требования к серверу:
- Docker и Docker Compose;
- Nginx
#### Шаги:
1. Выгрузить проект на сервер
```shell
git clone https://github.com/Demetrous-fd/AGOI
```
2. Перейти в папку проекта
```shell
cd AGOI
```
3. Создать и заполнить .env
```shell
cp backend/.env.example backend/.env 
cp frontend/.env.example frontend/.env 
```
4. Запустить сервисы
```shell
docker-compose --env-file=./backend/.env up -d
```
5. Открыть bash-терминал сервиса Backend
```shell
docker-compose exec -it backend bash
```
6. Заполнить БД
```shell
/app/.venv/bin/python manage.py loaddata seed/0001_initial.json
```
7. Создать суперпользователя
```shell
/app/.venv/bin/python manage.py createsuperuser
```
8. Выйти из консоли сервиса
```shell
exit
```
9. Добавить новую конфигурацию Nginx в sites-available
```shell
sudo nano /etc/nginx/sites-available/site.conf
```
Конфигурация:
```text
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}

server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host
        
        proxy_set_header X-Real-IP $remote_addr; 
        proxy_set_header X-Real-PORT $remote_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
10. Создание символической ссылки sites-available/site.conf в sites-enabled
```shell
sudo ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/
``` 
11. Проверка работоспособности конфигурации Nginx
```shell
sudo nginx -t
```
12. Перезапуск Nginx
```shell
sudo nginx -s reload
```
13. Приложение готово к работе, перейдите по адресу указанному в конфиге Nginx и пройдите авторизацию
![image](https://github.com/Demetrous-fd/AGOI/assets/63101072/42d3fc0b-526b-4e19-8150-8d60a19f9b22)
![image](https://github.com/Demetrous-fd/AGOI/assets/63101072/523fc967-bd06-4799-8e94-148b03fac7f0)

