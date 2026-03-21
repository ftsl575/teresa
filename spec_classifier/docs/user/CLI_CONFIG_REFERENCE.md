# Справка по CLI и config — spec_classifier

Подробное описание путей ввода/вывода, приоритетов и структуры каталогов: **[RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md)**.

## 1. CLI-параметры

| Параметр | Обязателен | По умолчанию | Описание |
|----------|------------|--------------|----------|
| `--input PATH` | Да (single-file) | — | Путь к входному .xlsx. |
| `--batch-dir PATH` | Да (batch) | — | Директория с .xlsx; обрабатываются все файлы по алфавиту. |
| `--vendor VENDOR` | Нет | `dell` | Вендор: `dell` (spec export), `cisco` (CCW export) или `hpe` (BOM). Выбирает адаптер парсинга и файл правил. |
| `--config PATH` | Нет | `config.yaml` | Путь к YAML-конфигу. |
| `--output-dir PATH` | Нет | из config `paths.output_root` или `C:\Users\G\Desktop\OUTPUT` | Верхний корень вывода. Внутри создаются подпапки по вендору: `dell_run/`, `cisco_run/`, `hpe_run/`, а в них — папки прогонов `run-YYYY-MM-DD__HH-MM-SS-<stem>/`. |
| `--batch` | Нет | — | Batch: все .xlsx из input_root (config или Desktop\\INPUT). |
| `--save-golden` | Нет | — | Сохранить golden без подтверждения. |
| `--update-golden` | Нет | — | Перезаписать golden с подтверждением (y/N). |

Примечание: нужен ровно один из `--input`, `--batch-dir` или `--batch`.

---

## 2. Структура вывода (соответствует out.zip)

**output_root** — это верхний корень вывода (по умолчанию `C:\Users\G\Desktop\OUTPUT`). Внутри него автоматически создаются подпапки по вендору:

- `output_root/dell_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — для Dell (в т.ч. `<stem>_branded.xlsx`, `run.log`)
- `output_root/cisco_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — для Cisco (без branded, с `run.log`)
- `output_root/hpe_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — для HPE (без branded, с `run.log`)

Без `--output-dir` используется `paths.output_root` из config или `C:\Users\G\Desktop\OUTPUT`; в репозитории артефакты не создаются. Полное описание: [RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md).

---

## 3. Примеры

Все примеры используют внешние пути по умолчанию (Desktop\INPUT, Desktop\OUTPUT). См. [RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md) для создания папок и чеклиста.

```powershell
# Одиночный Dell (результат: C:\Users\G\Desktop\OUTPUT\dell_run\run-...-<stem>\)
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx"

# Явный output-root (результат: D:\results\dell_run\run-...\)
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx" --output-dir "D:\results"

# Batch: все .xlsx из INPUT
python main.py --batch-dir "C:\Users\G\Desktop\INPUT"
python main.py --batch

# Cisco CCW (результат: OUTPUT\cisco_run\run-...-<stem>\)
python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco

# Cisco batch
python main.py --batch-dir "C:\Users\G\Desktop\INPUT" --vendor cisco

# HPE одиночный прогон (результат: OUTPUT\hpe_run\run-...-<stem>\)
python main.py --input "C:\Users\G\Desktop\INPUT\hpe\hp1.xlsx" --vendor hpe

# HPE batch
python main.py --batch-dir "C:\Users\G\Desktop\INPUT\hpe" --vendor hpe

# Сохранить golden (в репо: golden/<stem>_expected.jsonl)
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx" --save-golden

# Обновить golden интерактивно
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx" --update-golden
```

---

## 4. config.yaml — схема

```yaml
# Корни ввода/вывода (опционально). CLI --output-dir / --batch-dir переопределяют.
paths:
  input_root: "input"
  output_root: "output"

# Пути к файлам правил по вендору (используется при --vendor)
vendor_rules:
  dell: "rules/dell_rules.yaml"
  cisco: "rules/cisco_rules.yaml"
  hpe: "rules/hpe_rules.yaml"

cleaned_spec:
  # Типы сущностей для cleaned_spec.xlsx
  # Допустимые: BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN
  include_types:
    - BASE
    - HW
    - SOFTWARE
    - SERVICE

  # true = включать только строки с state=PRESENT
  include_only_present: true
```

---

## 5. Гарантии совместимости

- Ключи `cleaned_spec.include_types`, `include_only_present` стабильны с v1.0.0.
- `vendor_rules` — маппинг `vendor` → путь к YAML-правилам; определяет файл правил для каждого вендора.
- Неизвестные ключи в config.yaml игнорируются (forward-compatible).
- Пути разрешаются относительно текущей рабочей директории (CWD), а не от расположения config-файла.
- Изменения, ломающие контракт конфига, отражаются в MAJOR версии и в CHANGELOG.
