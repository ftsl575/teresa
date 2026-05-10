# ШАГ 2 — MASTER PLAN ДЛЯ CURSOR
**Модель:** Opus 4.6 | **Extended:** ON  
**Когда:** после PRE-CHECK (вариант A) или после FAIL аудита 1G (вариант B)

---

## ВАРИАНТ A — если 1G == PASS (новая фича)

**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — Senior Staff Engineer + Tech Lead + QA.
Сгенерируй "MASTER PLAN" для реализации задачи в Cursor.

Ограничения:
- НЕ пиши код.
- План должен быть совместим с Cursor guardrail.
- Каждый шаг должен быть проверяемым.

Задача:
[ВСТАВИТЬ ОПИСАНИЕ ФИЧИ]

Обязательный формат ответа:

WINDOW_NAME: 2 — MASTER PLAN

1) PROBLEM (1–2 предложения)

2) SCOPE
- In-scope:
- Out-of-scope:

3) MASTER PLAN (по шагам)
Для каждого шага:
- What
- Why
- FILES TO CHANGE
- Acceptance Criteria
- Validation Commands

4) FILES TO CHANGE (единый список путей)

5) DOC IMPACT (YES/NO по каждому документу)
- CURRENT_STATE.md
- CHANGELOG.md
- USER_GUIDE.md
- CLI_CONFIG_REFERENCE.md
- RUN_PATHS_AND_IO_LAYOUT.md
- DATA_CONTRACTS.md

6) TEST PLAN
- Pre-check
- Post-check
- Какие артефакты сравниваем

7) RISKS
```

**Сохранить:** `plan_step2_master_plan.txt`

---

## ВАРИАНТ B — если 1G == FAIL (устранение блокеров)

**Файлы:** прямой доступ через Cowork + результат_шаг1G.txt _(claude.ai: teresa.zip + результат_шаг1G.txt)_

```
Ты — Senior Staff Engineer + Tech Lead + QA.
Сгенерируй "MASTER PLAN" для устранения FAIL из audit_1G.

Ограничения:
- НЕ пиши код.
- Сначала закрыть все P0.
- P1 — отдельной фазой.
- Никакого широкого рефакторинга.

КРИТИЧЕСКОЕ ПРАВИЛО:
- В скоуп включать ТОЛЬКО P0 блокеры и P1 которые вызывают FAIL секции.
- Архитектурный долг (P2) и doc-drift → OUT-OF-SCOPE.
- Документацию обновлять ОДНИМ ПРОХОДОМ после всех кодовых правок,
  НЕ между ними.
- Если единственные FAIL — Docs Consistency и Outputs/Metrics,
  а P0=0, то это НЕ "fix audit FAIL", а "doc sync" — используй 07.

Задача:
Закрыть BLOCKERS из результат_шаг1G.txt и довести проект до PASS.

Обязательный формат ответа:

WINDOW_NAME: 2 — MASTER PLAN (fix audit_1G FAIL)

A) SCOPE
- In-scope (P0)
- Out-of-scope

B) PHASE P0 (обязательно)
Для каждого шага:
- What/Why
- FILES TO CHANGE
- Acceptance Criteria
- Validation Commands
- Expected Artifacts / Expected Deltas

C) PHASE P1 (если нужно, отдельно)

D) FILES TO CHANGE (единый список)

E) DOC IMPACT (YES/NO по каждому документу)

F) TEST PLAN
- Pre-check
- Post-check
- Критерии PASS

G) RISKS + ROLLBACK
```

**Сохранить:** `plan_step2_master_plan_fix_audit_1G.txt`
