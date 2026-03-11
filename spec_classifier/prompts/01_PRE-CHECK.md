# ШАГ 1 — PRE-CHECK
**Модель:** Sonnet 4.6 | **Extended:** OFF
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip + OUTPUT.rar)_
**Когда:** перед любыми изменениями, чтобы зафиксировать baseline

---

## ПРОМПТ

```
Ты — чеклист-аудитор. Никаких правок кода, только факты.
_(Cowork: прямой доступ к репо и OUTPUT. claude.ai: прочитай teresa.zip и OUTPUT.rar.)_

1) Подтверди, что тесты/прогоны в принципе возможны по документации: где описан
   запуск и какие входные пути ожидаются (только ссылки на документы).
2) По OUTPUT.rar посчитай для каждого вендора (Dell / Cisco / HPE):
   - unknown_count (entity_type == UNKNOWN в classification.jsonl)
   - hw_type_null_count среди HW строк
   - количество E2, E17, E18 в audit_report.json (если файл присутствует)
   Укажи точные пути файлов, по которым считал.
3) Если есть audit_report.json — укажи:
   - сколько REAL_BUG / REVIEW_NEEDED / FALSE_POSITIVE
   - топ-3 паттерна по count
4) Если есть cluster_summary.xlsx — укажи:
   - сколько кластеров, сколько с heuristic confidence
   - сколько manual_review
5) В конце дай SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION).
```

## ЧТО СОХРАНИТЬ
- `precheck.txt`
- `precheck_summary.txt` (только SUMMARY-блок)
