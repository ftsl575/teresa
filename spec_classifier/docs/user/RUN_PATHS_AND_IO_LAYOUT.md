# Run Paths & I/O Layout — Input/Output roots

## Цель: репозиторий только с кодом

Папка teresa/ (spec_classifier/) содержит ТОЛЬКО исходный код, правила, документацию и тесты. Входные данные, результаты прогонов, кеши и временные файлы ВСЕГДА хранятся СНАРУЖИ.

## Data Isolation Policy

Четыре директории ВСЕГДА раздельные:

| Роль      | Путь                           | Содержимое                          |
|-----------|--------------------------------|-------------------------------------|
| CODE      | C:\Users\G\Desktop\teresa      | Только .py, .yaml, .md, .ps1, тесты |
| INPUT     | C:\Users\G\Desktop\INPUT       | Исходные .xlsx с конфигуратора      |
| OUTPUT    | C:\Users\G\Desktop\OUTPUT      | Результаты прогонов (run folders)   |
| TEMPORARY | C:\Users\G\Desktop\temporary  | __pycache__, .pytest_cache, diag/   |

Как это обеспечивается:

1. config.local.yaml задаёт абсолютные пути (не коммитится).
2. pyproject.toml редиректит .pytest_cache в ../../temporary/ (из spec_classifier → Desktop\temporary\.pytest_cache).
3. Скрипты (run_full.ps1, run_tests.ps1) выставляют PYTHONPYCACHEPREFIX для __pycache__.
4. .gitignore блокирует input/, output/, temporary/, __pycache__/, .pytest_cache/.
5. clean.ps1 удаляет любой просочившийся мусор из repo.

ОБЯЗАТЕЛЬНО перед распространением (zip, отправка): запустить `scripts\clean.ps1` для удаления кешей из repo.

---

### Virtual Environment Policy

The virtual environment is **external** to the repository. Current path: `C:\venv`. The repository must not store virtual environments; this keeps the repo lightweight and clean. Dependency installation is done via `requirements.txt` (install into the external venv after creating it with `python -m venv C:\venv`).

---

## Папки по умолчанию

| Назначение | Путь по умолчанию |
|------------|-------------------|
| **INPUT**  | `input/` (относительно cwd) — каталог с входными .xlsx (одиночный файл задаётся путём к файлу; для batch — каталог с файлами). |
| **OUTPUT** | `output/` (относительно cwd) — верхний корень вывода; внутри создаются `dell_run/`, `cisco_run/`, `hpe_run/`, затем папки прогонов. |
| **TEMP**   | **Не используется.** Пайплайн работает в памяти (parse → normalize → classify) и пишет только в итоговую run-папку. Отдельная временная директория не требуется. В будущем TEMP может понадобиться только при появлении промежуточной записи на диск (например, распаковка больших архивов или кэширование нормализованных данных). |

---

## Рекомендуемая структура INPUT папки

При работе с несколькими вендорами рекомендуется держать файлы в отдельных подпапках:

```
input/
  dell/    <- dl*.xlsx
  cisco/   <- ccw*.xlsx
```

Запуск:

```bash
python main.py --batch-dir input/dell --vendor dell
python main.py --batch-dir input/cisco --vendor cisco
```

Это предотвращает попытку обработать Dell-файлы Cisco-адаптером и наоборот.

---

## Приоритет конфигурации путей

1. **CLI** — явные аргументы имеют наивысший приоритет:  
   `--output-dir`, `--batch-dir` (или каталог, указанный в `--input` для одиночного файла).
2. **config.yaml** — секция `paths`:  
   `paths.input_root`, `paths.output_root` (используются, если соответствующий CLI-аргумент не передан).
3. **Дефолты** — если в config нет `paths` или ключа:  
   `input`, `output` (относительно текущей директории).

---

## Точное дерево вывода (соответствует out.zip)

Верхний уровень — **output_root** (по умолчанию `output/`). Под ним создаются подпапки по вендору и затем папки прогонов.

### Dell

```
output/
  dell_run/
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
output/
  cisco_run/
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

## Примеры команд

### Создание папок INPUT и OUTPUT

```bash
mkdir input
mkdir output
```

### Одиночный прогон Dell

```bash
cd spec_classifier
# Положите dl1.xlsx в input/, затем:
python main.py --input input/dl1.xlsx
# Результат: output/dell_run/run-YYYY-MM-DD__HH-MM-SS-dl1/
```

### Одиночный прогон Cisco

```bash
cd spec_classifier
python main.py --input input/ccw_1.xlsx --vendor cisco
# Результат: output/cisco_run/run-YYYY-MM-DD__HH-MM-SS-ccw_1/
```

### Batch (все .xlsx из input)

```bash
cd spec_classifier
python main.py --batch-dir input
# или, если в config.yaml задан paths.input_root:
python main.py --batch-dir input
# Результат: output/dell_run/run-...-<stem>/ для каждого файла + run-...-TOTAL/
```

### Запуск тестов

```bash
cd spec_classifier
python -m pytest tests/ -v --tb=short
```

---

## Не делайте так (частые ошибки)

- **Не указывайте `--output-dir output` при запуске из репозитория** — тогда артефакты появятся в `spec_classifier/output/` и засорят репо.
- **Не коммитьте** каталоги `.venv/`, `__pycache__/`, `.pytest_cache/`, а также любые `out/`, `output/` с результатами прогонов.
- **Не запускайте pipeline без config.local.yaml** — relative defaults создадут input/ и output/ внутри repo.
- **Не запускайте `python -m pytest` напрямую без скриптов** — используйте `scripts\run_tests.ps1` (редиректит все кеши). Если IDE запускает pytest напрямую — pyproject.toml перенаправит .pytest_cache, но __pycache__ всё равно появится (удалить через clean.ps1).

---

## Чеклист: «ничего не пишется в репо»

1. Запустите `scripts\clean.ps1`.
2. Проверьте: `dir spec_classifier` — нет __pycache__, .pytest_cache, input/, output/, temporary/, diag/.
3. Проверьте: config.local.yaml НЕ должен попадать в архив/отправку (он в .gitignore).
4. В .gitignore присутствуют: input/, output/, temporary/, __pycache__/, .pytest_cache/, config.local.yaml.

---

## См. также

- [CLI_CONFIG_REFERENCE.md](CLI_CONFIG_REFERENCE.md) — все параметры CLI и config.
- [DOCS_INDEX.md](../DOCS_INDEX.md) — индекс документации.
