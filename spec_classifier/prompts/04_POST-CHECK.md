# ШАГ 4 — POST-CHECK
**Модель:** Sonnet 4.6 | **Extended:** OFF  
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip + OUTPUT.rar)_
**Когда:** после реализации в Cursor, перед финальным аудитом

---

## ПРОМПТ (Claude окно, опционально)

```
Ты — факт-чекер. Никаких правок.
_(Cowork: прямой доступ к репо и OUTPUT. claude.ai: прочитай teresa.zip и OUTPUT.rar.)_

1) Найди и перечисли итоговые артефакты по каждому вендору.
2) Посчитай для каждого вендора:
   - unknown_count и hw_type_null_count среди HW строк
   - количество E2, E17, E18 (из audit_report.json если есть)
3) Если есть cluster_summary.xlsx — укажи top-5 кластеров по count
   с proposed_device_type и confidence.
4) Дай SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION).
```

## ЧТО СОБРАТЬ ПЕРЕД ЭТИМ ШАГОМ
- вывод `pytest tests/ -v --tb=short`
- артефакты прогона (OUTPUT.rar / OUTPUT.zip) _(Cowork: доступ напрямую)_
- `git diff --name-only` относительно baseline

## ЧТО СОХРАНИТЬ
- `postcheck.txt`
- `postcheck_summary.txt` (только SUMMARY-блок)
