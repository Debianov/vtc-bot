[![Build Status](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml)
 
Система управления ВТК, реализованная на основе бота Discord.

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
Создайте секретный файл с ключом, именем базы данных и именем.
```sh
DISCORD_API_TOKEN=...
POSTGRES_DBNAME=...
POSTGRES_USER=...
```
После:
```sh
source file
```
Затем:
```sh
poetry run bot
```
Запуск не через `poetry run` приведёт к ошибкам импортирования.

# Совместная разработка
Текущий стек проекта: discord.py, psycopg, pytest + dpytest. 
Подробнее о правилах разработки: [contributing guidelines](./contributing.md).