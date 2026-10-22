# Тестовое задание BI: ClickHouse + FastAPI

<img width="1830" height="1386" alt="image" src="https://github.com/user-attachments/assets/851b9834-eee6-4dea-98d2-58e5a4a9de27" />

## База данных

ClickHouse в Docker. Параметры подключения и обработки лежат в `.env`.

```bash
docker compose up -d
```

## Структура данных и заполнение таблиц

При старте контейнер `app` создаёт 5 таблиц и заполняет их тестовыми данными (до 1000 записей), связанными по ключам.

```bash
docker compose up --build
```

## Витрина данных и график

Витрины `ВитринаЦеновыеСегменты` (5 ценовых сегментов по min/max) и `ВитринаПродаж` (облако продаж). График с фильтром по категории: http://localhost:8000


## MongoDB-версия

Та же задача на MongoDB, связанными по `_id`, витрины `ВитринаЦеновыеСегменты` и `ВитринаПродаж` как MongoDB views (`$lookup`, `$group`, `$unionWith`).

```bash
cd mongo
docker compose up --build
```

График: http://localhost:8001
