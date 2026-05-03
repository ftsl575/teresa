# Cursor master prompt — Lenovo DCSC parser robustness refactor

## 1. Контекст и цель

Teresa (`spec_classifier/`) — детерминированный пайплайн классификации Excel BOM-спецификаций для шести вендоров (Dell, Cisco, HPE, Lenovo, xFusion, Huawei). Каждый вендор имеет собственный парсер в `src/vendors/<vendor>/parser.py`. Lenovo-парсер сейчас опирается на жёстко зашитые позиционные константы (`_HEADER_ROW = 5`, `_DATA_START_ROW = 8`, индексы колонок 0/2/4/5/7, точное имя листа `"Quote"`). Любая ручная правка Lenovo-файла или экспорт в другой версии DCSC ломает парсер. Цель — привести Lenovo к уровню устойчивости HPE-парсера: шапка ищется по содержимому, колонки мапятся по именам, лист подбирается из приоритетного списка. Контракт `parse_excel(filepath) -> (List[dict], header_row_index)` и имена ключей в row dict при этом остаются неизменными — выше по pipeline на них завязан normalizer.

## 2. Файлы для контекста (открой перед работой)

- `src/vendors/lenovo/parser.py` — рефакторим
- `src/vendors/hpe/parser.py` — образец устойчивого парсинга (col_map по именам, end-of-data по содержимому)
- `src/core/parser.py` — образец `find_header_row()` сканированием первых 20 строк
- `src/vendors/lenovo/adapter.py` — обновить `can_parse()`
- `src/vendors/lenovo/normalizer.py` — НЕ менять; только читать как контракт row dict
- `tests/test_lenovo_parser.py` — существующие unit-тесты, плюс эталонная разметка стандартного Lenovo-файла в фикстуре `_make_lenovo_xlsx()`
- `tests/test_lenovo_normalizer.py` — фикстура `_raw()` фиксирует обязательные ключи row dict
- `tests/test_regression_lenovo.py` — golden-регрессия для L1.xlsx … L11.xlsx
- `tests/helpers.py` — `run_pipeline_in_memory()`, `build_golden_rows()`

## 3. Контракт API (зафиксирован, менять нельзя)

```python
def parse_excel(filepath: str) -> Tuple[List[dict], int]:
    """
    Returns:
        rows: List[dict] с обязательными ключами:
            "Part number"         — строка part number или None для разделителей
            "Product Description" — строка описания или None
            "Qty"                 — число или None
            "Price"               — число или None
            "Export Control"      — строка ('Yes'/'No'/...) или None
            "__row_index__"       — int, 1-based номер строки Excel
        header_row_index: 0-based индекс строки шапки
    """
```

Ключи row dict — точные имена, как сейчас читает `src/vendors/lenovo/normalizer.py` (см. `_raw()` в `tests/test_lenovo_normalizer.py`). Любое переименование сломает normalizer и пайплайн целиком.

## 4. Что должно измениться в парсере

### 4.1. Поиск листа по приоритетному списку

Сейчас падает с `ValueError`, если нет листа `"Quote"`. После рефакторинга:

1. Точное совпадение `"Quote"` (case-sensitive, как сейчас) — это основной лист во всех 11 эталонных файлах L1.xlsx … L11.xlsx.
2. Если `"Quote"` отсутствует, попытаться найти лист `"Quote w availability"` (присутствует в 10/11 эталонных файлов как альтернативный экспорт).
3. Если и его нет — перебор остальных листов в порядке `wb.sheetnames`; для каждого попытка найти Lenovo-шапку (см. 4.2). Первый лист, где шапка найдена, выигрывает.
4. Явно ИСКЛЮЧИТЬ из перебора служебные листы DCSC: `"Power Report"`, `"ConfigGroupView"`, `"Summary"`, `"Message History"` (они есть в эталонных файлах и шапку с маркерами не содержат, но во избежание ложных срабатываний и лишней работы их лучше пропускать).
5. Если ни в одном листе шапка не найдена — `ValueError` с текстом, перечисляющим имена листов в файле (как сейчас).

Это покрывает кейсы переименования листа (`"Quote 2024"`, `"BOM"`, `"Configuration"` и т. п.) и одновременно использует знание о структуре стандартного DCSC-экспорта.

### 4.2. Поиск шапки по содержимому

Убрать константу `_HEADER_ROW = 5`. Вместо этого сканировать первые 30 строк листа сверху и считать строкой шапки ту, в которой одновременно встречаются маркерные заголовки. Точные имена заголовков **подтверждены на всех 11 эталонных файлах** L1.xlsx … L11.xlsx — header лежит на 0-based row 5 во всех 11 и содержит:

```
['Part number', None, 'Product Description', None, 'Qty', 'Price', 'Total Part Price', 'Export Control', None, None, ...]
```

Маркерный набор для поиска (все пять должны присутствовать в одной строке):

- `"Part number"` (внимание: маленькая `n` в `number`)
- `"Product Description"`
- `"Qty"`
- `"Price"`
- `"Export Control"`

Сравнение — `str(cell).strip() == "<имя>"` (case-sensitive, с обрезкой пробелов; так же делает HPE-парсер). Шапкой считается строка, в которой найдены все пять маркеров. Возвращаемый `header_row_index` — 0-based индекс этой строки (для стандартного файла = 5).

Колонка `"Total Part Price"` присутствует, но в `col_map` для логики парсера она не нужна — её значения игнорируем (это формулы, см. 4.8).

### 4.3. Маппинг колонок по именам через `col_map`

Убрать жёсткие индексы `raw[0]`, `raw[2]`, `raw[4]`, `raw[5]`, `raw[7]`. После нахождения шапки построить:

```python
col_map: dict[str, int] = {}
for idx, val in enumerate(header_row):
    if val is not None:
        col_map[str(val).strip()] = idx
```

Затем читать значения через `col_map["Part number"]`, `col_map["Product Description"]`, `col_map["Qty"]`, `col_map["Price"]`, `col_map["Export Control"]`. Если какой-то из обязательных маркеров пропал в col_map (теоретически невозможно после 4.2, но защитимся) — `ValueError` со списком найденных имён.

Важно: колонки `"Part number"` и `"Product Description"` в стандартном DCSC-файле занимают объединённые ячейки, поэтому в шапке между ними появляется `None` (col 1 и col 3 пустые). Это нормально — `col_map` их просто игнорирует.

### 4.4. Определение начала данных

Сейчас данные начинаются на жёстко заданной строке 8 (0-based). Стандартный DCSC-файл устроен так (**проверено на всех 11 файлах L1…L11**):
- `header_row` = 5
- `header_row + 1` (row 6) — суб-шапка: `[None, None, None, None, None, '(per unit)\nUS Dollar', '(quantity x unit price)\nUS Dollar', None, ...]` (Part number пустой)
- `header_row + 2` (row 7) — полностью пустая строка
- `header_row + 3` (row 8) и далее — данные; первая строка данных всегда CTO Part number вида `7DXXCTO1WW` в col 0 + Description вида `"Server : ThinkSystem ..."` или `"Server 1C DB : ThinkSystem ..."` в col 2

После рефакторинга вместо `+3` использовать поведенческий критерий: сканировать строки после шапки и пропускать всё до **первой строки, в которой `col_map["Part number"]` непустой**. С этой строки начинается итерация данных. Это автоматически отбрасывает суб-шапку (Part number пуст) и pre-data пустые строки.

### 4.5. Сохранить empty rows как разделители ВНУТРИ данных

Существующее поведение, закреплённое тестами (`test_terms_and_conditions_stops_parsing`, `test_empty_rows_included_as_separators`):

- Пустые строки **до** первой data-строки — пропускаются.
- Пустые строки **между** data-строками — включаются в результат как row dict с `None` во всех полях, чтобы normalizer мог различить группы (CTO-блоки разделены пустой строкой).
- Пустая строка непосредственно перед stop-маркером "terms and conditions" — сейчас включается в результат (см. `test_terms_and_conditions_stops_parsing`: 2 data rows + 1 empty separator = 3 rows). Сохранить это поведение.

Реализация: ввести флаг `seen_data = False`; до первой data-строки empty-row пропускаем; после — включаем.

### 4.6. Стоп-маркер по содержимому

Сохранить текущее правило: `_STOP_SENTINEL = "terms and conditions"`. Проверка — на первой непустой ячейке строки (как сейчас), case-insensitive, через `.lower().startswith(_STOP_SENTINEL)`. Сейчас проверка идёт на `raw[0]`; после рефакторинга — на первой непустой ячейке строки (по аналогии с HPE), потому что после `col_map` мы не привязаны к индексу 0.

В реальных файлах текст ровно `"TERMS AND CONDITIONS:"` (заглавные + двоеточие), но `.lower().startswith("terms and conditions")` его корректно ловит — менять текст не нужно.

### 4.7. `__row_index__` как 1-based номер Excel-строки

Сохранить точно. Сейчас `excel_row_1based = i + 1`, где `i` — 0-based индекс из `iter_rows()`. Та же арифметика после рефакторинга. Тест `test_data_start_at_row_8` фиксирует: для row 8 (0-based) → `__row_index__ == 9`.

### 4.8. `data_only=False` сохранить

В колонке `Total Part Price` лежат Excel-формулы. Парсер их не читает (нет в выходных полях), но `openpyxl.load_workbook(..., data_only=False)` оставить — иначе формулы превращаются в `None` или закешированное значение, и могут случайно "оживить" если кто-то добавит чтение этого поля. Комментарий в docstring сохранить.

### 4.9. Обновить `can_parse()` в `src/vendors/lenovo/adapter.py`

Сейчас проверяет:
1. Лист `"Quote"` присутствует.
2. Cell row 0, col 2 содержит `"Data Center Solution Configurator"`.

После рефакторинга парсер уже не привязан к листу `"Quote"`, поэтому `can_parse()` тоже должен ослабить проверку. Новая логика: пройтись по всем листам (с тем же исключением служебных, что и в 4.1) и вернуть `True`, если хотя бы в одном найдена Lenovo-шапка (правило из 4.2 — все пять маркерных заголовков в одной строке среди первых 30). Маркер `"Data Center Solution Configurator"` в первой строке — слабее критерия наличия шапки, можно убрать (упоминание DCSC в первой строке есть не во всех версиях экспорта).

**Дискриминация vs другие вендоры — проверено эмпирически:** прогон такого критерия (5 маркеров в одной строке среди первых 30, по любому листу с исключением служебных) по 41 эталонному файлу всех 6 вендоров (`L1…L11`, `dl1…dl5`, `ccw_1…ccw_2`, `hp1…hp8`, `xf1…xf10`, `hu1…hu5`) даёт **11/11 матчей по Lenovo и 0 false positives** по Dell/Cisco/HPE/xFusion/Huawei. Конфликта с дискриминацией других адаптеров нет; `tests/test_can_parse_xfusion_huawei_disjoint.py` (тестирует только XFusion vs Huawei) тоже не задевается.

Альтернатива (если хочется консервативнее): сначала пробовать прежнюю быструю проверку (Quote + DCSC в row 0); если не сработала — fallback на сканирование шапки по всем листам. На усмотрение.

## 5. Что НЕ менять

- Сигнатуру `parse_excel(filepath: str) -> Tuple[List[dict], int]`.
- Имена ключей в row dict (`"Part number"`, `"Product Description"`, `"Qty"`, `"Price"`, `"Export Control"`, `"__row_index__"`).
- Файл `src/vendors/lenovo/normalizer.py`.
- Парсеры других вендоров (HPE, Dell, Cisco, Huawei, xFusion).
- Структуру golden-данных в `golden/L*_expected.jsonl`.
- Поведение `data_only=False`.
- 1-based семантику `__row_index__`.
- Поведение empty-rows-as-separators между data-строками (тесты в `test_lenovo_parser.py` и `test_lenovo_normalizer.py` это закрепляют).

## 6. Тестирование

Все команды запускаются из `spec_classifier/` (или из репо-корня; путь к pytest относительный).

```bash
# Полный прогон всех тестов проекта
python -m pytest tests/ -v --tb=short

# Только Lenovo (parser + normalizer + rules + regression)
python -m pytest tests/test_lenovo_parser.py tests/test_lenovo_normalizer.py tests/test_lenovo_rules_unit.py tests/test_regression_lenovo.py -v

# Только parser (быстрый цикл во время рефакторинга)
python -m pytest tests/test_lenovo_parser.py -v

# Только golden-регрессия Lenovo (требует L1.xlsx … L11.xlsx
# в paths.input_root/lenovo/, см. config.local.yaml; иначе все 11 тестов skip)
python -m pytest tests/test_regression_lenovo.py -v
```

Из репо-корня есть PowerShell-обёртка:

```powershell
.\run.ps1 -TestsOnly
```

Регенерация golden (если по какой-то причине допустимая разница в выводе появилась — но в этом рефакторинге golden меняться НЕ должны):

```bash
# Перегенерировать один файл
python main.py --save-golden --vendor lenovo --input <path>/L1.xlsx
# Или интерактивно перезаписать все
python main.py --update-golden
```

**Критерий зелёного билда:**
- Все существующие тесты в `tests/test_lenovo_parser.py`, `tests/test_lenovo_normalizer.py`, `tests/test_lenovo_rules_unit.py` проходят без изменений тестового кода.
- `tests/test_regression_lenovo.py` для L1…L11 даёт identical output (golden JSONL не меняются).
- Полный `pytest tests/ -v` зелёный.

## 7. Новые тесты на устойчивость

Добавить в `tests/test_lenovo_parser.py` минимум четыре синтетических теста на сценарии, которые сейчас сломали бы парсер. Использовать существующий хелпер `_make_lenovo_xlsx()` как базу или сделать его параметризованным.

1. **Сдвиг шапки.** Шапка начинается не с row 5, а с row 6 или 7 (вставлена дополнительная пустая строка или extra preamble line перед шапкой). Парсер должен найти шапку сканированием и корректно прочитать данные; `header_row_index` должен соответствовать реальной позиции.

2. **Переименованный лист.** Лист называется `"Quote 2024"` или `"BOM"` вместо `"Quote"`. Парсер должен найти лист fallback-логикой и распарсить данные. `can_parse()` должен вернуть `True`.

3. **Добавлена колонка в середине шапки.** Например, после `"Qty"` вставлен `"Discount"`. Реальные индексы `"Price"`, `"Total Part Price"`, `"Export Control"` уезжают на +1. Парсер должен корректно прочитать данные через `col_map`, не путая Discount с Price.

4. **Переставленные колонки.** Порядок шапки изменён, например: `["Product Description", None, "Part number", None, "Export Control", "Qty", "Price", "Total Part Price"]`. Парсер по `col_map` должен корректно соотнести значения.

Опционально, но желательно добавить пятый кейс:

5. **Пустая строка внутри блока данных** уже покрыта `test_empty_rows_included_as_separators` — но добавьте регрессионный тест, что после рефакторинга empty-row внутри данных по-прежнему попадает в output (важно, чтобы новая логика "skip pre-data empty rows" не съела этот случай).

## 8. Подход к работе (incremental)

Не одним коммитом. Между шагами — `python -m pytest tests/test_lenovo_parser.py -v` для контроля регрессий.

1. **TDD-сначала**: добавить новые тесты на устойчивость (см. раздел 7) — они должны быть красными на текущем коде.
2. **Refactor parser**: переписать `src/vendors/lenovo/parser.py` под пункты 4.1–4.8 до зелёных новых тестов и сохранения зелёных старых.
3. **Update adapter**: обновить `can_parse()` в `src/vendors/lenovo/adapter.py` (пункт 4.9). Проверить, что `tests/test_can_parse_xfusion_huawei_disjoint.py` и любые тесты, дёргающие `LenovoAdapter.can_parse`, всё ещё зелёные.
4. **Polish**: обновить docstring модуля (`Sheet 'Quote', header row 5...`) — описать новый алгоритм. Удалить `_HEADER_ROW`, `_DATA_START_ROW`. Сохранить `_STOP_SENTINEL` как module-level константу.
5. **Full regression**: `python -m pytest tests/ -v --tb=short`. Должно быть полностью зелёное.
6. **Golden parity**: `python -m pytest tests/test_regression_lenovo.py -v` — все L1…L11 должны давать identical output (skip только если файлы недоступны локально, не fail).
7. **CHANGELOG**: добавить запись под `## [Unreleased] / ### Changed`:
   - `refactor(LenovoParser): убраны позиционные константы _HEADER_ROW/_DATA_START_ROW и индексы колонок; шапка ищется сканированием первых 30 строк по маркерам Part number/Product Description/Qty/Price/Export Control; колонки мапятся через col_map (как в HPE); fallback по листам если "Quote" отсутствует; can_parse() обновлён под новую логику. Контракт row dict не меняется, golden L1…L11 идентичны.`

## 9. Критерии готовности (definition of done)

- [ ] `_HEADER_ROW`, `_DATA_START_ROW` и хардкод-индексы колонок (`raw[0]`, `raw[2]`, …) удалены из `src/vendors/lenovo/parser.py`.
- [ ] Шапка находится сканированием первых 30 строк по маркерным заголовкам.
- [ ] Колонки читаются через `col_map[<name>]` после `.strip()`.
- [ ] Лист подбирается по приоритету `"Quote"` → fallback по `wb.sheetnames`; `ValueError` только если ни в одном листе шапки нет.
- [ ] Стоп-маркер `"terms and conditions"` (case-insensitive) на первой непустой ячейке.
- [ ] Пустые строки до первой data-строки пропускаются; пустые строки между data-строками включаются как разделители; одна пустая перед T&C тоже включается (поведение текущих тестов сохранено).
- [ ] `__row_index__` остаётся 1-based.
- [ ] `data_only=False` сохранён.
- [ ] Минимум 4 новых теста на устойчивость в `tests/test_lenovo_parser.py` зелёные.
- [ ] Все существующие тесты Lenovo (parser + normalizer + rules + regression) зелёные.
- [ ] Полный `python -m pytest tests/` зелёный.
- [ ] Golden L1…L11 идентичны до и после (если файлы доступны локально).
- [ ] `can_parse()` в `src/vendors/lenovo/adapter.py` обновлён.
- [ ] Запись в `CHANGELOG.md` под `## [Unreleased]` добавлена.

## 10. Открытые вопросы

Все ключевые факты о структуре Lenovo-файлов **проверены на 11 реальных эталонных файлах** L1.xlsx … L11.xlsx (`C:\Users\G\Desktop\INPUT\lenovo\`):

- Лист: во всех 11 файлах есть `"Quote"`. В 10 из 11 есть также `"Quote w availability"`. Служебные листы: `"Power Report"`, `"ConfigGroupView"`, `"Summary"`, `"Message History"`.
- Шапка: 0-based row 5 во всех 11. Заголовки: `Part number`, `Product Description`, `Qty`, `Price`, `Total Part Price`, `Export Control` — точные имена с указанной капитализацией.
- Объединённые колонки: между `Part number` и `Product Description` (col 1 = None), между `Product Description` и `Qty` (col 3 = None) — не нарушает `col_map`.
- Суб-шапка row 6: `[None, None, None, None, None, '(per unit)\nUS Dollar', '(quantity x unit price)\nUS Dollar', None, ...]`.
- Row 7: полностью пустая.
- Первая data-строка row 8: всегда CTO Part number в col 0 + `"Server : ..."` или `"Server <NN> ... : ..."` в col 2.
- Stop-маркер: `"TERMS AND CONDITIONS:"` (lowercase startswith ловит).
- Колонка `Total Part Price` во всех 11 файлах содержит формулу вида `=IF(ISNUMBER(F9),IF($E9*F9>0,$E9*F9,""),"")` — `data_only=False` действительно нужен, иначе вернётся `None`.

Что осталось как побочное наблюдение (не блокирующее):

- **README.md строка 130 устарел** — описывает Lenovo как `sheet "Configuration"` с колонками `"Option Name" / "Option ID"`, что противоречит фактическому парсеру (`"Quote"` + `"Part number" / "Product Description"`). Вне scope текущего рефакторинга, но имеет смысл попутно поправить README под новую (после рефакторинга) логику: «лист подбирается из приоритетного списка, шапка ищется по маркерам Part number / Product Description / Qty / Price / Export Control».
