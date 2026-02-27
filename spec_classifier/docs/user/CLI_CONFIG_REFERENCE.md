# Справка по CLI и config — Dell Specification Classifier

## 1. CLI-параметры

| Параметр | Обязателен | По умолчанию | Описание |
|----------|------------|--------------|----------|
| `--input PATH` | Да (single-file) | — | Путь к входному .xlsx. |
| `--batch-dir PATH` | Да (batch) | — | Директория с .xlsx; обрабатываются все файлы по алфавиту. |
| `--config PATH` | Нет | `config.yaml` | Путь к YAML-конфигу. |
| `--output-dir PATH` | Нет | `output` | Директория для папок прогонов. |
| `--save-golden` | Нет | — | Сохранить golden без подтверждения. |
| `--update-golden` | Нет | — | Перезаписать golden с подтверждением (y/N). |

Примечание: нужен ровно один из `--input` или `--batch-dir`.

---

## 2. Примеры

```bash
# Одиночный файл
python main.py --input test_data/dl1.xlsx

# Другая output-директория
python main.py --input test_data/dl1.xlsx --output-dir /tmp/results

# Batch: все xlsx в test_data/
python main.py --batch-dir test_data --output-dir output

# Сохранить golden
python main.py --input test_data/dl1.xlsx --save-golden

# Обновить golden интерактивно
python main.py --input test_data/dl1.xlsx --update-golden
```

---

## 3. config.yaml — схема

```yaml
# Путь к файлу правил (относительно CWD или абсолютный)
rules_file: "rules/dell_rules.yaml"

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

## 4. Гарантии совместимости

- Ключи `rules_file`, `cleaned_spec.include_types`, `include_only_present` стабильны с v1.0.0.
- Неизвестные ключи в config.yaml игнорируются (forward-compatible).
- Пути разрешаются относительно текущей рабочей директории (CWD), а не от расположения config-файла.
- Изменения, ломающие контракт конфига, отражаются в MAJOR версии и в CHANGELOG.
