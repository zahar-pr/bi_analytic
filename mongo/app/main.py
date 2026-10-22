from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import get_db
from app.marts import ALL

app = FastAPI(title="BI на MongoDB: продажи по ценовым сегментам")
db = get_db()


@app.get("/api/categories")
def categories() -> list[str]:
    names = [row["_id"] for row in db["ВитринаЦеновыеСегменты"].aggregate([{"$group": {"_id": "$Категория"}}])]
    return sorted(names, key=lambda name: (name != ALL, name))


@app.get("/api/chart")
def chart(category: str = ALL):
    segments = db["ВитринаЦеновыеСегменты"].aggregate([
        {"$match": {"Категория": category}},
        {"$sort": {"НомерСегмента": 1}},
        {"$project": {
            "_id": 0,
            "name": "$Сегмент",
            "price_from": {"$toDouble": "$ЦенаОт"},
            "price_to": {"$toDouble": "$ЦенаДо"},
        }},
    ])

    sales = db["ВитринаПродаж"].aggregate([
        {"$match": {} if category == ALL else {"Категория": category}},
        {"$sort": {"Дата": 1}},
        {"$project": {
            "_id": 0,
            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$Дата"}},
            "price": {"$toDouble": "$Цена"},
            "product": "$Номенклатура",
        }},
    ])

    return {"segments": list(segments), "sales": list(sales)}


app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "web" / "dist", html=True), name="web")
