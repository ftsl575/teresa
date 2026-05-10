# DOC UPDATE — MASTER PLAN GENERATOR
**Модель:** Opus 4.6 | **Extended:** ON  
**Когда:** после того как 1A–1G = PASS, все P0 закрыты, тесты зелёные

**Файлы (обязательно):**
- репо _(Cowork: прямой доступ; claude.ai: teresa.zip)_
- `SESSION_SUMMARY.md` или `work_report_audit_1G_complete.txt` — что было сделано

**Файлы (опционально):**
- OUTPUT _(Cowork: прямой доступ; claude.ai: OUTPUT.rar)_ — последний прогон
- `результат_шаг1G.txt` — отчёт аудита

---

## ПРОМПТ

```
Ты — Senior Tech Writer + Staff Engineer. Никаких правок кода. Только документация.

Задача: составить MASTER PLAN для Cursor — обновить docs/ после завершённого цикла фиксов.

ШАГ 1. ПРОЧИТАЙ ИСТОЧНИКИ ИСТИНЫ

A) Прочитай ВСЕ docs/ _(Cowork: прямой доступ; claude.ai: из teresa.zip)_:
   CURRENT_STATE.md, CHANGELOG.md, README.md
   docs/user/USER_GUIDE.md, CLI_CONFIG_REFERENCE.md, RUN_PATHS_AND_IO_LAYOUT.md
   docs/product/TECHNICAL_OVERVIEW.md
   docs/schemas/DATA_CONTRACTS.md
   docs/dev/TESTING_GUIDE.md, CONTRIBUTING.md
   docs/DOCS_INDEX.md
   (если каких-то нет — отметь MISSING)

B) Прочитай изменённый код _(Cowork: прямой доступ; claude.ai: из teresa.zip)_:
   batch_audit.py, cluster_audit.py, rules/*.yaml, src/outputs/annotated_writer.py

C) Из work_report / SESSION_SUMMARY собери:
   - список изменённых файлов
   - что именно изменилось (новые E-коды, алиасы, правила)
   - новые артефакты/поля/CLI-опции

ШАГ 2. АНАЛИЗ РАСХОЖДЕНИЙ

Таблица: | Документ | Нужно обновить? | Что устарело/отсутствует |

Правила YES:
- Нет [Unreleased] в CHANGELOG → YES
- CURRENT_STATE: неактуальная дата/вендоры → YES
- Не упомянут Lenovo в списке вендоров → YES
- Не упомянут E18 → YES
- Не описан cluster_audit.py → YES
- Нет audit_report.json / cluster_summary.xlsx в OUTPUT layout → YES
- Нет схем в DATA_CONTRACTS → YES
- power_cord или stacking cable как LOGISTIC → YES

ШАГ 3. MASTER PLAN ДЛЯ CURSOR

ЖЁСТКОЕ ПРАВИЛО: только точечные правки содержимого.
ЗАПРЕЩЕНО: переименовывать разделы, менять порядок секций, удалять разделы,
менять форматирование таблиц/списков.

Формат:

WINDOW_NAME: DOC UPDATE — MASTER PLAN
DATE: [дата]

A) SCOPE
In-scope: [список docs с YES]
Out-of-scope: любые правки кода, docs со статусом NO

B) ФАЗЫ

ФАЗА 1 — КРИТИЧНО:
┌─────────────────────────────────────────────────────┐
│ Документ: <файл>                                    │
│ What / Why / Section                                │
│ Old text (≤2 строки): "…"                          │
│ New text: "…"                                       │
│ AC-1: … AC-2: …                                    │
│ Validation: grep / открыть и проверить              │
└─────────────────────────────────────────────────────┘

ФАЗА 2 — ВАЖНО (тот же формат)
ФАЗА 3 — NICE (тот же формат)

C) ПОЛНЫЙ СПИСОК ФАЙЛОВ К ИЗМЕНЕНИЮ

D) CURSOR PROMPT
--- НАЧАЛО ---
Работай строго по плану. ТОЛЬКО файлы из раздела C. Никаких правок кода.
ЗАПРЕЩЕНО: менять структуру документов, переименовывать разделы,
менять порядок секций, удалять разделы, менять форматирование.
Разрешено ТОЛЬКО: заменить устаревший текст на новый в указанном месте.
После каждого документа: проверь что структура не изменилась,
все 4 вендора (Dell, Cisco, HPE, Lenovo) упомянуты там где нужно.
[MASTER PLAN секции A, B, C]
--- КОНЕЦ ---

E) РИСКИ

ШАГ 4. SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

## ЧТО СОХРАНИТЬ
- `plan_doc_update_post_audit.txt` — полный Master Plan
- `cursor_doc_prompt.txt` — только CURSOR PROMPT из секции D
