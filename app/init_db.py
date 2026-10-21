import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from app.db import CHUNK_SIZE, get_client

random.seed(42)

CITIES = ["Екатеринбург", "Москва", "Казань", "Пермь", "Тюмень", "Челябинск", "Новосибирск", "Уфа"]
COMPANIES = ["Ромашка", "Вектор", "Альфа", "Гранит", "Меридиан", "Северстрой", "Техно", "Восход", "Сфера", "Импульс"]

CATEGORIES = {
    "Канцтовары": (["Ручка", "Тетрадь", "Блокнот", "Папка", "Маркер", "Степлер"], (20, 600)),
    "Продукты": (["Кофе", "Чай", "Шоколад", "Печенье", "Сыр", "Оливковое масло"], (60, 1500)),
    "Одежда": (["Футболка", "Джинсы", "Свитер", "Куртка", "Кроссовки", "Шапка"], (400, 8000)),
    "Бытовая техника": (["Чайник", "Утюг", "Блендер", "Пылесос", "Микроволновка", "Кофеварка"], (1500, 25000)),
    "Электроника": (["Наушники", "Колонка", "Клавиатура", "Монитор", "Планшет", "Смартфон"], (1000, 60000)),
}

DEPARTMENTS, COUNTERPARTIES, PRODUCTS, SALES, SALE_ITEMS = 10, 300, 500, 400, 1000
START_DATE, DAYS = date(2026, 1, 1), 90


def money(value: float) -> Decimal:
    return Decimal(f"{value:.2f}")


def run_sql(client, path: Path):
    text = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.strip().startswith("--"))
    for statement in text.split(";"):
        if statement.strip():
            client.command(statement)


def insert(client, table: str, columns: list[str], rows: list):
    for i in range(0, len(rows), CHUNK_SIZE):
        client.insert(table, rows[i:i + CHUNK_SIZE], column_names=columns)
    print(f"{table}: {len(rows)} записей")


def main():
    client = get_client()
    for sql_file in sorted((Path(__file__).parent / "sql").glob("*.sql")):
        run_sql(client, sql_file)

    departments = [(i, f"Магазин №{i}", random.choice(CITIES)) for i in range(1, DEPARTMENTS + 1)]

    counterparties = [
        (i, f'{random.choice(["ООО", "АО", "ИП"])} «{random.choice(COMPANIES)}-{i}»',
         str(random.randint(10**9, 10**10 - 1)), random.choice(CITIES))
        for i in range(1, COUNTERPARTIES + 1)
    ]

    products, base_price = [], {}
    for i in range(1, PRODUCTS + 1):
        category = random.choice(list(CATEGORIES))
        names, (low, high) = CATEGORIES[category]
        products.append((i, f"{random.choice(names)} M-{i:03d}", category))
        base_price[i] = low * (high / low) ** random.random()

    sale_ids = list(range(1, SALES + 1)) + [random.randint(1, SALES) for _ in range(SALE_ITEMS - SALES)]
    items, line_no, doc_sum = [], {}, {}
    for sale_id in sale_ids:
        product_id = random.randint(1, PRODUCTS)
        qty = random.randint(1, 10)
        price = money(0 if random.random() < 0.03 else base_price[product_id] * random.uniform(0.9, 1.1))
        line_no[sale_id] = line_no.get(sale_id, 0) + 1
        doc_sum[sale_id] = doc_sum.get(sale_id, 0) + price * qty
        items.append((sale_id, line_no[sale_id], product_id, qty, price, price * qty))

    sales = [
        (i, f"РТУ-{i:06d}", START_DATE + timedelta(days=random.randrange(DAYS)),
         random.randint(1, COUNTERPARTIES), random.randint(1, DEPARTMENTS), doc_sum[i])
        for i in range(1, SALES + 1)
    ]

    insert(client, "Подразделения", ["Ссылка", "Наименование", "Город"], departments)
    insert(client, "Контрагенты", ["Ссылка", "Наименование", "ИНН", "Город"], counterparties)
    insert(client, "Номенклатура", ["Ссылка", "Наименование", "Категория"], products)
    insert(client, "РеализацияТоваровУслуг",
           ["Ссылка", "Номер", "Дата", "Контрагент", "Подразделение", "СуммаДокумента"], sales)
    insert(client, "РеализацияТоваровУслугТовары",
           ["Реализация", "НомерСтроки", "Номенклатура", "Количество", "Цена", "Сумма"], items)


if __name__ == "__main__":
    main()
