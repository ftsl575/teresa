# Changelog

All notable changes to Dell classification rules will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2026-02-25

### Added
- Full hw_type classification pipeline
- Three-layer hw_type matching (device_type → rule_id → regex)
- hw_type statistics (counts + null counter)
- Annotated Excel output with hw_type column

### Fixed
- Unresolved HW rows handling
- Regression synchronization with golden
- Repository cleanup (remove helper scripts and artifacts)
## [1.1.0] - 2026-02-23 (vNext Phase 2)

### Added
- **device_type** field: `ClassificationResult` and `classification.jsonl` now include `device_type` for ITEM rows with HW/LOGISTIC and `matched_rule_id != UNKNOWN-000`. `run_summary.json` includes `device_type_counts`.
- **device_type_rules** in `dell_rules.yaml`: second-pass match for HW/LOGISTIC rows to assign power_cord, storage_ssd, storage_nvme, psu, nic, sfp_cable, hba, raid_controller, cpu.
- **New entity rules** (first-match after HW-001вЂ“004 / LOGISTIC-001вЂ“003):
  - LOGISTIC-004-CORD: power cords (option_name: power cord, jumper cord, rack cord, C13/C14/C19/C20)
  - LOGISTIC-005-SFP-CABLE: SFP/twinax cables (option_name or module_name SFP Module)
  - HW-005-STORAGE-CUS: SSD/NVMe Customer Kit
  - HW-006-PSU-CUS: Power Supply Customer Kit
  - HW-007-NIC-CUS: NIC/OCP Customer Kit or Install
  - HW-008-HBA-PERC-CUS: HBA/PERC/Fibre Channel (DIB, CK, full height, low profile)
  - HW-009-CPU-CUS: Xeon Customer Install
- **tests/test_device_type.py**: 20 unit tests for all MUST-FIX SKUs and edge cases (UNKNOWN/HEADER/BASE в†’ device_type None).
- Golden format extended with `device_type`; regression compares entity_type, state, matched_rule_id, device_type, skus.

### Changed
- HW rules order: generic module rules (HW-001вЂ“004) before option_name-only rules (HW-005вЂ“009) so only formerly UNKNOWN rows are reclassified; anti-regression preserved.
- `scripts/generate_golden.ps1`: fixed Write-Warning causing parse error in some PowerShell hosts.

## [1.0.0] - 2026-02-23

### Added
- Initial release with 8 entity types (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN)
- row_kind detection (ITEM/HEADER)
- SOFTWARE-001: Embedded Systems Management
- SOFTWARE-002: Dell Secure Onboarding
- Full test coverage with regression tests

