[![Build Status](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml)
 
# Функционал

![functional](./docs/diagram.png)

# Установка

## База данных
Запустите `./scripts/setupdb.sh` для создания таблиц из `schema.sql`, указав в качестве базы данных указанную в `db_secret.sec`, а в качестве имени пользователя — с правом на создание таблиц:
```sh
./setupdb.sh <db_name> <db_user> 
```

## Среда
В качестве виртуального окружения используется poetry. Для его инициализации в корне проекта необходимо запустить:
```sh
poetry init
```
Установка зависимостей:
```sh
poetry install --only main
```

# Запуск
Не забываем установить зависимости:
```sh
poetry install --only main
```
Запуск осуществляется исключительно через poetry:
```sh
poetry run bot
```
Поскольку в проекте используется относительное
импортирование, при запуске другим способом это приведёт к ошибкам импортирования.

# Совместная разработка

## Установка зависимостей
```sh
poetry install --with dev,docs
```
## Документация
За внутреннюю документацию отвечает sphinx. Для его генерации необходимо:
```sh
cd docs
make html
```

Внешняя документация — документация всех функций, которые непосредственно вызываются при вызове команды — реализуется через команды типа "help".

# Ресурсы проекта
[Группа в VK](https://vk.com/vcsys)\
[Цикл стримов с разработкой бота на YT](https://youtube.com/playlist?list=PLhz29l3FXDWhePFfKJw447uN3rLl020xz)
