# Roadmap: Teresa

## Milestones

- ✅ **v1.0 Cleanup & Workflow Setup** — Phases 1-3 (shipped 2026-05-10)
- ✅ **v1.1 Periphery cleanup (residual)** — Phases 4-6 (shipped 2026-05-11)
- 📋 **v1.2 (next)** — TBD via `/gsd-new-milestone`

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5, 6): Planned milestone work
- Decimal phases (e.g., 4.1): Urgent insertions (marked with INSERTED)
- Phase numbering is monotonic across milestones — never restart at 1

<details>
<summary>✅ v1.0 Cleanup & Workflow Setup (Phases 1-3) — SHIPPED 2026-05-10</summary>

- [x] Phase 1: Hygiene (4/4 plans) — completed 2026-05-10
- [x] Phase 2: Docs (6/6 plans) — completed 2026-05-10
- [x] Phase 3: Workflow (3/3 plans) — completed 2026-05-10

Full details: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md)

</details>

<details>
<summary>✅ v1.1 Periphery cleanup (residual) (Phases 4-6) — SHIPPED 2026-05-11</summary>

- [x] Phase 4: Cache Redirect (3/3 plans) — completed 2026-05-10
- [x] Phase 5: Orphan Cleanup (1/1 plans) — completed 2026-05-10
- [x] Phase 6: Doc-vs-Impl Drift Sweep (6/6 plans) — completed 2026-05-11

Full details: [`.planning/milestones/v1.1-ROADMAP.md`](milestones/v1.1-ROADMAP.md)

</details>

### 📋 v1.2 (next milestone — TBD)

Run `/gsd-new-milestone` to scope and plan the next milestone. v1.2 candidates surfaced during v1.1:

- Broader `/gsd-map-codebase` refresh of all 7 `.planning/codebase/` maps (folds in volatile-counts work deferred from Phase 6)
- `spec_classifier/CLAUDE.md` + `spec_classifier/README.md` drift sweep (out of v1.1's 16-file ROADMAP scope; deepest accumulation of drift-prone claims in the repo)
- Per-vendor knowledge documentation (the original v1.2 scope per `[v1.1 Init]`)

## Progress

| Phase                       | Milestone | Plans Complete | Status   | Completed  |
| --------------------------- | --------- | -------------- | -------- | ---------- |
| 1. Hygiene                  | v1.0      | 4/4            | Complete | 2026-05-10 |
| 2. Docs                     | v1.0      | 6/6            | Complete | 2026-05-10 |
| 3. Workflow                 | v1.0      | 3/3            | Complete | 2026-05-10 |
| 4. Cache Redirect           | v1.1      | 3/3            | Complete | 2026-05-10 |
| 5. Orphan Cleanup           | v1.1      | 1/1            | Complete | 2026-05-10 |
| 6. Doc-vs-Impl Drift Sweep  | v1.1      | 6/6            | Complete | 2026-05-11 |

---
*v1.0 milestone closed 2026-05-10. v1.1 milestone closed 2026-05-11. Per-milestone details preserved in `.planning/milestones/`.*
