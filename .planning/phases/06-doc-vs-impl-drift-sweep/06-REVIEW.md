---
phase: 06-doc-vs-impl-drift-sweep
reviewed: 2026-05-11T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - run.ps1
  - spec_classifier/docs/DOCS_INDEX.md
  - spec_classifier/docs/dev/DOC_INVARIANTS.md
  - spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md
  - spec_classifier/docs/dev/ONE_BUTTON_RUN.md
  - spec_classifier/docs/dev/OPERATIONAL_NOTES.md
  - spec_classifier/docs/dev/TESTING_GUIDE.md
  - spec_classifier/docs/product/TECHNICAL_OVERVIEW.md
  - spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md
  - spec_classifier/docs/user/USER_GUIDE.md
findings:
  critical: 1
  warning: 4
  info: 0
  total: 5
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-05-11T00:00:00Z
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Phase 6 was a "doc-vs-impl drift sweep" that added a 64-line PowerShell comment-based help block to `run.ps1` and translated/cleaned several markdown files. The 8 mechanical Bash invariants in the new `DOC_INVARIANTS.md` were verified — all 8 PASS against the current tree, including the composite loop reproduced in the doc.

However, the review surfaced one Critical and four Warning findings:

- The new `<#.SYNOPSIS … #>` help block in `run.ps1` contains a corrupted token in every `.EXAMPLE` section: the example commands read `.un.ps1` instead of `.\run.ps1`. PowerShell renders this as a broken two-line garble (verified by running `Get-Help .\run.ps1 -Examples` against the current file). This is the deliverable Phase 6 invariant #8 was designed to protect, and it ships broken in its first version.
- The Phase 6 sweep was supposed to catch documentation that contradicts the live tree (DRIFT-01). Three user/dev docs still claim that `<stem>_branded.xlsx` is "not created" for Cisco / HPE runs, but every adapter (`cisco`, `hpe`, plus `dell`, `lenovo`, `huawei`, `xfusion`) returns `True` from `generates_branded_spec()`. The same Phase 6 commits also produced `TECHNICAL_OVERVIEW.md` line 247 which now correctly says "Branded spec is generated for all six vendors" — the user-facing copies were missed.
- `TESTING_GUIDE.md` claims `test_unknown_threshold` covers Lenovo fixtures; in fact `tests/test_unknown_threshold.py` is hard-parametrized with `dl1.xlsx … dl5.xlsx` only and runs the Dell rules path. Lenovo has no analogous threshold test.

The 8 Bash one-liners in `DOC_INVARIANTS.md` and the composite loop are syntactically valid Bash and exit 0 against the current tree. All internal markdown links resolve to real files on disk. No hardcoded credentials, secrets, or leaked usernames were found in the changed surface — the `<USERNAME>` placeholder is used consistently.

## Critical Issues

### CR-01: `.un.ps1` typo in every `.EXAMPLE` block of `run.ps1` help

**File:** `run.ps1:41,45,49,53,57,61`
**Issue:** The Phase 6 comment-based help block lists `.un.ps1` instead of `.\run.ps1` in all six `.EXAMPLE` sections. The leading `.\r` in `.\run.ps1` was interpreted as the carriage-return escape (`\r` → CR). PowerShell's help engine then renders each example as a broken two-line garble:

```
PS C:\>.

un.ps1 -NoAi
Full pipeline + rule-only audit (no OpenAI).
```

Confirmed by running `powershell -NoProfile -Command "Get-Help C:\Users\G\Desktop\teresa\run.ps1 -Examples"` against the current file — every example contains a literal `.` on one line followed by `un.ps1 …` on the next, which is what `Get-Help -Examples` and `.\run.ps1 -?` will display to users.

This is exactly the deliverable Invariant #8 in the new `DOC_INVARIANTS.md` (`grep -q ".SYNOPSIS" run.ps1`) is meant to protect. Invariant #8 only checks for the literal string `.SYNOPSIS`, so it passes despite the corrupted `.EXAMPLE` bodies — the invariant cannot detect this class of regression.

The corruption is not present in the legacy RU header at lines 5–11 (which uses `.\run.ps1` correctly), so this is a Phase 6 regression in the new help block rather than a pre-existing issue.

**Fix:** In `run.ps1`, replace the six occurrences of `.un.ps1` (lines 41, 45, 49, 53, 57, 61) with `.\run.ps1`. The simplest patch is a literal in-place edit:

```powershell
.EXAMPLE
    .\run.ps1
    Full pipeline + AI audit + cluster + tests (all vendors).

.EXAMPLE
    .\run.ps1 -NoAi
    Full pipeline + rule-only audit (no OpenAI).

.EXAMPLE
    .\run.ps1 -Vendor dell
    Only dell, otherwise as usual.

.EXAMPLE
    .\run.ps1 -TestsOnly
    Pytest only.

.EXAMPLE
    .\run.ps1 -SkipTests
    Full pipeline without pytest at the end.

.EXAMPLE
    .\run.ps1 -Vendor huawei -NoAi -SkipTests
    Minimal smoke run on a single vendor.
```

After fixing, re-run `powershell -NoProfile -Command "Get-Help .\run.ps1 -Examples"` and confirm each example renders as a single `PS C:\>.\run.ps1 …` line. Optionally tighten Invariant #8 to also grep for `\.\\run\.ps1` so a future identical regression is caught mechanically.

## Warnings

### WR-01: Three docs still claim `<stem>_branded.xlsx` is not created for Cisco / HPE — code generates it for all six vendors

**Files:**
- `spec_classifier/docs/user/USER_GUIDE.md:78` — table row: `Not created for Cisco CCW runs.`
- `spec_classifier/docs/user/USER_GUIDE.md:160` — body text: `Not created for Cisco CCW and HPE runs.`
- `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md:129` — `For Cisco, there is **no** \`<stem>_branded.xlsx\`.`
- `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md:148` — `For HPE, there is **no** \`<stem>_branded.xlsx\`.`
- `spec_classifier/docs/dev/OPERATIONAL_NOTES.md:26` — `For Cisco and HPE runs \`<stem>_branded.xlsx\` is not copied (the file is not created).`

**Issue:** All four files were touched by Phase 6 commits (T1 `3d4ca85`, T2 `c2bca43` / `3e289bc`, T3 `d45f3fb`) — the explicit DRIFT-01 sweep — yet carry forward the stale claim that Cisco and HPE runs do not produce a branded spec.

Verified against the live tree:
- `spec_classifier/main.py:182` calls `generate_branded_spec(...)` only when `adapter.generates_branded_spec()` returns `True`.
- All six adapters return `True`:
  - `src/vendors/cisco/adapter.py:48-49`
  - `src/vendors/hpe/adapter.py:64-65`
  - `src/vendors/dell/adapter.py`, `lenovo/adapter.py`, `huawei/adapter.py`, `xfusion/adapter.py` likewise.
- `TECHNICAL_OVERVIEW.md:247` (also touched by Phase 6) now correctly says: *"Branded spec is generated for all six vendors (per `adapter.generates_branded_spec()` in `src/vendors/<vendor>/adapter.py`)."*

The user-facing copies were not back-ported. This is the exact class of drift Phase 6 was scoped to eliminate. The contradiction is internally visible: a reader comparing `TECHNICAL_OVERVIEW.md:247` against `RUN_PATHS_AND_IO_LAYOUT.md:129/148` sees opposite statements about the same artifact.

CLAUDE.md (`spec_classifier/CLAUDE.md`, OUTPUT layout block) corroborates the code: `<stem>_branded.xlsx ← all vendors (since f2a2300)`.

**Fix:** Update all five locations to reflect that the branded spec is generated for every vendor. Suggested edits:

```diff
- | `<stem>_branded.xlsx` | Branded specification: grouped by BASE … . Not created for Cisco CCW runs. |
+ | `<stem>_branded.xlsx` | Branded specification: grouped by BASE … . Generated for every vendor. |

- The file is intended for client presentation. Not created for Cisco CCW and HPE runs.
+ The file is intended for client presentation. Generated for every vendor.

- - For Cisco, there is **no** `<stem>_branded.xlsx`. **run.log** is present in every run.
+ - Cisco runs include `<stem>_branded.xlsx` as well. **run.log** is present in every run.

- - For HPE, there is **no** `<stem>_branded.xlsx`. **run.log** is present in every run.
+ - HPE runs include `<stem>_branded.xlsx` as well. **run.log** is present in every run.

- … For Cisco and HPE runs `<stem>_branded.xlsx` is not copied (the file is not created).
+ … `<stem>_branded.xlsx` is now produced for every vendor and is copied into TOTAL.
```

Also add the Cisco/HPE run-folder layouts in `RUN_PATHS_AND_IO_LAYOUT.md` (sections 129 and 148 fenced trees) the missing `<stem>_branded.xlsx` line so the trees match what `main.py` actually emits.

### WR-02: `TESTING_GUIDE.md` claims `test_unknown_threshold` covers Lenovo — it does not

**File:** `spec_classifier/docs/dev/TESTING_GUIDE.md:15`
**Issue:** The Lenovo bullet says: *"`test_lenovo_parser`, `test_lenovo_normalizer`, `test_lenovo_rules_unit`, `test_regression_lenovo`, `test_unknown_threshold` (Lenovo fixtures)."*

`tests/test_unknown_threshold.py` is hard-parametrized with `["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]` (line 17), uses `get_input_root_dell()` (line 21), and loads `rules/dell_rules.yaml` (line 26). It never sees Lenovo fixtures. There is no `test_unknown_threshold_lenovo.py` either (`ls spec_classifier/tests/test_unknown_threshold_lenovo.py` → no such file). A user following this doc to add a Lenovo dataset will be left without a threshold test.

The same line for Cisco / HPE / Huawei / xFusion correctly points to per-vendor `test_unknown_threshold_<vendor>.py` files that do exist.

**Fix:** Either drop the misleading clause for Lenovo, or add a `test_unknown_threshold_lenovo.py`. The minimum-doc-only fix:

```diff
-- **Lenovo:** `test_lenovo_parser`, `test_lenovo_normalizer`, `test_lenovo_rules_unit`, `test_regression_lenovo`, `test_unknown_threshold` (Lenovo fixtures).
++ **Lenovo:** `test_lenovo_parser`, `test_lenovo_normalizer`, `test_lenovo_rules_unit`, `test_regression_lenovo`. *(No per-vendor threshold test yet — see `.planning/codebase/CONCERNS.md`.)*
```

### WR-03: `OPERATIONAL_NOTES.md` § "TOTAL folder" lists branded.xlsx among files Cisco/HPE TOTAL won't have — same drift, second-order consequence

**File:** `spec_classifier/docs/dev/OPERATIONAL_NOTES.md:26`
**Issue:** Same root cause as WR-01 but a separate user-visible statement (TOTAL folder contents). The sentence "For Cisco and HPE runs `<stem>_branded.xlsx` is not copied (the file is not created)" implies TOTAL folders for Cisco/HPE batches will be missing the branded file. In practice `copy_to_total(...)` is unconditional and the branded file is now produced and copied. A user trusting this doc will think a missing branded file is normal when in fact it would indicate a bug.

**Fix:** Covered by the WR-01 patch list (this entry exists to ensure the OPERATIONAL_NOTES.md change is not overlooked when only USER_GUIDE.md / RUN_PATHS_AND_IO_LAYOUT.md are patched).

### WR-04: `DOC_INVARIANTS.md` Invariant #8 grep is too narrow to detect help-block corruption

**File:** `spec_classifier/docs/dev/DOC_INVARIANTS.md:118-122`
**Issue:** Invariant #8 is: `grep -q ".SYNOPSIS" run.ps1`. This passes against the current `run.ps1` even though six of the `.EXAMPLE` bodies are corrupted (CR-01). The doc's "Why this matters" prose says the goal is to keep `Get-Help .\run.ps1` and `.\run.ps1 -?` returning useful help — but the check only verifies one literal token, not that the help renders correctly.

This is a quality issue with the new invariant: it cannot detect the specific class of regression (carriage-return / escape-sequence errors in the help body) that just happened in its own deliverable.

**Fix:** Tighten the invariant to also verify the canonical example string is intact, e.g.:

```bash
grep -q ".SYNOPSIS" run.ps1 && grep -qE '\.\\\\run\.ps1' run.ps1
```

Or, more robustly, parse with PowerShell when available:

```bash
grep -q ".SYNOPSIS" run.ps1 && \
  powershell -NoProfile -Command "(Get-Help ./run.ps1 -Examples | Out-String) -match '\\.\\\\run\\.ps1'" 2>/dev/null | grep -q True
```

The simpler grep variant keeps the no-new-tech-stack stance of the doc. Either form would have caught CR-01.

---

_Reviewed: 2026-05-11T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
