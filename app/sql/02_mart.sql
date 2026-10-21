CREATE OR REPLACE VIEW `ВитринаЦеновыеСегменты` AS
SELECT
    `Категория`,
    seg.1 AS `НомерСегмента`,
    seg.2 AS `Сегмент`,
    round(min_price + step * (seg.1 - 1), 2) AS `ЦенаОт`,
    if(seg.1 = 5, max_price, round(min_price + step * seg.1, 2)) AS `ЦенаДо`
FROM
(
    SELECT `Категория`, min_price, max_price, (max_price - min_price) / 5 AS step
    FROM
    (
        SELECT n.`Категория` AS `Категория`, min(t.`Цена`) AS min_price, max(t.`Цена`) AS max_price
        FROM `РеализацияТоваровУслугТовары` AS t
        JOIN `Номенклатура` AS n ON n.`Ссылка` = t.`Номенклатура`
        WHERE t.`Цена` > 0
        GROUP BY n.`Категория`

        UNION ALL

        SELECT 'Все категории', min(`Цена`), max(`Цена`)
        FROM `РеализацияТоваровУслугТовары`
        WHERE `Цена` > 0
    )
)
ARRAY JOIN arrayZip([1, 2, 3, 4, 5], ['Бюджет', 'Эконом', 'Стандарт', 'Премиум', 'Люкс']) AS seg;

CREATE OR REPLACE VIEW `ВитринаПродаж` AS
SELECT
    r.`Дата`          AS `Дата`,
    r.`Номер`         AS `НомерДокумента`,
    k.`Наименование`  AS `Контрагент`,
    p.`Наименование`  AS `Подразделение`,
    n.`Категория`     AS `Категория`,
    n.`Наименование`  AS `Номенклатура`,
    t.`Количество`    AS `Количество`,
    t.`Цена`          AS `Цена`,
    t.`Сумма`         AS `Сумма`
FROM `РеализацияТоваровУслугТовары` AS t
JOIN `РеализацияТоваровУслуг` AS r ON r.`Ссылка` = t.`Реализация`
JOIN `Номенклатура`  AS n ON n.`Ссылка` = t.`Номенклатура`
JOIN `Контрагенты`   AS k ON k.`Ссылка` = r.`Контрагент`
JOIN `Подразделения` AS p ON p.`Ссылка` = r.`Подразделение`
WHERE t.`Цена` > 0;
