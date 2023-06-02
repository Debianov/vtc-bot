![Build Status](https://github.com/GREEN-Corporation/discord-bot/actions/workflows/checks.yml/badge.svg)

# Введение
Бот разработан в рамках проекта "[Virtual Company Systems](https://vk.com/vcsys)" и предназначен для автоматизации процессов виртуальных транспортных компаний ETS 2/ATS. 

![functional](./docs/diagram.png)

# Подготовка к запуску

## База данных
В проекте используется PostgreSQL.

Создайте файл `db_secret.sec` в корне репозитория со следующим содержанием:
```sh
<имя базы данных>
<имя пользователя базы данных>
```

Запустите `./scripts/setupdb.sh` для создания таблиц из `schema.sql`, указав в качестве базы данных указанную в `db_secret.sec`, а в качестве имени пользователя — уполномоченного создавать таблицы.

## Среда
В качестве виртуального окружения используется poetry. Для его инициализации в корне проекта необходимо запустить:
```sh
poetry init
```

## VSCode
В .vscode содержатся верные конфигурации для запуска дебага и тестов. Дополнительных настроек не требуется.

# Запуск
Запуск осуществляется исключительно через poetry:
```sh
poetry run bot
```
Поскольку в проекте используется относительное
импортирование, при запуске другим способом это приведёт к ошибкам импортирования.

# Совместная разработка
## Документация
За внутреннюю документацию отвечает sphinx. Для его генерации необходимо:
```sh
cd docs
make html
```

Внешняя документация — документация всех функций, которые непосредственно вызываются при вызове
команды — реализуется через команды типа "help".

# Ресурсы проекта
[Группа в VK](https://vk.com/vcsys)
[Цикл стримов с разработкой бота на YT](https://youtube.com/playlist?list=PLhz29l3FXDWhePFfKJw447uN3rLl020xz)