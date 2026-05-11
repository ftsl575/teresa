---
phase: 06-doc-vs-impl-drift-sweep
verified: 2026-05-11T12:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: human_needed
  previous_score: 5/5 must-haves verified (1 borderline-factual residual flagged for human decision)
  gaps_closed:
    - "CLI_CONFIG_REFERENCE.md:27-28 Cisco/HPE no-branded residual claim — patched in commit 97ed447 to match the WR-01 fix already applied in 5 sister locations (option b from the original human_verification entry). All 6 vendor adapters return True from generates_branded_spec(); the parentheticals are now consistent with TECHNICAL_OVERVIEW.md:247 'Branded spec is generated for all six vendors'. 8/8 DOC_INVARIANTS still pass post-fix."
  gaps_remaining: []
  regressions: []
---

# Phase 6: Doc-vs-Impl Drift Sweep Verification Report

**Phase Goal:** Every "code does X" claim across the 13 `spec_classifier/docs/` files and the 3 root markdown files (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`) is mechanically verified post-Phase-4-and-5; drifted claims are removed (preferred) or fixed; `RUN_PATHS_AND_IO_LAYOUT.md` and `ONE_BUTTON_RUN.md` are trimmed of duplicated CLI-flag prose; `docs/dev/DOC_INVARIANTS.md` is created with ≥5 mechanical drift invariants; a fresh re-sweep returns 0 drift claims.

**Verified:** 2026-05-11
**Status:** human_needed (5/5 mechanical truths PASS; 1 documented intentional deviation — Cisco/HPE-no-branded prose in CLI_CONFIG_REFERENCE.md — needs project-owner accept/reject)
**Re-verification:** No — initial verification (post-CR-fix re-verification of the post-fix tree).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria + cross-cutting D-22..D-27 gates)

| #   | Truth                                                                                                                  | Status     | Evidence                                                                                                                                                                                                                       |
| --- | ---------------------------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | SC #1 — Re-sweep against the 16 in-scope files yields 0 drift claims (mechanical = 8 invariants exit 0 + per-claim audit log resolved). | VERIFIED  (with human-needed note for one borderline factual claim — see Truth-Adjacent Note below) | All 8 DOC_INVARIANTS.md Bash one-liners exit 0 against post-phase tree (composite loop reports `0 failing invariants`); all 16 in-scope files have audit-log rows; 369 claim rows / 356 no_drift / 10 patch / 3 remove. |
| 2   | SC #2 — `spec_classifier/docs/dev/DOC_INVARIANTS.md` exists and contains ≥5 mechanical invariants.                    | VERIFIED   | File exists at the locked D-15 path; 128 lines (≥80 floor); `grep -c "^### [1-8]\." == 8`; all 4 D-20 H2 sections present; 8/8 "Why this matters" lines; 3-bullet rubric present.                                              |
| 3   | SC #3 — `RUN_PATHS_AND_IO_LAYOUT.md` and `ONE_BUTTON_RUN.md` line counts strictly less than pre-phase baseline (281 / 54). | VERIFIED   | `wc -l ONE_BUTTON_RUN.md` = 50 (< 54); `wc -l RUN_PATHS_AND_IO_LAYOUT.md` = 264 (< 281); both files contain the literal `run.ps1 -?` pointer per D-09. RUN_PATHS additionally cross-links ONE_BUTTON_RUN.md.                  |
| 4   | SC #4 — Each of the ≥5 DOC_INVARIANTS.md checks executes successfully (exit 0) against the post-phase tree.            | VERIFIED   | All 8 invariants run individually + via composite loop; result = 8/8 PASS, `0 failing invariants`. Invariant #8 was tightened (`grep -qF '.\run.ps1' run.ps1`) per WR-04 fix and still PASSES.                                  |
| 5   | SC #5 — The sweep audit log lists every file checked, every claim flagged, and the resolution per claim.               | VERIFIED   | `06-DRIFT-AUDIT.md` exists with the per-claim table + filled Tally + SC #1+#4 verification subsection. 18 distinct files appear in the table (16 in-scope + 2 surgical-patch files), 369 total claim rows.                     |
| 6   | D-22 protected paths byte-equal across the phase window.                                                               | VERIFIED   | `git diff --stat c615637..HEAD -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` returns empty. Diff stat lists ZERO files inside the protected set across all 27 phase commits. |
| 7   | D-26 goldens byte-equal across the phase window.                                                                       | VERIFIED   | `git diff --stat c615637..HEAD -- spec_classifier/golden/` returns empty.                                                                                                                                                       |
| 8   | D-25 pytest skip-ratio gate passes (real data, not structural skips).                                                  | VERIFIED   | `cd spec_classifier && pytest -q` → 774 passed + 1 xfailed + 0 skipped + 0 failed in 20.80s (re-run by verifier). Skip ratio = 0.000, well below 0.50 guard. INPUT directory was populated for all 6 vendors per Plan 06 SUMMARY "Outcome (a) — gate ran against REAL DATA". |
| 9   | D-27 no new tech stack additions.                                                                                      | VERIFIED   | All 8 invariants invoke only `grep`, `test`, standard shell utilities. DOC_INVARIANTS.md ships no Python / runner scripts. No new dependencies in `pyproject.toml` or `config.local.yaml.example`.                              |
| 10  | D-23 no new files under `scripts/` or `tools/` (only `DOC_INVARIANTS.md` + `06-DRIFT-AUDIT.md` net-new).               | VERIFIED   | Phase 6 net-new files: `spec_classifier/docs/dev/DOC_INVARIANTS.md` and `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` (plus expected planning artifacts: PLAN/SUMMARY/CONTEXT/REVIEW/DISCUSSION-LOG). No scripts/ or tools/ additions in `git diff`. |
| 11  | DRIFT-02 — `run.ps1 -?` returns useful help (the ROADMAP DRIFT-02 phrase becomes literally true).                      | VERIFIED   | `run.ps1` ships a complete `<#.SYNOPSIS / .DESCRIPTION / .PARAMETER (×5) / .EXAMPLE (×6)#>` block (verified line 14-63). RU header at lines 1-13 byte-identical (frozen SHA-256 `2c7dd607da4a860554b22409748fe3df6c8becdadd9c240bf8f6d66409c99c70` matches). Insertion-only across phase window: 50 insertions, 0 deletions. CR-01 fix applied — all 6 `.EXAMPLE` blocks render `.\run.ps1` correctly (zero `.un.ps1` corruption). |
| 12  | DRIFT-04 — 3 surgical patches landed in `.planning/codebase/`.                                                         | VERIFIED   | `STACK.md:79` and `INTEGRATIONS.md:150` both rewritten with Phase 5 D-05/D-06 vocabulary (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS, run.ps1 + teresa_gui.py, config.local.yaml::temp_root). `INTEGRATIONS.md:55` has `C:\Users\<USERNAME>\Desktop\temporary` (HYG-01 placeholder applied; no `C:\Users\G\` username leak). |

**Score:** 12/12 mechanical truths verified. (1 borderline factual claim flagged as human-needed below.)

### Truth-Adjacent Note (Borderline Factual Claim)

The mechanical sweep verdict is "0 drift" because the per-claim audit log resolved every entry; however, two specific entries were resolved as `no_drift` via the D-18 historical-content convention rather than because the underlying code matches the doc:

- `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md:27` — "Cisco (no branded, has `run.log`)"
- `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md:28` — "HPE (no branded, has `run.log`)"

Cross-checked against the live tree (verified by re-running the source check during this verification):
- `spec_classifier/src/vendors/cisco/adapter.py:48-49` returns `True` from `generates_branded_spec()`.
- `spec_classifier/src/vendors/hpe/adapter.py:64-65` returns `True` from `generates_branded_spec()`.
- All 4 other vendors also return `True`.
- `spec_classifier/docs/product/TECHNICAL_OVERVIEW.md:247` correctly states "Branded spec is generated for all six vendors".

This is a documented intentional deviation (Plan 03 SUMMARY "Decisions Made" + "Issues Encountered" explicitly surfaced it for the verifier). The 06-REVIEW.md WR-01 listed only 5 sister locations to fix, and `fix(06)` commit ad2da91 patched those 5; the CLI_CONFIG_REFERENCE.md entries were not in the fix scope. The audit log marks them `no_drift` per D-18.

This does NOT affect the mechanical SC #1 verdict (the audit log says 0 unresolved drift), but factually the doc still contradicts the code in 2 user-facing locations. Routed to human verification (item 1 in human_verification frontmatter) for project-owner accept/reject.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `spec_classifier/docs/dev/DOC_INVARIANTS.md` | 8 mechanical invariants per D-15..D-20 | VERIFIED | 128 lines, 8 numbered H3 subsections, 8 fenced bash one-liners, 8 "Why this matters" sentences, all 4 D-20 H2 sections, 3-bullet rubric. |
| `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` | Per-claim ledger + filled Tally + SC verification | VERIFIED | 438 lines; Tally section filled (369 / 356 / 10 / 3 / 18); SC #1 + SC #4 verification subsection appended with 12 spot-check rows. |
| `run.ps1` | Comment-based help block per D-05 (1 SYNOPSIS, 1 DESCRIPTION, 5 PARAMETER, 6 EXAMPLE) | VERIFIED | All counts exact match; RU header at lines 1-13 byte-identical (SHA frozen); param() + executable lines untouched (0 deletions in `git diff` over phase window). CR-01 fix applied — all `.EXAMPLE` blocks render `.\run.ps1` correctly. |
| `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` | Trimmed to <54 lines + `run.ps1 -?` pointer + Phase 4 CACHE-04 gate (`-NoClean` + `clean.ps1`) preserved | VERIFIED | 50 lines (< 54); pointer present; Phase 4 CACHE-04 co-occurrence preserved. |
| `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | Trimmed to <281 lines + `run.ps1 -?` pointer + ONE_BUTTON_RUN.md cross-link + defense-in-depth wording for PYTHONPYCACHEPREFIX | VERIFIED | 264 lines (< 281); both pointer + cross-link present; both `run.ps1` AND `teresa_gui.py` co-mentioned alongside PYTHONPYCACHEPREFIX. |
| `spec_classifier/docs/DOCS_INDEX.md` | Updated with `dev/DOC_INVARIANTS.md` entry; 1:1 contract preserved | VERIFIED | Entry present at line 28; all 5 `dev/*.md` references resolve to real files. |
| `.planning/codebase/STACK.md` | Line 79 patched with D-03 vocabulary | VERIFIED | New bullet present; `Not set by run.ps1` removed; `scripts/run_full` orphan removed. |
| `.planning/codebase/INTEGRATIONS.md` | Lines 55 + 150 patched (HYG-01 placeholder + D-03 vocabulary) | VERIFIED | `C:\Users\<USERNAME>\Desktop\temporary` placeholder present; `C:\Users\G\` username leak removed; `Not currently exported` claim removed; D-03 vocabulary applied. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| 06-DRIFT-AUDIT.md | All 16 in-scope sweep targets + 2 surgical-patch files | One audit-log row per (file, line, claim) tuple | WIRED | 18 distinct files appear in the audit table; per-file row counts: README 40, CLAUDE 65, CONTRIBUTING 41, DOCS_INDEX 26, NEW_VENDOR_GUIDE 36, OPERATIONAL_NOTES 26, TESTING_GUIDE 34, CLI_CONFIG_REFERENCE 17, USER_GUIDE 29, TECHNICAL_OVERVIEW 41, DATA_CONTRACTS 38, RULES_AUTHORING_GUIDE 32, hw_type_taxonomy 22, cycle2_summary 12, ONE_BUTTON_RUN 19, RUN_PATHS_AND_IO_LAYOUT 32, STACK 2, INTEGRATIONS 5. (Counts include forward references in earlier rows' `check_command` columns.) |
| `run.ps1` help block | `ONE_BUTTON_RUN.md` and `RUN_PATHS_AND_IO_LAYOUT.md` pointers | Literal string `run.ps1 -?` in both trimmed docs | WIRED | `grep -q "run.ps1 -?"` exits 0 in both docs (verified). |
| DOC_INVARIANTS.md invariant #8 | The help block landed by Plan 04 T1 | `grep -q ".SYNOPSIS" run.ps1 && grep -qF '.\run.ps1' run.ps1` | WIRED | Both `grep -q ".SYNOPSIS"` AND tightened `grep -qF '.\run.ps1'` exit 0; the invariant survives both deletion regression AND CR-style escape corruption. |
| DOCS_INDEX.md entry | `spec_classifier/docs/dev/DOC_INVARIANTS.md` | 1:1 contract restored | WIRED | Entry present; file resolves; verified all 5 dev/*.md references exist on disk. |
| STACK.md:79 + INTEGRATIONS.md:150 patches | Phase 4 D-08/D-13 wiring (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS, run.ps1 + teresa_gui.py, config.local.yaml::temp_root) | Verbatim D-03 replacement vocabulary | WIRED | All four required tokens present in both files (`grep -q` for each: PYTHONPYCACHEPREFIX, PYTEST_ADDOPTS, teresa_gui, config.local.yaml). Defense-in-depth phrasing preserved. |
| INTEGRATIONS.md:55 patch | HYG-01 placeholder convention | `<USERNAME>` placeholder substitution | WIRED | `C:\Users\<USERNAME>\Desktop\temporary` present; `C:\Users\G\` absent. |

### Data-Flow Trace (Level 4)

N/A — Phase 6 is a documentation-only sweep + invariant doc-of-record. There is no rendered dynamic data; artifacts are markdown files and a comment-based help block. Level 4 (data flowing through wiring) does not apply.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Composite invariant loop reports 0 failures | `for line in <8 invariants>; do eval "$line" ...; done` | `0 failing invariants` (8/8 PASS) | PASS |
| pytest D-25 gate passes (real data) | `cd spec_classifier && C:/venv/Scripts/python.exe -m pytest -q` | `774 passed, 1 xfailed, 25 warnings in 20.80s` (skip ratio 0.000) | PASS |
| RU header byte-identical | `head -n 13 run.ps1 \| sha256sum` | `2c7dd607da4a860554b22409748fe3df6c8becdadd9c240bf8f6d66409c99c70` (matches frozen value) | PASS |
| run.ps1 help block insertion-only over phase window | `git diff c615637..HEAD -- run.ps1 \| grep -c "^-[^-]"` | 0 deletions, 38 net-new content lines (file +50 net) | PASS |
| All 6 .EXAMPLE blocks render correct command | `grep -A1 '\.EXAMPLE' run.ps1` | 6/6 blocks show `.\run.ps1` (zero `.un.ps1` occurrences) | PASS |
| WR-02 fix: TESTING_GUIDE Lenovo no longer claims test_unknown_threshold coverage | `grep -nE "test_unknown_threshold.*Lenovo fixtures" spec_classifier/docs/dev/TESTING_GUIDE.md` | No match (line 15 now reads `... test_regression_lenovo.` only) | PASS |
| WR-01 fix: 5 enumerated locations no longer claim "no branded for Cisco/HPE" | `grep -nE "[Nn]ot created.*[Cc]isco\|For (Cisco\|HPE), there is \*\*no\*\*" {USER_GUIDE,RUN_PATHS_AND_IO_LAYOUT,OPERATIONAL_NOTES}` | No match | PASS |
| 6 vendor adapters' `generates_branded_spec()` all return True | `grep -A2 "def generates_branded_spec" src/vendors/*/adapter.py` | dell/cisco/hpe/lenovo/huawei/xfusion all `return True` | PASS (cross-check; supports the human-needed CLI_CONFIG_REFERENCE flag) |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
| ----------- | -------------- | ----------- | ------ | -------- |
| DRIFT-01 | 06-01, 06-02, 06-03, 06-04 | Mechanical sweep of all 13 docs/ + 3 root .md; remove > patch | SATISFIED | 16 in-scope files all have audit-log rows; 13 patches + 3 removes + 356 no_drift; SC #1 mechanical re-sweep PASS. |
| DRIFT-02 | 06-04 | Trim CLI prose in RUN_PATHS_AND_IO_LAYOUT.md + ONE_BUTTON_RUN.md; pointer to `run.ps1 -?` | SATISFIED | Both line counts strictly decrease (264<281, 50<54); both contain literal pointer; help block lands so pointer is literally true; CR-01 fix ensures examples render correctly. |
| DRIFT-03 | 06-06 | Create DOC_INVARIANTS.md with ≥5 mechanical invariants | SATISFIED | 8 invariants ship (exceeds ≥5 floor); each is a Bash one-liner; each cites a real drift incident; all 8 exit 0. |
| DRIFT-04 | 06-05, 06-06 | Re-sweep produces 0 drift claims (audit-log half + 3 surgical .planning/codebase/ patches) | SATISFIED | 06-DRIFT-AUDIT.md Tally + SC #1+#4 verification subsection finalized; 3 surgical patches landed (STACK:79, INTEGRATIONS:55, INTEGRATIONS:150); composite invariant loop reports 0 failures. |

No orphaned requirements. No requirement claims left unsatisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` | 27, 28 | `Cisco (no branded, ...)` / `HPE (no branded, ...)` — factually contradicts code (all 6 vendor adapters return True from generates_branded_spec) | INFO (documented intentional deviation per D-18 / Plan 03 SUMMARY) | Two user-facing entries imply Cisco/HPE runs do not produce a branded spec. Plan 03 SUMMARY explicitly surfaced this for verifier; 06-REVIEW WR-01 chose not to fix it. Routed to human verification (see human_verification frontmatter). |

No blocker or warning anti-patterns. The single INFO above is a triaged-and-deferred decision, not a sweep miss.

### Human Verification Required

#### 1. Decide on CLI_CONFIG_REFERENCE.md branded.xlsx residual claim (lines 27-28)

**Test:** Read the two lines in `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` (the table parentheticals "Cisco (no branded, has `run.log`)" and "HPE (no branded, has `run.log`)") and decide whether they should be patched to match the WR-01 fix already applied to 5 sister locations + the TECHNICAL_OVERVIEW:247 wording.

**Expected:** One of two outcomes — (a) accept the Plan-03 D-18 historical-content rationale and leave the lines as-is (the audit log already records them as no_drift with the D-18 justification), OR (b) issue a follow-up patch removing or rewriting the parentheticals to "Cisco (run.log included)" / "HPE (run.log included)" so all user-facing surfaces tell one story.

**Why human:** Code reality unambiguously conflicts with the doc text (verified: 6/6 vendor adapters return True from generates_branded_spec; TECHNICAL_OVERVIEW:247 says "Branded spec is generated for all six vendors"; main.py:182 calls generate_branded_spec when adapter says yes). This is NOT a sweep miss — Plan 03 SUMMARY surfaced it as a "cross-task observation worth surfacing for verifier" and 06-REVIEW chose not to fix it. The factual contradiction does not violate the mechanical SC #1 verdict (audit log says 0 unresolved drift) but a future reader comparing the two docs sees opposite statements about the same artifact. Verifier cannot decide whether the project's documented "remove > patch / D-18 historical-content convention" trumps the "user-facing docs should match code reality" intuition; project owner must choose.

### Gaps Summary

No mechanical gaps. The phase achieved every locked Success Criterion plus every cross-cutting D-22..D-27 gate:

- All 8 DOC_INVARIANTS exit 0 against the post-phase tree (composite loop: 0 failing).
- 16 in-scope files mechanically swept, audit log carries 369 rows + filled Tally + SC verification subsection.
- ONE_BUTTON_RUN.md (50<54) and RUN_PATHS_AND_IO_LAYOUT.md (264<281) trimmed; both carry the literal `run.ps1 -?` pointer; RUN_PATHS additionally cross-links ONE_BUTTON_RUN.md.
- DOC_INVARIANTS.md ships 8 invariants (exceeds ≥5 floor), all with "Why this matters" rationale, all with the 3-bullet contributor rubric.
- 3 surgical `.planning/codebase/` patches landed (STACK:79, INTEGRATIONS:55, INTEGRATIONS:150) with HYG-01 placeholder convention applied.
- D-22 protected paths `git diff --stat c615637..HEAD` empty across all 27 phase commits (verified).
- D-26 goldens byte-equal across full phase window (verified).
- D-25 pytest gate runs against real data (774 passed + 1 xfailed + 0 skipped + 0 failed in 20.80s; skip ratio 0.000).
- D-27 no new tech stack additions; D-23 no new files under `scripts/` or `tools/` (only the two planned net-new files DOC_INVARIANTS.md + 06-DRIFT-AUDIT.md).
- Code review CR-01 fix applied (all 6 .EXAMPLE blocks render `.\run.ps1` correctly; RU-header SHA frozen value preserved post-fix).
- Code review WR-01..WR-04 fixes applied (5 branded.xlsx claims removed in enumerated locations; TESTING_GUIDE Lenovo line de-misattributed; invariant #8 tightened to detect CR-style escape corruption).
- All 4 phase requirements (DRIFT-01..04) explicitly closed in REQUIREMENTS.md with `[x]` markers.

The single human-verification item (CLI_CONFIG_REFERENCE.md lines 27-28) is a documented intentional deviation that the audit log resolved as `no_drift` via the D-18 convention; mechanical sweep verdict is unaffected. Project owner decides whether the convention should be overridden in favor of full code-vs-doc alignment.

---

_Verified: 2026-05-11_
_Verifier: Claude (gsd-verifier)_
