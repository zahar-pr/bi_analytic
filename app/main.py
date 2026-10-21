from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import get_client

ALL = "Все категории"

app = FastAPI(title="BI: продажи по ценовым сегментам")
client = get_client()


@app.get("/api/categories")
def categories() -> list[str]:
    rows = client.query(
        "SELECT DISTINCT `Категория` FROM `ВитринаЦеновыеСегменты` "
        "ORDER BY `Категория` != {all:String}, `Категория`",
        parameters={"all": ALL},
    ).result_rows
    return [row[0] for row in rows]


@app.get("/api/chart")
def chart(category: str = ALL):
    segments = client.query(
        "SELECT `Сегмент` AS name, toFloat64(`ЦенаОт`) AS price_from, toFloat64(`ЦенаДо`) AS price_to "
        "FROM `ВитринаЦеновыеСегменты` WHERE `Категория` = {category:String} ORDER BY `НомерСегмента`",
        parameters={"category": category},
    ).named_results()

    sales = client.query(
        "SELECT `Дата` AS date, toFloat64(`Цена`) AS price, `Номенклатура` AS product "
        "FROM `ВитринаПродаж` WHERE {category:String} = {all:String} OR `Категория` = {category:String} "
        "ORDER BY `Дата`",
        parameters={"category": category, "all": ALL},
    ).named_results()

    return {"segments": list(segments), "sales": list(sales)}


app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "web" / "dist", html=True), name="web")
