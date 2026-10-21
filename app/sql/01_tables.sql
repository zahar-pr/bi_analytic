DROP TABLE IF EXISTS `Подразделения`;
DROP TABLE IF EXISTS `Контрагенты`;
DROP TABLE IF EXISTS `Номенклатура`;
DROP TABLE IF EXISTS `РеализацияТоваровУслуг`;
DROP TABLE IF EXISTS `РеализацияТоваровУслугТовары`;

CREATE TABLE `Подразделения`
(
    `Ссылка`       UInt32,
    `Наименование` String,
    `Город`        String
)
ENGINE = MergeTree ORDER BY `Ссылка`;

CREATE TABLE `Контрагенты`
(
    `Ссылка`       UInt32,
    `Наименование` String,
    `ИНН`          String,
    `Город`        String
)
ENGINE = MergeTree ORDER BY `Ссылка`;

CREATE TABLE `Номенклатура`
(
    `Ссылка`       UInt32,
    `Наименование` String,
    `Категория`    String
)
ENGINE = MergeTree ORDER BY `Ссылка`;

CREATE TABLE `РеализацияТоваровУслуг`
(
    `Ссылка`         UInt32,
    `Номер`          String,
    `Дата`           Date,
    `Контрагент`     UInt32,
    `Подразделение`  UInt32,
    `СуммаДокумента` Decimal(15, 2)
)
ENGINE = MergeTree ORDER BY (`Дата`, `Ссылка`);

CREATE TABLE `РеализацияТоваровУслугТовары`
(
    `Реализация`   UInt32,
    `НомерСтроки`  UInt16,
    `Номенклатура` UInt32,
    `Количество`   UInt32,
    `Цена`         Decimal(15, 2),
    `Сумма`        Decimal(15, 2)
)
ENGINE = MergeTree ORDER BY (`Реализация`, `НомерСтроки`);
