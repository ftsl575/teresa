# Codebase Structure

**Analysis Date:** 2026-05-04

## Directory layout

```
teresa/
├── spec_classifier/           # Основной пакет приложения
│   ├── main.py                # CLI: пайплайн классификации
│   ├── batch_audit.py         # Аудит выходов (E-коды, опц. AI)
│   ├── cluster_audit.py       # Кластеризация проблемных строк
│   ├── config.yaml            # Базовый конфиг + vendor_rules
│   ├── config.local.yaml      # Локально (gitignore), пример — *.example в репо
│   ├── requirements.txt
│   ├── conftest.py
│   ├── rules/                 # <vendor>_rules.yaml (6 вендоров)
│   ├── golden/                # *_expected.jsonl для регрессии
│   ├── prompts/               # Промпты для AI-разработки (не runtime)
│   ├── docs/                  # Документация (может отставать от кода)
│   ├── scripts/               # Вспомогательные скрипты
│   ├── tests/                 # pytest
│   └── src/
│       ├── core/              # classifier, normalizer, parser, state_detector
│       ├── vendors/           # dell, cisco, hpe, lenovo, huawei, xfusion + base.py
│       ├── rules/             # rules_engine.py
│       ├── outputs/           # excel / annotated / branded writers, json_writer
│       └── diagnostics/       # run_manager, stats_collector
├── run.ps1                    # Единая точка полного прогона
├── teresa_gui.py              # PyQt6 GUI → spawn run.ps1
├── teresa.bat
├── requirements-gui.txt
├── LAUNCHER_README.md
├── README.md                  # Минимальный заголовок (см. drift)
└── CLAUDE.md                  # Контекст для AI (в корне / дубли по смыслу в spec_classifier/)
```

## Directory purposes

**`spec_classifier/src/vendors/`:**
- Один подпакет на вендор: `adapter.py`, обычно `parser.py`, `normalizer.py`.
- `base.py` — абстрактный `VendorAdapter`.

**`spec_classifier/rules/`:**
- Источник истины для классификации по вендору; пути задаются в `config.yaml` → `vendor_rules`.

**`spec_classifier/golden/`:**
- Эталоны JSONL для сравнения с прогоном; покрытие см. имена файлов (Dell dl*, Cisco ccw_*, HPE hp*, Lenovo L*, Huawei hu*, xFusion xf*).

**`spec_classifier/prompts/`:**
- Документация и шаблоны для работы с Cursor/Claude; **не часть исполняемого пайплайна**.

**`spec_classifier/tests/`:**
- Зеркало доменов: парсеры, нормализаторы, правила, регрессия, аудиты, writers.

## Key file locations

**Entry points:**
- `spec_classifier/main.py`, `run.ps1`, `teresa_gui.py`, `batch_audit.py`, `cluster_audit.py`.

**Configuration:**
- `spec_classifier/config.yaml`, `spec_classifier/config.local.yaml` (локально).

**Core classification:**
- `spec_classifier/src/core/classifier.py`, `state_detector.py`, `normalizer.py`.
- `spec_classifier/src/rules/rules_engine.py`.

## Naming conventions

**Python modules:** `snake_case.py` в `src/` и тестах `test_*.py`.

**Rules:** `<vendor>_rules.yaml`.

**Golden:** `<stem>_expected.jsonl` согласован с именами входных книг в тестах.

## Where to add new code

**Новый вендор:** адаптер и правила в `src/vendors/<name>/`, строка в `vendor_rules` и `VENDOR_REGISTRY` в `main.py`, YAML в `rules/`, тесты и golden по принятому шаблону; лаунчер — списки вендоров в `run.ps1` и GUI.

**Новое правило классификации:** правки в соответствующем `rules/<vendor>_rules.yaml` и регрессионные тесты.

---

*Structure analysis: 2026-05-04*
