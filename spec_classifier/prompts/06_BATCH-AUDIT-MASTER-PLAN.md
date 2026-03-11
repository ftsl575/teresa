# BATCH AUDIT — ANALYSIS & MASTER PLAN
**Модель:** Opus 4.6 | **Extended:** ON  
**Когда:** после прогона batch_audit.py, для анализа audit_report.json и генерации плана правок

**Файлы (обязательно):**
- `batch_audit.py` _(Cowork: прямой доступ)_
- `audit_report.json` (из OUTPUT/audit/)
- `audit_summary.xlsx` (из OUTPUT/audit/)
- репо _(Cowork: прямой доступ; claude.ai: teresa.zip)_

**Файлы (опционально):**
- `cluster_summary.xlsx`
- `*_audited.xlsx`

---

## ПРОМПТ

```
Ты — Senior Staff Engineer + Tech Lead + QA.
Контекст проекта: Teresa — пайплайн классификации оборудования (Dell/HPE/Cisco).

БИЗНЕС-ПРАВИЛА (не нарушать):
- LOGISTIC = только упаковка, документы, доставка
- Power cord, stacking cable, rail, bracket — HW, не LOGISTIC
- power_cord: hw_type=None (не cable)
- BASE без device_type — норма (E15 = инфо)
- BASE с device_type — валидно (BASE-*-DT-* YAML rules)
- blank_filler + ABSENT — заглушка в слоте, не ошибка (E16)
- Factory Integrated строки — CONFIG, AI не проверяет

АЛИАСЫ (не мисматч):
ram=memory, nic=network_adapter, raid_controller=storage_controller,
sfp_cable/fiber_cable=cable, drive_cage/bezel=chassis,
storage_nvme/storage_ssd/storage_hdd=storage_drive

ШАГИ:

ШАГ 1. ПРОАНАЛИЗИРУЙ ОТЧЁТ
Из audit_report.json прочитай:
A) meta — дата, модель, токены, стоимость
B) stats — by_vendor, by_file, by_tag
C) bugs — REAL_BUG / REVIEW_NEEDED / FALSE_POSITIVE, паттерн, count
D) yaml_candidates — AI_SUGGEST предложения (device_type + count)
E) rule_issues — E-коды с примерами (включая E18)
F) clusters — если есть: total_candidates, total_clusters

Из cluster_summary.xlsx (если есть):
- cluster_id, count, vendors, top_terms, proposed_device_type, confidence
- suggested_yaml_rule (готовые regex-кандидаты)

ШАГ 2. КЛАССИФИЦИРУЙ ПРОБЛЕМЫ

КАТЕГОРИЯ A — РЕАЛЬНЫЕ БАГИ В YAML:
Признак: AI_MISMATCH где AI явно прав. Требуют: правки rules/*.yaml

КАТЕГОРИЯ B — КАНДИДАТЫ НА НОВЫЕ ПРАВИЛА:
Признак: AI_SUGGEST с count > 5, или кластеры с высокой confidence.
Требуют: новые regex-правила в rules/*.yaml

КАТЕГОРИЯ C — ЛОЖНЫЕ СРАБАТЫВАНИЯ СКРИПТА:
Признак: AI_MISMATCH где пайплайн прав, AI не знает бизнес-логику.
Требуют: правки в batch_audit.py (ENTITY_TRUST_PIPELINE, DEVICE_TYPE_ALIASES)

Таблица: | # | Категория | Паттерн | Кол-во | Вендор | Пример | Целевой файл |

ШАГ 3. СГЕНЕРИРУЙ MASTER PLAN ДЛЯ CURSOR
НЕ пиши код. Только план с acceptance criteria.

Формат:

WINDOW_NAME: BATCH AUDIT — MASTER PLAN FOR CURSOR
DATE: [дата]

A) SCOPE
In-scope: rules/*.yaml (если есть правки), batch_audit.py (если есть правки)
Out-of-scope: src/ (ядро — не трогать), docs/, cluster_audit.py

B) ФАЗА P0 — БЛОКЕРЫ
┌─────────────────────────────────────────────────────┐
│ Шаг: N — название                                   │
│ What / Why / Файл / Где именно                      │
│ Пример проблемной строки: "…"                       │
│ Ожидаемый результат: entity_type X→Y, device_type A→B│
│ AC-1: строка "…" больше не получает AI_MISMATCH     │
│ AC-2: batch_audit.py завершается без ошибок         │
│ Validation: python batch_audit.py --output-dir OUTPUT --vendor X │
└─────────────────────────────────────────────────────┘

C) ФАЗА P1 — НОВЫЕ ПРАВИЛА (из cluster_summary + yaml_candidates)
Для кластеров с confidence и count > 5:
- Suggested YAML rule из cluster_summary
- rule_id, секция, AC

D) ФАЗА P2 — УЛУЧШЕНИЯ СКРИПТА (ложные срабатывания)

E) ПОЛНЫЙ СПИСОК ФАЙЛОВ К ИЗМЕНЕНИЮ

F) CURSOR PROMPT (готовый промпт)
--- НАЧАЛО ---
Работай строго по плану. ТОЛЬКО файлы из секции E.
НЕ трогай src/. НЕ меняй структуру YAML — только добавляй/правь правила.
Порядок: специфичные паттерны ПЕРЕД generic (first-match-wins).
После каждого шага: python batch_audit.py --output-dir OUTPUT --no-ai
[MASTER PLAN секции A–E]
--- КОНЕЦ ---

G) РИСКИ

ШАГ 4. SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

## ЧТО СОХРАНИТЬ
- `batch_audit_master_plan.txt` — полный Master Plan
- `cursor_batch_audit_prompt.txt` — только CURSOR PROMPT из секции F
