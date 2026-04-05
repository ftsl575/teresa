# COWORK OPUS — АУДИТ OPUS-ШАГОВ (1B, 1D, 1E, 1F) + СРАВНЕНИЕ С SONNET
**Модель:** Opus 4.6 | **Extended:** ON
**Папка результатов:** OUTPUT\opus run\
**Что делает:** запускает только шаги, требующие Opus (глубокий анализ).
Sonnet-шаги (1A — метрики, 1C — чеклист) уже выполнены и лежат в OUTPUT\.

---

## КАК ИСПОЛЬЗОВАТЬ

1. Открой новое окно Cowork с моделью **Opus 4.6**
2. Вставь текст ниже как первое сообщение — Opus сам попросит подключить папки
3. Подключи папки когда он попросит: `teresa` и `OUTPUT`

---

## ПРОМПТ (вставить в новое окно целиком)

```
Ты — старший аудитор проекта Teresa. Твоя задача — выполнить шаги аудита,
требующие глубокого анализа (1B, 1D, 1E, 1F), затем сравнить с уже
готовыми Sonnet-результатами и дать финальное заключение.

────────────────────────────────────────────────
ШАГ 0 — ПОДКЛЮЧЕНИЕ ПАПОК
────────────────────────────────────────────────

Прежде чем начать, мне нужен доступ к файлам.
Пожалуйста, подключи две папки через кнопку выбора папки в интерфейсе:

1. Папка с репозиторием — C:\Users\G\Desktop\teresa
   (содержит spec_classifier/ с кодом, правилами, тестами, документацией)

2. Папка с результатами — C:\Users\G\Desktop\OUTPUT
   (содержит результаты прогонов и уже готовые Sonnet-файлы аудита)

После подключения напиши "папки подключены" — и я начну аудит.

────────────────────────────────────────────────
КОНТЕКСТ ПРОЕКТА
────────────────────────────────────────────────

Teresa — детерминированный пайплайн классификации оборудования из Excel BOM.
Вендоры: Dell, Cisco, HPE, Lenovo.
Классификация по полям:
  entity_type: BASE / HW / CONFIG / SOFTWARE / SERVICE / LOGISTIC / NOTE / UNKNOWN
  hw_type: server / switch / cpu / memory / gpu / storage_drive / …
  device_type: ram / nic / raid_controller / power_cord / …
  state: PRESENT / ABSENT

БИЗНЕС-ПРАВИЛА (не нарушать при аудите):
- LOGISTIC = только упаковка, документы, доставка
- Power cord, stacking cable, rail, bracket → HW, не LOGISTIC
- power_cord: hw_type=None (не cable)
- BASE без device_type → норма (E15 = инфо)
- BASE с device_type → валидно (BASE-*-DT-* YAML rules)
- blank_filler + ABSENT → заглушка, не ошибка (E16)
- Factory Integrated → CONFIG, не проверяется AI
- hw_type applies_to: [HW] (не [HW, BASE])

АЛИАСЫ device_type (одно и то же, не мисматч):
ram=memory, nic=network_adapter, raid_controller=storage_controller,
sfp_cable/fiber_cable=cable, drive_cage/bezel=chassis,
storage_nvme/storage_ssd/storage_hdd=storage_drive

E-КОДЫ batch_audit:
E2=UNKNOWN (BLOCKER), E6=entity не в (HW/LOGISTIC/BASE)+device_type (P0),
E13=LOGISTIC с физическим кабелем (P0), E14=CONFIG похож на blank_filler (P1),
E15=BASE без device_type (INFO), E16=blank_filler+ABSENT (INFO),
E17=HW без определённого типа (P1), E18=LOGISTIC с physical keyword (P0)

────────────────────────────────────────────────
ЗАДАНИЕ
────────────────────────────────────────────────

Выполни шаги 1B → 1D → 1E → 1F последовательно.
После каждого шага сохраняй файл в OUTPUT/opus run/.
Шаги 1A и 1C пропускаем — они уже выполнены Sonnet и лежат в OUTPUT/.
Никаких правок кода — только аудит и факты с доказательствами.

────────────────────────────────────────────────
ШАГ 1B — Архитектура и расширяемость
Сохранить: OUTPUT/opus run/audit_1B.txt
────────────────────────────────────────────────

Ты — Tech Lead + QA. Никаких правок, только аудит.

Прочитай ТОЛЬКО:
- src/core/classifier.py
- src/core/normalizer.py
- src/core/parser.py
- src/vendors/ (все .py)
- rules/ (все *.yaml/*.yml)
- src/outputs/annotated_writer.py

Ответь:
1) Есть ли vendor-specific знание в classifier/normalizer? (файл+фрагмент)
2) core/parser.py — это действительно общий парсер или фактически dell-specific?
3) VendorAdapter ABC: список абстрактных методов и проверка реализаций в Dell/Cisco/HPE/Lenovo.
4) can_parse: позитивная сигнатура у каждого?
5) get_extra_cols(): реализован ли в каждом адаптере?
6) Добавление нового (5-го) вендора: сколько файлов создать/редактировать?
   Нужны ли правки в batch_audit/cluster_audit? (ожидание: нет)
7) batch_audit.py и cluster_audit.py: подтверди что vendor-agnostic рефакторинг
   работает. Проверь:
   - DEVICE_TYPE_MAP загружается из YAML (не хардкод)?
   - --vendor choices динамические из config.yaml?
   - detect_vendor_from_path() принимает known_vendors?
   - E4 state logic использует E4_STATE_VALIDATORS dict (не if/elif цепочку)?
   - Есть ли KNOWN_FP_CASES для новых вендоров (Lenovo)?

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)

────────────────────────────────────────────────
ШАГ 1D — Стыки модулей (anti-hidden bugs)
Сохранить: OUTPUT/opus run/audit_1D.txt
────────────────────────────────────────────────

Ты — QA по "стыкам". Прочитай ТОЛЬКО:
- src/core/classifier.py
- src/core/normalizer.py
- src/outputs/ (все writer'ы)
- src/vendors/hpe/ (все .py)
- rules/hpe_rules.yaml
- batch_audit.py (функции find_annotated_files, validate_row, _generate_human_report)
- cluster_audit.py (функции load_candidate_rows, write_cluster_summary)

Проведи две цепочки и найди разрывы:

ЦЕПОЧКА 1: Основной пайплайн (HW-item от xlsx до outputs)
1) parser: какие поля читает/пишет для HPE
2) normalizer: какие поля гарантирует (включая vendor extension поля)
3) classifier: какие поля читает и как выбирает applies_to
4) writers: какие поля теряются/где (annotated, cleaned_spec, unknown_rows)

ЦЕПОЧКА 2: Audit-слой (annotated.xlsx → batch_audit → cluster_audit)
1) batch_audit: какие колонки читает из *_annotated.xlsx?
   Что происходит если колонки нет (KeyError vs graceful)?
2) batch_audit → *_audited.xlsx: какие колонки добавляются?
3) cluster_audit: читает ли он *_audited.xlsx или *_annotated.xlsx?
4) cluster_summary.xlsx: есть ли поля для передачи в Cursor как YAML-кандидаты?

Выдай список разрывов P0/P1/P2 с доказательствами.

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)

────────────────────────────────────────────────
ШАГ 1E — Документация как контракт
Сохранить: OUTPUT/opus run/audit_1E.txt
────────────────────────────────────────────────

Ты — аудитор документации. Никаких правок, только расхождения с доказательствами.
Прочитай ТОЛЬКО:
- docs/DOCS_INDEX.md
- docs/user/USER_GUIDE.md
- docs/user/CLI_CONFIG_REFERENCE.md
- docs/user/RUN_PATHS_AND_IO_LAYOUT.md
- docs/product/TECHNICAL_OVERVIEW.md
- docs/schemas/DATA_CONTRACTS.md
- docs/taxonomy/hw_type_taxonomy.md
- CURRENT_STATE.md
- CHANGELOG.md
- README.md

Проверь:
1) CHANGELOG.md: есть секция [Unreleased]? Запись после [1.3.0]?
2) CURRENT_STATE.md: версия, дата, список вендоров актуальны?
3) INPUT layout: документы описывают плоскую структуру или с подпапками (dell/, cisco/, hpe/)?
4) batch_audit.py и cluster_audit.py в документации:
   - README: упомянут E18? audit-слой описан?
   - RUN_PATHS: описаны audit_report.json, audit_summary.xlsx, cluster_summary.xlsx, *_audited.xlsx?
   - DATA_CONTRACTS: есть схема audit_report.json и cluster_summary.xlsx?
   - DOCS_INDEX: есть ссылка на cluster_audit.py?
5) CLI --vendor enum соответствует факту (dell/cisco/hpe/lenovo)?
6) Устаревшие формулировки без полного списка вендоров.
   Проверить что ВСЕ документы упоминают Lenovo где перечислены вендоры.
7) hw_type_taxonomy.md: power_cord=None, applies_to=[HW] — синхронизировано с кодом?

Формат: RESULTS (таблица: документ → проблема → цитата → риск) + SUMMARY

────────────────────────────────────────────────
ШАГ 1F — Тесты и ловушки разработки
Сохранить: OUTPUT/opus run/audit_1F.txt
────────────────────────────────────────────────

Ты — QA по тестам и процессу. Никаких правок.
Прочитай ТОЛЬКО:
- tests/ (все test_*.py)
- conftest.py
- scripts/ (все .py и .ps1)
- .gitignore
- config.yaml

Задачи:
1) Покрытие по вендорам: симметрия тестов между Dell/Cisco/HPE/Lenovo.
   Для каждого вендора проверить наличие: rules_unit, normalizer, parser.
   Проверь: есть ли assertions на device_type/hw_type в test_hpe_rules_unit.py?

2) Покрытие audit-слоя:
   - Есть ли тесты для batch_audit.py? (E18, динамический REAL_BUG)
   - Есть ли тесты для cluster_audit.py? (load_candidate_rows, heuristic_mapping)

3) Skip guard: conftest.py проверяет per-vendor subdirs или только root?
   Сколько HPE runtime cases (с учётом parametrize)?

4) Слепые зоны: нет ли schema validation, проверки rule_id формата, обработки битых xlsx.

5) ВАЖНО: отличай "файл есть в репо" от "файл tracked в git".
   Если утверждаешь tracked — дай доказательство (git ls-files) или пометь НЕПОДТВЕРЖДЕНО.

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)

────────────────────────────────────────────────
ФИНАЛЬНЫЙ БЛОК — СРАВНЕНИЕ И ЗАКЛЮЧЕНИЕ
Сохранить: OUTPUT/opus run/сравнение_opus_vs_sonnet.txt
────────────────────────────────────────────────

Прочитай Sonnet-результаты из OUTPUT/:
  audit_1A.txt, audit_1B.txt, audit_1C.txt, audit_1D.txt,
  audit_1E.txt, audit_1F.txt, результат_шаг1G.txt

Составь итоговый отчёт из трёх частей:

ЧАСТЬ 1 — СРАВНЕНИЕ OPUS VS SONNET (по шагам 1B, 1D, 1E, 1F):
Для каждого шага таблица:
| Находка | Sonnet | Opus | Вердикт |
Вердикт: "совпало" / "Opus глубже" / "Sonnet нашёл, Opus пропустил"

ЧАСТЬ 2 — СВОДНЫЙ АУДИТ (объединяем всё):
Используй:
- 1A и 1C: из Sonnet (метрики и чеклист — не требуют переоценки)
- 1B, 1D, 1E, 1F: лучшие находки из обоих прогонов

Составь финальный список:
BLOCKERS (P0): …
IMPORTANT (P1): …
NICE (P2): …

AUDIT_STATUS: PASS / FAIL

ЧАСТЬ 3 — ЗАКЛЮЧЕНИЕ: ГОТОВЫ ЛИ МЫ К СЛЕДУЮЩЕМУ ШАГУ?

Следующий шаг после аудита — 02_MASTER-PLAN вариант B:
генерация плана для Cursor по устранению всех P0 блокеров.

Дай однозначный ответ на вопрос:

  ГОТОВЫ К MASTER PLAN B? ДА / НЕТ / УСЛОВНО

Обоснование (не более 5 пунктов):
- Что подтверждает готовность
- Что мешает (если НЕТ или УСЛОВНО)
- Есть ли P0, которые Cursor НЕ должен трогать (слишком рискованно без доп. контекста)
- Рекомендуемый первый шаг в Master Plan

Сохрани отчёт в OUTPUT/opus run/сравнение_opus_vs_sonnet.txt
```
