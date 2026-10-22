ALL = "Все категории"
SEGMENTS = ["Бюджет", "Эконом", "Стандарт", "Премиум", "Люкс"]

PRICED = {"$match": {"Цена": {"$gt": 0}}}

SEGMENTS_PIPELINE = [
    PRICED,
    {"$lookup": {"from": "Номенклатура", "localField": "Номенклатура", "foreignField": "_id", "as": "n"}},
    {"$unwind": "$n"},
    {"$group": {"_id": "$n.Категория", "min": {"$min": "$Цена"}, "max": {"$max": "$Цена"}}},
    {"$unionWith": {"coll": "РеализацияТоваровУслугТовары", "pipeline": [
        PRICED,
        {"$group": {"_id": ALL, "min": {"$min": "$Цена"}, "max": {"$max": "$Цена"}}},
    ]}},
    {"$set": {"step": {"$divide": [{"$subtract": ["$max", "$min"]}, 5]}, "seg": {"$range": [0, 5]}}},
    {"$unwind": "$seg"},
    {"$project": {
        "_id": 0,
        "Категория": "$_id",
        "НомерСегмента": {"$add": ["$seg", 1]},
        "Сегмент": {"$arrayElemAt": [SEGMENTS, "$seg"]},
        "ЦенаОт": {"$round": [{"$add": ["$min", {"$multiply": ["$step", "$seg"]}]}, 2]},
        "ЦенаДо": {"$cond": [
            {"$eq": ["$seg", 4]},
            "$max",
            {"$round": [{"$add": ["$min", {"$multiply": ["$step", {"$add": ["$seg", 1]}]}]}, 2]},
        ]},
    }},
    {"$sort": {"Категория": 1, "НомерСегмента": 1}},
]

SALES_PIPELINE = [
    PRICED,
    {"$lookup": {"from": "РеализацияТоваровУслуг", "localField": "Реализация", "foreignField": "_id", "as": "r"}},
    {"$unwind": "$r"},
    {"$lookup": {"from": "Номенклатура", "localField": "Номенклатура", "foreignField": "_id", "as": "n"}},
    {"$unwind": "$n"},
    {"$lookup": {"from": "Контрагенты", "localField": "r.Контрагент", "foreignField": "_id", "as": "k"}},
    {"$unwind": "$k"},
    {"$lookup": {"from": "Подразделения", "localField": "r.Подразделение", "foreignField": "_id", "as": "p"}},
    {"$unwind": "$p"},
    {"$project": {
        "_id": 0,
        "Дата": "$r.Дата",
        "НомерДокумента": "$r.Номер",
        "Контрагент": "$k.Наименование",
        "Подразделение": "$p.Наименование",
        "Категория": "$n.Категория",
        "Номенклатура": "$n.Наименование",
        "Количество": 1,
        "Цена": 1,
        "Сумма": 1,
    }},
]


def create_marts(db):
    db.create_collection("ВитринаЦеновыеСегменты", viewOn="РеализацияТоваровУслугТовары", pipeline=SEGMENTS_PIPELINE)
    db.create_collection("ВитринаПродаж", viewOn="РеализацияТоваровУслугТовары", pipeline=SALES_PIPELINE)
