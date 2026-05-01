# ШАГ 0 — VENDOR RECONNAISSANCE
**Модель:** Opus 4.6 | **Extended:** ON
**Файлы:** teresa.zip + 2-5 примеров xlsx нового вендора (например `huawei_*.xlsx`)
**Когда:** ПЕРЕД 01_PRE-CHECK и 02_MASTER-PLAN, при добавлении нового вендора.

**Цель:** превратить «куча файлов от вендора» в `VENDOR_FORMAT_SPEC.md` —
структурированный документ, по которому Window 3 (Master Plan) сможет
сгенерировать корректный план для Cursor без догадок.

---

## ПРОМПТ

```
Ты — Senior Staff Engineer + Data Reverse-Engineer. Никаких правок кода.
Я даю тебе репо teresa.zip и N примеров xlsx нового вендора <VENDOR>.
Твоя задача — выдать VENDOR_FORMAT_SPEC.md.

КОНТЕКСТ ПРОЕКТА (бизнес-правила и таксономия):
- Прочитай docs/taxonomy/hw_type_taxonomy.md — особенно строки про <VENDOR>:
  он может быть split (например Huawei → СХД OceanStor vs WLAN — это
  разные форматы xlsx, разные адаптеры или режимы одного адаптера).
- Прочитай docs/dev/NEW_VENDOR_GUIDE.md — это инструкция по добавлению.
  ВНИМАНИЕ: гайд содержит drift — пункт про VENDOR_EXTRA_COLS
  устарел; правильный паттерн — VendorAdapter.get_extra_cols().
- Прочитай docs/schemas/DATA_CONTRACTS.md — обязательные поля
  NormalizedRow.

ЭТАЛОННЫЕ АДАПТЕРЫ (выбери ближайший по структуре файла):
- src/vendors/dell/   — column-sentinel «Module Name», positional cols
- src/vendors/cisco/  — лист «Price Estimate», иерархия групп
- src/vendors/hpe/    — лист «BOM», col_map по имени, EOF по «Total»
- src/vendors/lenovo/ — лист «Quote», fixed col-index, header_row=5,
                       stop-sentinel «terms and conditions»
                       (САМЫЙ свежий, шаблон по дефолту)

────────────────────────────────────────────────────────────
ШАГ 1 — РАЗВЕДКА ФОРМАТА
────────────────────────────────────────────────────────────

По каждому xlsx-примеру выдай таблицу:
| Файл | Sheet names | Header row (0-based) | Data start row | Stop sentinel |

Если форматов несколько (Huawei СХД vs WLAN) — РАЗДЕЛИ их сразу.
Каждый формат = отдельный VENDOR_FORMAT_SPEC, либо один с явным
режимом/детекцией.

────────────────────────────────────────────────────────────
ШАГ 2 — POSITIVE can_parse SIGNATURE
────────────────────────────────────────────────────────────

Сформулируй УНИКАЛЬНЫЙ маркер этого вендора:
- имя листа? (предпочтительно — как у Lenovo: "Quote")
- содержимое конкретной ячейки в шапке? (как у Lenovo:
  row 0 col 2 содержит "Data Center Solution Configurator")
- сочетание лист+ячейка?

ЗАПРЕЩЕНО: «not Dell and not HPE → значит Huawei» (negative identity).
Сигнатура должна быть positive и НЕ пересекаться с Dell/Cisco/HPE/Lenovo.

────────────────────────────────────────────────────────────
ШАГ 3 — КОЛОНКИ И ИХ МАППИНГ В NormalizedRow
────────────────────────────────────────────────────────────

Таблица:
| Колонка в xlsx | Тип | NormalizedRow поле | Vendor extension? |

Обязательные core-поля (см. DATA_CONTRACTS.md):
source_row_index, row_kind, group_name, group_id, product_name,
module_name, option_name, option_id, skus, qty, option_price.

Поля, которых НЕТ в core, но они есть в xlsx → vendor extension
(как Lenovo.export_control, HPE.product_type/extended_price/lead_time/
config_name/is_factory_integrated, Cisco.line_number/service_duration_months).
Их потом адаптер вернёт в get_extra_cols().

────────────────────────────────────────────────────────────
ШАГ 4 — КЛАССИФИКАЦИЯ: что в YAML rules
────────────────────────────────────────────────────────────

Просканируй option_name / option_id / SKU паттерны и предложи:

A) BASE rules — какие SKU/паттерны идентифицируют сервер/СХД/AP-узел
   (для Lenovo это `^[A-Z0-9]{4}CTO`, для Dell — sentinel «Module Name»).

B) entity_type spread:
   Какие строки SERVICE (warranty/support)?
   Какие SOFTWARE (license/firmware)?
   Какие LOGISTIC (shipping/freight/delivery)?
   Какие NOTE (информационные строки без SKU)?

C) device_type rules — список уникальных устройств в примерах:
   cpu, ram/memory, gpu, storage_drive, raid_controller, hba, nic,
   transceiver, cable, psu, fan, heatsink, riser, rail, backplane,
   chassis, tpm, battery, blank_filler, accessory, ...
   + особенности из таксономии (для Huawei СХД: io_module).

D) hw_type_rules.device_type_map — маппинг device_type → hw_type
   (см. lenovo_rules.yaml:670-693 как самый свежий шаблон).

E) Бизнес-нюансы вендора, которые НЕ вписываются в общие правила
   (Lenovo: все строки PRESENT, нет ABSENT; HPE: Factory Integrated;
   Dell: Configure-to-Order). У Huawei — что? Опиши явно.

────────────────────────────────────────────────────────────
ШАГ 5 — КОНФИГ vs КОД (граф изменений)
────────────────────────────────────────────────────────────

Конкретный список «что создать» и «что отредактировать»:

СОЗДАТЬ:
- src/vendors/<vendor>/__init__.py
- src/vendors/<vendor>/parser.py
- src/vendors/<vendor>/normalizer.py     (если нужны vendor extension поля)
- src/vendors/<vendor>/adapter.py
- rules/<vendor>_rules.yaml
- tests/test_<vendor>_parser.py
- tests/test_<vendor>_normalizer.py      (если есть extension поля)
- tests/test_<vendor>_rules_unit.py
- tests/test_regression_<vendor>.py
- tests/test_unknown_threshold_<vendor>.py
- golden/<stem>_expected.jsonl  ← через `python main.py --save-golden`

ОТРЕДАКТИРОВАТЬ (точечно, по 1-2 строки):
- main.py                    — VENDOR_REGISTRY[<vendor>] = <Vendor>Adapter
- config.yaml                — vendor_rules.<vendor>
- batch_audit.py             — E4_STATE_VALIDATORS[<vendor>] (тип stateset)
- batch_audit.py             — KNOWN_FP_CASES (если known false positives)
- conftest.py                — get_input_root_<vendor>() helper +
                               vendor_names list (строка 142, сейчас drift)
- run_audit.ps1              — добавить <vendor> в прогон (сейчас Lenovo
                               пропущен — drift, см. CLAUDE.md TechDebt #9)

NOT TOUCH:
- src/core/                  — ядро vendor-agnostic, не править
- src/outputs/annotated_writer.py — теперь параметризован extra_cols,
                                    редактировать НЕ надо

────────────────────────────────────────────────────────────
ШАГ 6 — ОТКРЫТЫЕ ВОПРОСЫ К ЧЕЛОВЕКУ
────────────────────────────────────────────────────────────

Список вопросов, на которые НЕ удалось ответить из примеров:
- сколько форматов у вендора (один или несколько)?
- ожидается ли branded_spec? (generates_branded_spec()=True/False)
- vendor_stats — какие метрики осмысленны для run_summary.json?
- есть ли state ABSENT, или все строки PRESENT (как у Lenovo)?
- что с export-control / lead-time / факторами, которые есть в xlsx?

────────────────────────────────────────────────────────────
ШАГ 7 — VENDOR_FORMAT_SPEC.md (финальный артефакт)
────────────────────────────────────────────────────────────

Собери всё в один markdown-документ со структурой:

# VENDOR_FORMAT_SPEC — <vendor>
## 1. Файлы-примеры (имена + краткое описание)
## 2. Формат xlsx (sheet, header row, data start, stop sentinel)
## 3. can_parse signature (точный код-сниппет на Python)
## 4. Колонки → NormalizedRow + vendor extensions
## 5. YAML rules — оценка количества правил по секциям
## 6. Бизнес-нюансы вендора
## 7. Список файлов для создания + редактирования (точные пути)
## 8. Открытые вопросы

В конце — обязательный SUMMARY:
CLAIMS / EVIDENCE / SEVERITY / ACTION

ACTION должен явно сказать: «готов передать VENDOR_FORMAT_SPEC.md
в Window 3 для генерации Master Plan по 02_MASTER-PLAN.md (variant A)»
ИЛИ
«нужны дополнительные примеры/ответы на вопросы из §6 перед
переходом к Master Plan».
```

## ЧТО СОХРАНИТЬ
- `VENDOR_FORMAT_SPEC.md` — это вход для Window 3
- `recon_summary.txt` — только SUMMARY-блок

## ЧТО ПОТОМ ПОЛУЧИТ WINDOW 3 (MASTER PLAN)
- `teresa.zip`
- `VENDOR_FORMAT_SPEC.md`
- промпт `02_MASTER-PLAN.md` (variant A), где в строке `[ВСТАВИТЬ ОПИСАНИЕ ФИЧИ]`
  вставить: `Добавить вендор <vendor> по спецификации из VENDOR_FORMAT_SPEC.md.`
