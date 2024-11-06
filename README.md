# Бекэнд кинотеатра (первая версия)

### Ссылка на репозиторий [repo](https://github.com/infox182/Auth_sprint_2)

### Запуск проекта

- Для запуска проекта создайте три файла .env, согласно .env.example, в директориях:
  - auth-service
  - fastapi-solution
  - movies_admin

- После чего командой ```sudo docker-compose up -d``` запустите проект

### Адреса компонентов проекта

- [Документация сервиса авторизации](http://localhost/api/openapi_auth)


- [Документация сервиса контента](http://localhost/api/openapi_movies)


- [Админка сервиса контента](http://localhost/admin)

> Логин и пароль для админки возьмите в auth-service/.env из переменных SUPERUSER_LOGIN SUPERUSER_PASSWORD

- [Jaeger](http://localhost:16686/)


