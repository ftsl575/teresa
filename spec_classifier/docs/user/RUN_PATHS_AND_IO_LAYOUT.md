# Run Paths & I/O Layout — External roots (Desktop INPUT/OUTPUT)

## Цель: репозиторий только с кодом

Все входные и выходные данные прогонов располагаются **вне репозитория**. По умолчанию используются папки на рабочем столе: `INPUT` (вход) и `OUTPUT` (выход). В каталоге `spec_classifier/` не создаются папки `out/`, `output/` и не появляются артефакты прогонов.

---

## Папки по умолчанию

| Назначение | Путь по умолчанию |
|------------|-------------------|
| **INPUT**  | `C:\Users\G\Desktop\INPUT`  — каталог с входными .xlsx (одиночный файл задаётся путём к файлу; для batch — каталог с файлами). |
| **OUTPUT** | `C:\Users\G\Desktop\OUTPUT` — верхний корень вывода; внутри создаются `dell_run/`, `cisco_run/`, затем папки прогонов. |
| **TEMP**   | **Не используется.** Пайплайн работает в памяти (parse → normalize → classify) и пишет только в итоговую run-папку. Отдельная временная директория не требуется. В будущем TEMP может понадобиться только при появлении промежуточной записи на диск (например, распаковка больших архивов или кэширование нормализованных данных). |

---

## Приоритет конфигурации путей

1. **CLI** — явные аргументы имеют наивысший приоритет:  
   `--output-dir`, `--batch-dir` (или каталог, указанный в `--input` для одиночного файла).
2. **config.yaml** — секция `paths`:  
   `paths.input_root`, `paths.output_root` (используются, если соответствующий CLI-аргумент не передан).
3. **Дефолты** — если в config нет `paths` или ключа:  
   `C:\Users\G\Desktop\INPUT`, `C:\Users\G\Desktop\OUTPUT`.

---

## Точное дерево вывода (соответствует out.zip)

Верхний уровень — **output_root** (по умолчанию `C:\Users\G\Desktop\OUTPUT`). Под ним создаются подпапки по вендору и затем папки прогонов.

### Dell

```
OUTPUT\
  dell_run\
    run-YYYY-MM-DD__HH-MM-SS-<stem>\
      rows_raw.json
      rows_normalized.json
      classification.jsonl
      cleaned_spec.xlsx
      header_rows.csv
      unknown_rows.csv
      run_summary.json
      run.log
      <stem>_annotated.xlsx
      <stem>_branded.xlsx
```

- В каждом run-каталоге Dell присутствуют все перечисленные артефакты, включая **run.log** и **&lt;stem&gt;_branded.xlsx**.

### Cisco

```
OUTPUT\
  cisco_run\
    run-YYYY-MM-DD__HH-MM-SS-<stem>\
      rows_raw.json
      rows_normalized.json
      classification.jsonl
      cleaned_spec.xlsx
      header_rows.csv
      unknown_rows.csv
      run_summary.json
      run.log
      <stem>_annotated.xlsx
```

- Для Cisco **нет** файла `<stem>_branded.xlsx` — только перечисленные выше. **run.log** есть в каждом run.

### Batch (TOTAL)

В режиме batch дополнительно создаётся папка агрегации:  
`output_root\<vendor>_run\run-YYYY-MM-DD__HH-MM-SS-TOTAL\` с копиями presentation-файлов из каждого прогона (с префиксом stem).

---

## Примеры команд (PowerShell, полные пути)

### Создание папок INPUT и OUTPUT

```powershell
New-Item -ItemType Directory -Force -Path "C:\Users\G\Desktop\INPUT"
New-Item -ItemType Directory -Force -Path "C:\Users\G\Desktop\OUTPUT"
```

### Одиночный прогон Dell

```powershell
cd C:\Users\G\Desktop\teresa\spec_classifier
# Положите dl1.xlsx в Desktop\INPUT, затем:
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx"
# Результат: C:\Users\G\Desktop\OUTPUT\dell_run\run-YYYY-MM-DD__HH-MM-SS-dl1\
```

### Одиночный прогон Cisco

```powershell
cd C:\Users\G\Desktop\teresa\spec_classifier
python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco
# Результат: C:\Users\G\Desktop\OUTPUT\cisco_run\run-YYYY-MM-DD__HH-MM-SS-ccw_1\
```

### Batch (все .xlsx из INPUT)

```powershell
cd C:\Users\G\Desktop\teresa\spec_classifier
python main.py --batch-dir "C:\Users\G\Desktop\INPUT"
# или, если в config.yaml задан paths.input_root:
python main.py --batch
# Результат: OUTPUT\dell_run\run-...-<stem>\ для каждого файла + run-...-TOTAL\
```

### Запуск тестов

```powershell
cd C:\Users\G\Desktop\teresa\spec_classifier
python -m pytest tests/ -v --tb=short
```

---

## Не делайте так (частые ошибки)

- **Не указывайте `--output-dir output` при запуске из репозитория** — тогда артефакты появятся в `spec_classifier/output/` и засорят репо.
- **Не коммитьте** каталоги `.venv/`, `__pycache__/`, `.pytest_cache/`, а также любые `out/`, `output/` с результатами прогонов.

---

## Чеклист: «ничего не пишется в репо»

После прогона без явного `--output-dir` (или с `--output-dir C:\Users\G\Desktop\OUTPUT`):

1. Выполните `git status` — в списке изменённых/новых файлов не должно быть папок вывода и артефактов.
2. Убедитесь, что в корне репозитория и в `spec_classifier/` нет новых каталогов `out/`, `output/` с run-папками.

Если оба пункта выполнены — вывод действительно идёт только во внешний OUTPUT.

---

## См. также

- [CLI_CONFIG_REFERENCE.md](CLI_CONFIG_REFERENCE.md) — все параметры CLI и config.
- [DOCS_INDEX.md](../DOCS_INDEX.md) — индекс документации.
