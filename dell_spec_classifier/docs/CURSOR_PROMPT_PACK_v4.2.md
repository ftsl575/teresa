# CURSOR PROMPT PACK — Dell Spec Classifier
## Версия: v4.2 (Fix 3 backward-compatible signature)
## Среда: Windows PowerShell + Cursor

---

## АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ

Действуют на протяжении всего пака. Вставлять в начало каждого промпта в Cursor.

```
ЗАПРЕЩЕНО трогать:
- src/core/*                        (parser, normalizer, classifier, state_detector)
- src/rules/*                       (rules_engine)
- golden/*                          (golden JSONL — обновление ЗАПРЕЩЕНО)
- dataclass ClassificationResult    (src/core/classifier.py)
- dataclass NormalizedRow           (src/core/normalizer.py)
- src/diagnostics/run_manager.py

РАЗРЕШЕНО в Prompt 1:
- src/outputs/annotated_writer.py   (Fix 1)
- src/outputs/json_writer.py        (Fix 2, Fix 3, Fix 6)
- main.py                           (Fix 1, Fix 3, Fix 4)
- config.yaml                       (Fix 5)
- .gitignore в корне репо           (Fix 7 — только если нужно)
- tests/                            (только чтение для понимания контекста, не изменять)

РАЗРЕШЕНО в Prompt 2:
- src/outputs/branded_spec_writer.py  (создать новый файл — не существует)
- main.py                             (только: добавить 1 импорт и 4 строки вызова)
- requirements.txt                    (ТОЛЬКО если openpyxl отсутствует — добавить строку "openpyxl>=3.1.0")
                                      Если openpyxl уже есть — requirements.txt не трогать.

РАЗРЕШЕНО в Prompt 3:
- tests/test_branded_spec_writer.py   (создать новый файл — не существует)
```

---

## GIT-СТРАТЕГИЯ

### Проверка чистоты перед стартом

```powershell
cd <корень репозитория>

# Проверить что нет изменённых tracked-файлов
git diff --name-only
# Вывод должен быть ПУСТЫМ.
# Если есть строки — остановиться и разобраться.

# Untracked файлы в output/, test_data/, *.xlsx — НЕ блокируют старт.
# git status может показывать их — это нормально.
```

### Создать baseline tag и рабочую ветку

```powershell
git checkout main
git pull
git log --oneline -1          # записать hash — это baseline
git tag baseline-before-prompts
git checkout -b feature/bugfix-and-branded-spec
```

### Коммиты после каждого блока

```powershell
# После Prompt 1:
git add src/outputs/annotated_writer.py `
        src/outputs/json_writer.py `
        main.py `
        config.yaml `
        .gitignore
# Добавлять только явно разрешённые файлы. git add src/ — ЗАПРЕЩЕНО.
git diff --name-only  # список должен быть пустым после add (только staged)
git commit -m "fix: 7 bugfixes — annotated path, NaN, source_row_index, run_summary, config cleanup, dedup, gitignore"

# После Prompt 2:
git add src/outputs/branded_spec_writer.py main.py
git diff --name-only  # пустой
git commit -m "feat: add branded_spec_writer module"

# После Prompt 3:
git add tests/test_branded_spec_writer.py
git diff --name-only  # пустой
git commit -m "test: add tests for branded_spec_writer"
```

**НЕ делать push** до финального прохода всех тестов.

**Правило перед каждым коммитом:**
```powershell
git diff --name-only
# Если в списке есть файлы вне разрешённого набора для текущего блока — остановиться и не коммитить.
```

### Откат

```powershell
# Откатить конкретный файл:
git checkout baseline-before-prompts -- src/outputs/json_writer.py

# Откатить всё:
git reset --hard baseline-before-prompts
```

---

## REGRESSION GATE

**Определение:** regression gate = запуск существующих тестов, которые сравнивают вывод пайплайна с golden/*.

```powershell
cd dell_spec_classifier
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v
```

**Правила:**
- Любой FAIL = **немедленная остановка**
- Обновлять `golden/*` в рамках этого пака **ЗАПРЕЩЕНО**
- Изменять `tests/test_regression.py` и `tests/test_dec_acceptance.py` **ЗАПРЕЩЕНО**
- Если regression падает после изменения — откатить и разобраться

**Запускается:**
1. До начала (baseline)
2. После Prompt 1 (полностью)
3. После Prompt 2
4. Финально после Prompt 3

---

## BASELINE — выполнить ДО начала изменений

```powershell
cd dell_spec_classifier

# 1. Все тесты зелёные
python -m pytest tests\ -q
# Записать результат: X passed, 0 failed

# 2. Regression gate зелёный
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v
# Все должны быть PASSED

# 3. Зафиксировать количество строк в golden (контрольная точка)
foreach ($f in Get-ChildItem golden\*_expected.jsonl) {
    $lines = (Get-Content $f.FullName | Where-Object { $_ -ne "" }).Count
    Write-Host "$($f.Name): $lines rows"
}
```

Только после зелёного baseline — переходить к Fix 1.

---

---

## PROMPT 1 — 7 фиксов

Каждый Fix = отдельное сообщение в Cursor. Перед каждым — вставить блок АРХИТЕКТУРНЫХ ОГРАНИЧЕНИЙ.

---

### Fix 1 — annotated.xlsx переместить в run_folder

**Файлы:** `src/outputs/annotated_writer.py`, `main.py`
**НЕ менять:** логику чтения/записи Excel, всё остальное в этих файлах.

**Текущее состояние:**

`annotated_writer.py` строка 21: `output_dir: Path`
`annotated_writer.py` строки 72–74:
```python
output_dir = Path(output_dir)
stem = path.stem
out_path = output_dir / f"{stem}_annotated.xlsx"
```

`main.py` строки 142–145:
```python
generate_annotated_source_excel(
    raw_rows, normalized_rows, classification_results, input_path, output_dir
)
```

**Что изменить:**

`annotated_writer.py`:
- строка 21: `output_dir: Path` → `run_folder: Path`
- строка 72: `output_dir = Path(output_dir)` → `run_folder = Path(run_folder)`
- строка 74: `out_path = output_dir / f"{stem}_annotated.xlsx"` → `out_path = run_folder / f"{stem}_annotated.xlsx"`
- строка 25 (docstring): `output_dir` → `run_folder`

`main.py`:
```python
# БЫЛО:
generate_annotated_source_excel(
    raw_rows, normalized_rows, classification_results, input_path, output_dir
)

# СТАЛО:
generate_annotated_source_excel(
    raw_rows, normalized_rows, classification_results, input_path, run_folder
)
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output

$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1

Test-Path "$($run.FullName)\dl1_annotated.xlsx"    # True
Test-Path "..\output\dl1_annotated.xlsx"           # False

python -m pytest tests\ -q
```

---

### Fix 2 — rows_raw.json: NaN → null

**Файл:** `src/outputs/json_writer.py`
**НЕ менять:** всё кроме функции `save_rows_raw`.

**Определение санации:** только `float` значения где `val != val` (IEEE 754 NaN). Не трогать: `""`, `None`, `0`, `False`, целые числа, строки.

**Текущее состояние** `save_rows_raw`:
```python
def save_rows_raw(rows: List[dict], run_folder: Path) -> None:
    path = Path(run_folder) / "rows_raw.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
```

**Заменить тело функции на:**
```python
def save_rows_raw(rows: List[dict], run_folder: Path) -> None:
    """Write raw parsed rows to rows_raw.json. float NaN replaced with null."""
    path = Path(run_folder) / "rows_raw.json"

    def _sanitize_nan(obj):
        """Replace float NaN with None only. str/int/bool/None unchanged."""
        if isinstance(obj, float) and obj != obj:
            return None
        if isinstance(obj, dict):
            return {k: _sanitize_nan(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize_nan(v) for v in obj]
        return obj

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_sanitize_nan(rows), f, indent=2, ensure_ascii=False)
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output

$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1

# JSON парсится без ошибок
python -c "import json; json.load(open(r'$($run.FullName)\rows_raw.json')); print('OK')"

# Литерал NaN отсутствует
$content = Get-Content "$($run.FullName)\rows_raw.json" -Raw
if ($content -match '(?<![\"a-zA-Z])NaN') { Write-Host 'FAIL: NaN literal found' } else { Write-Host 'OK: no NaN literal' }
```

---

### Fix 3 — source_row_index в classification.jsonl

**Файлы:** `src/outputs/json_writer.py`, `main.py`
**НЕ менять:** `ClassificationResult`, `NormalizedRow`, `src/core/*`, `tests/*`, порядок и логику других функций в json_writer.py.
**Точка внедрения:** только `_classification_result_to_dict` и `save_classification`.

**Инварианты classification.jsonl (не нарушать):**
- 1 JSON объект = 1 строка
- Без indent, без pretty-print
- UTF-8 encoding
- Каждая строка парсится независимо через `json.loads(line)`
- Поле `source_row_index` всегда присутствует в схеме (int или null — никогда не omit)

**Важно — backward compatibility:**
Существующие тесты вызывают `save_classification(results, run_folder)` (старая сигнатура из двух аргументов).
Функция должна принимать ОБЕ сигнатуры. Тесты трогать НЕЛЬЗЯ.

**Что изменить в `json_writer.py`:**

```python
# 1. Обновить импорты — добавить Optional и Union:
from typing import List, Optional, Union

# 2. Заменить функцию _classification_result_to_dict:
def _classification_result_to_dict(
    result: ClassificationResult,
    source_row_index: Optional[int] = None,
) -> dict:
    """Build dict for classification.jsonl.
    source_row_index is int when normalized_rows provided, null otherwise.
    Field is always present in output schema.
    """
    out = {
        "source_row_index": source_row_index,  # null when old call path, int when new
        "row_kind": result.row_kind.value,
        "entity_type": result.entity_type.value if result.entity_type else None,
        "state": result.state.value if result.state else None,
        "matched_rule_id": result.matched_rule_id,
        "warnings": result.warnings,
    }
    is_classified = (
        result.row_kind.value == "ITEM"
        and result.matched_rule_id != "UNKNOWN-000"
        and result.entity_type is not None
    )
    out["device_type"] = result.device_type if is_classified else None
    out["hw_type"] = getattr(result, "hw_type", None) if is_classified else None
    return out


# 3. Заменить функцию save_classification:
def save_classification(
    results: List[ClassificationResult],
    normalized_rows_or_run_folder: Union[List[NormalizedRow], Path],
    run_folder: Optional[Path] = None,
) -> None:
    """Write one JSON object per line to classification.jsonl.

    Backward-compatible signature:
      Old (smoke tests): save_classification(results, run_folder)
        → source_row_index: null in every row
      New (main.py):     save_classification(results, normalized_rows, run_folder)
        → source_row_index: int from normalized_rows[i].source_row_index
    """
    if isinstance(normalized_rows_or_run_folder, Path):
        # Old call path: second arg is run_folder
        actual_run_folder = normalized_rows_or_run_folder
        normalized_rows = None
    else:
        # New call path: second arg is normalized_rows
        normalized_rows = normalized_rows_or_run_folder
        actual_run_folder = run_folder
        assert len(results) == len(normalized_rows), \
            "Results and normalized_rows length mismatch"

    path = Path(actual_run_folder) / "classification.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for i, result in enumerate(results):
            source_row_index = (
                normalized_rows[i].source_row_index
                if normalized_rows is not None
                else None
            )
            line = json.dumps(
                _classification_result_to_dict(result, source_row_index),
                ensure_ascii=False,
            ) + "\n"
            f.write(line)
```

**Что изменить в `main.py`:**
```python
# БЫЛО:
save_classification(classification_results, run_folder)

# СТАЛО:
save_classification(classification_results, normalized_rows, run_folder)
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier

# 1. Полный тест-сьют — должен быть зелёным (включая smoke tests)
python -m pytest tests\ -q
# Ожидаемо: все passed, 0 failed

# 2. Прогон пайплайна
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output
$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1

# 3. Через main.py: source_row_index = int (не null)
python -c "
import json
lines = open(r'$($run.FullName)\classification.jsonl').readlines()
for i, line in enumerate(lines):
    obj = json.loads(line)
    assert 'source_row_index' in obj, f'Field missing at line {i}'
    assert isinstance(obj['source_row_index'], int), f'Expected int at line {i}, got: {obj[\"source_row_index\"]}'
print(f'OK: {len(lines)} lines, all source_row_index are int')
"

# 4. Число строк совпадает
python -c "
import json
cl = open(r'$($run.FullName)\classification.jsonl').readlines()
nr = json.load(open(r'$($run.FullName)\rows_normalized.json'))
assert len(cl) == len(nr), f'Length mismatch: {len(cl)} vs {len(nr)}'
print(f'OK: both have {len(cl)} rows')
"

# 5. Старый путь вызова (smoke-тест симуляция) — source_row_index = null
python -c "
import json, sys, tempfile
sys.path.insert(0, '.')
from pathlib import Path
from src.outputs.json_writer import save_classification
from src.core.classifier import ClassificationResult, EntityType
from src.core.normalizer import RowKind
from src.core.state_detector import State

result = ClassificationResult(RowKind.ITEM, EntityType.HW, State.PRESENT, 'HW-001')
with tempfile.TemporaryDirectory() as tmp:
    save_classification([result], Path(tmp))
    obj = json.loads(open(Path(tmp) / 'classification.jsonl').readline())
    assert 'source_row_index' in obj, 'Field must exist even on old path'
    assert obj['source_row_index'] is None, f'Expected null, got {obj[\"source_row_index\"]}'
    print('OK: old call path produces source_row_index: null')
"

# 6. Regression gate
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v
```

---

### Fix 4 — input_file и run_timestamp в run_summary.json

**Файл:** `main.py`
**НЕ менять:** `stats_collector.py`, структуру других артефактов.

**Контракт формата timestamp:** UTC, без микросекунд, ISO format.
Пример значения: `"2026-02-26T10:34:15"`

**Что изменить в `main.py`:**

1. В блок импортов (после `import sys`) добавить:
```python
from datetime import datetime
```

2. После строки `stats["rules_file_hash"] = compute_file_hash(str(rules_path))` добавить:
```python
stats["input_file"] = input_path.name
stats["run_timestamp"] = datetime.utcnow().replace(microsecond=0).isoformat()
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output

$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1

python -c "
import json
d = json.load(open(r'$($run.FullName)\run_summary.json'))
assert 'input_file' in d, 'Missing input_file'
assert 'run_timestamp' in d, 'Missing run_timestamp'
assert d['input_file'] == 'dl1.xlsx', f'Wrong: {d[\"input_file\"]}'
assert '.' not in d['run_timestamp'], f'Timestamp must not contain microseconds: {d[\"run_timestamp\"]}'
print('OK:', d['input_file'], d['run_timestamp'])
"
```

---

### Fix 5 — убрать exclude_headers из config.yaml

**Файл:** `config.yaml`
**НЕ менять:** всё остальное.

**Сначала убедиться что параметр нигде не используется:**
```powershell
Select-String -Path "dell_spec_classifier\src\**\*.py" -Pattern "exclude_headers" -Recurse
# Вывод должен быть пустым
```

**Что изменить:** удалить строку `  exclude_headers: true` из `config.yaml`

**Acceptance + regression (PowerShell):**
```powershell
Select-String -Path "dell_spec_classifier\config.yaml" -Pattern "exclude_headers"
# Пустой вывод

# Regression gate — убедиться что удаление не сломало контракт
cd dell_spec_classifier
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v
# Все PASSED
```

---

### Fix 6 — дедупликация if-блоков в json_writer.py

**Файл:** `src/outputs/json_writer.py`
**НЕ менять:** ничего кроме тела `_classification_result_to_dict`.

**Примечание:** если Fix 3 уже выполнен — функция уже содержит `is_classified`. Проверить:
```powershell
Select-String -Path "dell_spec_classifier\src\outputs\json_writer.py" -Pattern "is_classified"
# Если строка найдена — Fix 6 пропустить.
```

Если Fix 3 ещё не выполнен — заменить два идентичных if-блока для `device_type` и `hw_type` на:
```python
is_classified = (
    result.row_kind.value == "ITEM"
    and result.matched_rule_id != "UNKNOWN-000"
    and result.entity_type is not None
)
out["device_type"] = result.device_type if is_classified else None
out["hw_type"] = getattr(result, "hw_type", None) if is_classified else None
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python -m pytest tests\ -q
# Количество passed = baseline, 0 failed
```

---

### Fix 7 — __pycache__ в .gitignore

**Файл:** `.gitignore` в корне репозитория.

**Сначала проверить — возможно уже реализовано:**
```powershell
Select-String -Path ".gitignore" -Pattern "__pycache__"
# Если найдена строка — Fix 7 пропустить, ничего не менять.
```

Если вывод пустой — добавить в `.gitignore`:
```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
```

**Acceptance:**
```powershell
Select-String -Path ".gitignore" -Pattern "__pycache__"
# Хотя бы одна строка найдена
```

---

### Финальная проверка Prompt 1

```powershell
cd dell_spec_classifier

# Прогон пайплайна
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output

$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1
Write-Host "Run folder: $($run.FullName)"

# 1. annotated внутри run_folder
Test-Path "$($run.FullName)\dl1_annotated.xlsx"     # True
Test-Path "..\output\dl1_annotated.xlsx"            # False

# 2. rows_raw.json — валидный JSON без NaN
python -c "import json; json.load(open(r'$($run.FullName)\rows_raw.json')); print('rows_raw OK')"

# 3. source_row_index в каждой строке classification.jsonl
python -c "import json; [json.loads(l)['source_row_index'] for l in open(r'$($run.FullName)\classification.jsonl')]; print('classification OK')"

# 4. input_file и run_timestamp в run_summary.json
python -c "import json; d=json.load(open(r'$($run.FullName)\run_summary.json')); assert 'input_file' in d and 'run_timestamp' in d; print('run_summary OK')"

# 5. exclude_headers отсутствует
Select-String -Path "config.yaml" -Pattern "exclude_headers"   # пустой вывод

# 6. Все тесты зелёные
python -m pytest tests\ -q

# 7. Regression gate
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v

# 8. Diff scope — только разрешённые файлы изменены
git diff --name-only baseline-before-prompts
# Допустимо: src/outputs/annotated_writer.py, src/outputs/json_writer.py, main.py, config.yaml, .gitignore
# Недопустимо: src/core/*, tests/*, golden/*, rules/*
```

**Коммит:**
```powershell
cd ..
git add src/ main.py config.yaml .gitignore
git commit -m "fix: 7 bugfixes — annotated path, NaN, source_row_index, run_summary, config cleanup, dedup, gitignore"
```

---

---

## PROMPT 2 — Новый модуль: branded_spec_writer.py

**Перед началом — проверить зависимость:**
```powershell
Select-String -Path "dell_spec_classifier\requirements.txt" -Pattern "openpyxl"
# Должна быть найдена строка с openpyxl.
# Если отсутствует — добавить строку "openpyxl>=3.1.0" в requirements.txt перед продолжением.
```

---

### Шаг 2.1 — Создать файл модуля

Передать в Cursor:

> Создай файл `dell_spec_classifier/src/outputs/branded_spec_writer.py` с точным содержимым ниже. Ничего не добавляй, не изменяй, не сокращай. Не трогай никакие другие файлы.

```python
"""
Branded specification document: groups items by server (BASE) and entity type sections.
Output mirrors YADRO-style format with company brand colors.
"""

from pathlib import Path
from typing import List

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult, EntityType
from src.core.state_detector import State


# ── Toggle flags ────────────────────────────────────────────────────────────
SHOW_ABSENT_BLOCK = True   # Set False to hide "Не установлено" section

# ── Brand colors ────────────────────────────────────────────────────────────
C_PRIMARY       = "2A90D2"   # Primary blue — title, table header, BASE row
C_PRIMARY_LIGHT = "5DAFF8"   # Reserved
C_WHITE         = "FFFFFF"
C_ZEBRA         = "F0F7FF"   # Light blue tint for alternating rows

SECTION_COLORS = {
    EntityType.HW:       "B7DEFF",
    EntityType.CONFIG:   "E6E6FE",
    EntityType.SOFTWARE: "C7B7FE",
    EntityType.SERVICE:  "B3F4EC",
    EntityType.LOGISTIC: "E8E8E8",
    EntityType.NOTE:     "F5F5F5",
    EntityType.UNKNOWN:  "FFD0D0",
}

SECTION_LABELS = {
    EntityType.HW:       "Оборудование",
    EntityType.CONFIG:   "Конфигурация",
    EntityType.SOFTWARE: "Программное обеспечение",
    EntityType.SERVICE:  "Сервис и гарантия",
    EntityType.LOGISTIC: "Логистика",
    EntityType.NOTE:     "Примечания",
    EntityType.UNKNOWN:  "Нераспознанные позиции",
}

ABSENT_SECTION_COLOR = "F5E6E6"
ABSENT_SECTION_LABEL = "Не установлено / Не выбрано"

SECTION_ORDER = [
    EntityType.HW,
    EntityType.CONFIG,
    EntityType.SOFTWARE,
    EntityType.SERVICE,
    EntityType.LOGISTIC,
    EntityType.NOTE,
    EntityType.UNKNOWN,
]

COL_A_WIDTH  = 3.5
COL_B_WIDTH  = 23.0
COL_C_WIDTH  = 70.0
COL_D_WIDTH  = 12.0


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _font(bold=False, size=11, color="000000", italic=False) -> Font:
    return Font(name="Arial", bold=bold, size=size, color=color, italic=italic)


def _thin_border() -> Border:
    side = Side(style="thin", color="D0D0D0")
    return Border(bottom=side)


def _write_title(ws, row: int, source_name: str) -> int:
    cell = ws.cell(row=row, column=3, value=f"Спецификация на основе {source_name}")
    cell.font = Font(name="Arial", bold=True, size=18, color=C_PRIMARY)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 36
    return row + 2


def _write_table_header(ws, row: int) -> int:
    headers = {2: "Артикул", 3: "Наименование", 4: "Кол-во"}
    for col, text in headers.items():
        cell = ws.cell(row=row, column=col, value=text)
        cell.fill = _fill(C_PRIMARY)
        cell.font = _font(bold=True, size=11, color=C_WHITE)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
        cell.border = _thin_border()
    ws.row_dimensions[row].height = 20
    return row + 1


def _write_base_row(ws, row: int, option_name: str, skus: List[str], qty) -> int:
    ws.cell(row=row, column=2, value=", ".join(skus) if skus else "").fill = _fill(C_PRIMARY)
    ws.cell(row=row, column=3, value=option_name).fill = _fill(C_PRIMARY)
    ws.cell(row=row, column=4, value=qty).fill = _fill(C_PRIMARY)
    for col in (2, 3, 4):
        c = ws.cell(row=row, column=col)
        c.font = _font(bold=True, size=11, color=C_WHITE)
        c.alignment = Alignment(
            horizontal="left" if col < 4 else "center",
            vertical="center",
            wrap_text=False,
        )
    ws.row_dimensions[row].height = 18
    return row + 1


def _write_section_header(ws, row: int, entity_type: EntityType) -> int:
    label = SECTION_LABELS.get(entity_type, entity_type.value)
    bg = SECTION_COLORS.get(entity_type, "E0E0E0")
    for col in (2, 3, 4):
        c = ws.cell(row=row, column=col, value=label if col == 3 else None)
        c.fill = _fill(bg)
        c.font = _font(bold=True, size=10, italic=True)
        c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 16
    return row + 1


def _write_data_row(ws, row: int, skus: List[str], option_name: str, qty, zebra: bool) -> int:
    bg = C_ZEBRA if zebra else C_WHITE
    ws.cell(row=row, column=2, value=", ".join(skus) if skus else "").fill = _fill(bg)
    ws.cell(row=row, column=3, value=option_name).fill = _fill(bg)
    ws.cell(row=row, column=4, value=qty).fill = _fill(bg)
    for col in (2, 3, 4):
        c = ws.cell(row=row, column=col)
        c.font = _font(size=10)
        c.alignment = Alignment(
            horizontal="left" if col < 4 else "center",
            vertical="top",
            wrap_text=True,
        )
    ws.row_dimensions[row].height = None  # Excel autofit on open
    return row + 1


def generate_branded_spec(
    normalized_rows: List[NormalizedRow],
    classification_results: List[ClassificationResult],
    source_filename: str,
    output_path: Path,
) -> Path:
    """
    Build branded specification Excel.

    Groups rows by BASE; within each block renders sections in SECTION_ORDER.
    PRESENT rows only (NOTE/UNKNOWN always included — no state filter).
    ABSENT rows collected into separate block at end of each server block.
    Row height = None (Excel autofit on open).
    """
    output_path = Path(output_path)

    blocks = []
    current = None

    for nrow, result in zip(normalized_rows, classification_results):
        if result.row_kind != RowKind.ITEM:
            continue
        if result.entity_type == EntityType.BASE:
            current = {
                "base": (nrow, result),
                "sections": {et: [] for et in SECTION_ORDER},
                "absent": [],
            }
            blocks.append(current)
            continue
        if current is None:
            continue
        if result.entity_type is None:
            continue

        if result.state == State.ABSENT:
            current["absent"].append((nrow, result))
            continue

        if result.entity_type not in (EntityType.NOTE, EntityType.UNKNOWN):
            if result.state != State.PRESENT:
                continue

        et = result.entity_type
        if et in current["sections"]:
            current["sections"][et].append((nrow, result))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Спецификация"

    ws.column_dimensions["A"].width = COL_A_WIDTH
    ws.column_dimensions["B"].width = COL_B_WIDTH
    ws.column_dimensions["C"].width = COL_C_WIDTH
    ws.column_dimensions["D"].width = COL_D_WIDTH

    stem = Path(source_filename).stem
    current_row = 1
    current_row = _write_title(ws, current_row, stem)
    header_row = current_row
    current_row = _write_table_header(ws, current_row)
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)

    for block in blocks:
        base_nrow, _ = block["base"]
        current_row = _write_base_row(
            ws, current_row,
            option_name=base_nrow.option_name,
            skus=list(base_nrow.skus),
            qty=base_nrow.qty,
        )

        for entity_type in SECTION_ORDER:
            section_rows = block["sections"][entity_type]
            if not section_rows:
                continue
            current_row = _write_section_header(ws, current_row, entity_type)
            for zebra_idx, (nrow, _) in enumerate(section_rows):
                current_row = _write_data_row(
                    ws, current_row,
                    skus=list(nrow.skus),
                    option_name=nrow.option_name,
                    qty=nrow.qty,
                    zebra=(zebra_idx % 2 == 1),
                )

        if SHOW_ABSENT_BLOCK and block["absent"]:
            for col in (2, 3, 4):
                c = ws.cell(row=current_row, column=col,
                            value=ABSENT_SECTION_LABEL if col == 3 else None)
                c.fill = _fill(ABSENT_SECTION_COLOR)
                c.font = _font(bold=True, size=10, italic=True)
                c.alignment = Alignment(horizontal="left", vertical="center")
            ws.row_dimensions[current_row].height = 16
            current_row += 1
            for zebra_idx, (nrow, _) in enumerate(block["absent"]):
                current_row = _write_data_row(
                    ws, current_row,
                    skus=list(nrow.skus),
                    option_name=nrow.option_name,
                    qty=nrow.qty,
                    zebra=(zebra_idx % 2 == 1),
                )

        ws.row_dimensions[current_row].height = 8
        current_row += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(output_path))
    return output_path
```

**Acceptance (PowerShell):**
```powershell
Test-Path "dell_spec_classifier\src\outputs\branded_spec_writer.py"   # True

cd dell_spec_classifier
python -c "from src.outputs.branded_spec_writer import generate_branded_spec; print('import OK')"
```

---

### Шаг 2.2 — Подключить в main.py

Передать в Cursor:

> В файле `dell_spec_classifier/main.py` внести ровно два изменения. Ничего другого не трогать.
>
> **Изменение 1.** В блок импортов, сразу после строки:
> ```python
> from src.outputs.annotated_writer import generate_annotated_source_excel
> ```
> добавить новую строку:
> ```python
> from src.outputs.branded_spec_writer import generate_branded_spec
> ```
>
> **Изменение 2.** Найти в коде блок:
> ```python
>         generate_annotated_source_excel(
>             raw_rows, normalized_rows, classification_results, input_path, run_folder
>         )
>         log.info("Done.")
> ```
> Вставить следующие 6 строк между `generate_annotated_source_excel(...)` и `log.info("Done.")`:
> ```python
>         branded_path = run_folder / f"{input_path.stem}_branded.xlsx"
>         generate_branded_spec(
>             normalized_rows=normalized_rows,
>             classification_results=classification_results,
>             source_filename=input_path.name,
>             output_path=branded_path,
>         )
> ```
> Итоговый порядок строк должен быть:
> ```python
>         generate_annotated_source_excel(...)
>         branded_path = run_folder / f"{input_path.stem}_branded.xlsx"
>         generate_branded_spec(...)
>         log.info("Done.")
> ```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python main.py --input ..\test_data\dl1.xlsx --output-dir ..\output

$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1

Test-Path "$($run.FullName)\dl1_branded.xlsx"      # True
Test-Path "$($run.FullName)\dl1_annotated.xlsx"    # True (не сломан Fix 1)

python -c "
import openpyxl
wb = openpyxl.load_workbook(r'$($run.FullName)\dl1_branded.xlsx')
ws = wb.active
assert ws.max_row > 5, 'File seems empty'
print('Rows:', ws.max_row, '| Sheet:', ws.title)
"

# Regression gate — branded_spec не должен влиять на classification
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v

# Все тесты
python -m pytest tests\ -q

# Diff scope
git diff --name-only baseline-before-prompts
# Ожидаемо: src/outputs/branded_spec_writer.py, main.py (+ файлы из Prompt 1)
# Недопустимо: src/core/*, tests/*, golden/*, rules/*
```

**Коммит:**
```powershell
cd ..
git add src\outputs\branded_spec_writer.py main.py
git commit -m "feat: add branded_spec_writer module"
```

---

---

## PROMPT 3 — Тесты для branded_spec_writer

**НЕ менять** никакие существующие файлы. Только создать `tests/test_branded_spec_writer.py`.

Передать в Cursor:

> Создай файл `dell_spec_classifier/tests/test_branded_spec_writer.py`.
> Посмотри на стиль тестов в `tests/test_annotated_writer.py` для справки по структуре.
> Не меняй ни один существующий файл.
> Реализуй ровно 7 тест-кейсов:

```
Тест 1: test_branded_spec_creates_file
Входные данные: 1 BASE + 2 HW PRESENT
Проверить:
- файл создаётся по указанному пути
- openpyxl открывает файл без исключений
- ws.max_row > 0

Тест 2: test_branded_spec_absent_block_present
Входные данные: 1 BASE + 1 HW PRESENT + 1 HW ABSENT
SHOW_ABSENT_BLOCK = True (значение по умолчанию)
Проверить: среди значений всех ячеек файла есть строка "Не установлено / Не выбрано"

Тест 3: test_branded_spec_absent_block_hidden
Те же входные данные что в тесте 2
Перед вызовом: import src.outputs.branded_spec_writer as bsw; bsw.SHOW_ABSENT_BLOCK = False
После теста (в блоке finally или через fixture): bsw.SHOW_ABSENT_BLOCK = True
Проверить: строка "Не установлено / Не выбрано" НЕ присутствует ни в одной ячейке файла

Тест 4: test_branded_spec_only_present_in_sections
Входные данные: 1 BASE + 1 HW PRESENT (option_name="PRESENT_ITEM") + 1 HW ABSENT + 1 HW DISABLED
import src.outputs.branded_spec_writer as bsw; bsw.SHOW_ABSENT_BLOCK = False (восстановить после)
Проверить:
- "PRESENT_ITEM" присутствует в файле
- option_name DISABLED строки НЕ присутствует нигде в файле

Тест 5: test_branded_spec_title_contains_source_name
Входные данные: 1 BASE, source_filename="my_spec_test.xlsx"
Проверить: в файле есть ячейка, значение которой содержит подстроку "my_spec_test"

Тест 6: test_branded_spec_multiple_base_blocks
Входные данные: 2 BASE строки (option_name="Server_A" и "Server_B"), у каждой по 1 HW PRESENT
Проверить:
- "Server_A" присутствует в файле
- "Server_B" присутствует в файле

Тест 7: test_branded_spec_unknown_entity_type
Входные данные: 1 BASE + 1 строка с entity_type=EntityType.UNKNOWN (state=None)
Проверить: option_name строки с UNKNOWN присутствует в файле
(UNKNOWN всегда включается независимо от state)

Требования к реализации:
- Использовать pytest fixture tmp_path для путей к выходным файлам
- Строить NormalizedRow и ClassificationResult вручную (не запускать пайплайн)
- НЕ вызывать main.py, parse_excel или другие части пайплайна
- НЕ создавать файлы вне tmp_path
- Для проверки содержимого ячеек: собрать все non-None значения через ws.iter_rows()
```

**Acceptance (PowerShell):**
```powershell
cd dell_spec_classifier
python -m pytest tests\test_branded_spec_writer.py -v
# Все 7 тестов: PASSED

python -m pytest tests\ -q
# Итог = baseline + 7 новых PASSED, 0 FAILED

# Regression gate финальный
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v
```

**Коммит:**
```powershell
cd ..
git add tests\test_branded_spec_writer.py
git commit -m "test: add tests for branded_spec_writer"
```

---

---

## ИТОГОВАЯ ПРОВЕРКА (после всех 3 промптов)

```powershell
cd dell_spec_classifier

# Прогон на всех тестовых файлах
foreach ($f in Get-ChildItem ..\test_data\*.xlsx) {
    Write-Host "--- $($f.Name) ---"
    python main.py --input $f.FullName --output-dir ..\output
}

# Все тесты
python -m pytest tests\ -v

# Финальный regression gate
python -m pytest tests\test_regression.py tests\test_dec_acceptance.py -v

# Финальный diff scope (cumulative от baseline до текущего состояния)
# Внимание: это cumulative diff — показывает ВСЕ изменения с момента baseline-before-prompts
git diff --name-only baseline-before-prompts
# Допустимые файлы:
#   src/outputs/annotated_writer.py
#   src/outputs/json_writer.py
#   src/outputs/branded_spec_writer.py  (новый)
#   main.py
#   config.yaml
#   .gitignore
#   tests/test_branded_spec_writer.py   (новый)
# Недопустимо: src/core/*, golden/*, rules/*

# Структура последнего run_folder
$run = Get-ChildItem ..\output\run_* | Sort-Object Name | Select-Object -Last 1
Get-ChildItem $run.FullName | Select-Object Name
# Ожидаемые файлы:
#   classification.jsonl
#   cleaned_spec.xlsx
#   dl*_annotated.xlsx
#   dl*_branded.xlsx
#   header_rows.csv
#   rows_normalized.json
#   rows_raw.json
#   run.log
#   run_summary.json
#   unknown_rows.csv

# Проверить что нет неожиданных файлов в run_folder
Get-ChildItem $run.FullName | Where-Object {
    $_.Name -notmatch "classification|cleaned_spec|annotated|branded|header_rows|rows_|run_|unknown"
}
# Вывод должен быть пустым
```
