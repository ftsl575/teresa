# One-Button Run — spec_classifier

## Быстрый старт

```powershell
.\scripts\run_full.ps1
```

## Что делает run_full.ps1

1. Находит корень репо
2. Перенаправляет .pytest_cache и __pycache__ в temp_root (из config.local.yaml или ./temporary)
3. Запускает pytest
4. Запускает batch-прогон для каждого вендора (если есть файлы)
5. Сохраняет логи в temp_root/diag/runs/<timestamp>/
6. Печатает итог

## Конфигурация путей

Три уровня (от низкого к высокому приоритету):

1. **config.yaml** — дефолты (относительные, в репо)
2. **config.local.yaml** — личные пути (НЕ в git)
3. CLI параметры / параметры скрипта

## Настройка config.local.yaml

```powershell
copy config.local.yaml.example config.local.yaml
# Отредактировать пути под свою машину
```

## Чистка мусора

```powershell
.\scripts\clean.ps1
```

Удаляет __pycache__, .pytest_cache, .ruff_cache, .mypy_cache и diag/ из temp_root и рабочего дерева.  
Не трогает: golden, output.
