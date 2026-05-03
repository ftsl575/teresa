# hw_type Taxonomy — Universal Device Type Dictionary
## Универсальный словарь типов устройств / spec_classifier teresa

**Version:** v2.6.0  
**Date:** 2026-05-02  
**Vendors covered:** Dell · Cisco CCW · HPE · Lenovo · xFusion · Huawei (active)  
**History:** `HW_TYPE_VOCAB` v2.0.0 (25 values) → v2.1.0 (26, adds `storage_enclosure`) → v2.2.0 — vocab unchanged; `device_type=front_panel` (Lenovo→`management`); RoT→`tpm` bucket (PR-9a) → v2.3.0 — vocab unchanged; `power_distribution_board`, `interconnect_board` (Lenovo+HPE→`chassis`, PR-9b) → v2.4.0 — vocab unchanged; Lenovo `drive_cage`→`backplane`, `media_bay`→`chassis` (PR-9c) → v2.5.0 — vocab unchanged; `air_duct` (Lenovo+xFusion→`accessory`), `optical_drive` (HPE→`storage_drive`); Cable Riser→`riser`; C3RP GPU air-duct fix (PR-10) → **v2.6.0** — vocab still 26; PR-11 adds master `device_type→hw_type` matrix below + code comments that cycle 2 added **no new `hw_type` literals**.

---

## Cycle 2 master map: `device_type` → `hw_type` (PR-8–PR-10, PR-11)

`HW_TYPE_VOCAB` stays at **26** values. Cycle 2 adds or refines **device_type** labels only; mappings live in `rules/<vendor>_rules.yaml` `device_type_map` plus `batch_audit.py` `DEVICE_TYPE_ALIASES` for AI audit.

### New `device_type` labels (cycle 2)

| device_type | hw_type | Vendor(s) | PR | Notes |
|---|---|---|---|---|
| `front_panel` | `management` | Lenovo | PR-9a | Server front operator panel, LCD info display |
| `power_distribution_board` | `chassis` | Lenovo, HPE | PR-9b | Internal PDB / power interface / interconnect board (power path) |
| `interconnect_board` | `chassis` | Lenovo | PR-9b | PCIe Switch / Retimer / I/O Board (internal server board) |
| `media_bay` | `chassis` | Lenovo | PR-9c | Removable physical bay (front I/O, optical, etc.) |
| `air_duct` | `accessory` | Lenovo, xFusion | PR-10 | Airflow guide; **not** a `cooling` hw_type (does not exist in vocab) |
| `optical_drive` | `storage_drive` | HPE | PR-10 | DVD-RW / ODD — same rollup bucket as HDD/SSD/NVMe readers |

### Updated existing mappings (cycle 2)

| device_type | hw_type | Vendor | PR | Change |
|---|---|---|---|---|
| `battery` | `accessory` | xFusion | PR-8 | SuperCap / super capacitor lines: `device_type=battery` unified with Lenovo/HPE naming; still maps to `hw_type=accessory` |
| `drive_cage` | `backplane` | Lenovo | PR-9c | New rules for HDD/HD/NVMe Cage; HPE already `drive_cage→backplane` (PR-3) |

### Taxonomy notes

- **`tpm` bucket:** includes literal **TPM 2.0** modules **and** Lenovo **Root of Trust (RoT)** security modules. Lenovo copy often merges them as "Firmware and Root of Trust/TPM 2.0 Security Module"; both share `device_type=tpm`, `hw_type=tpm` when classified as HW (software-delivery lines may still hit SOFTWARE via `SW-L-010`).

- **`motherboard` (Q1, PR-4a)** is reserved for the **main system board** (e.g. "ThinkSystem SR650 V3 MB"). Internal infrastructure boards use **`power_distribution_board`** (PDB / power interface) or **`interconnect_board`** (PCIe switch / retimer / system I/O board), not `motherboard`.

- **`media_bay` vs `drive_cage`:** *Media bay* — generic front/side **slot** that can host front I/O, optical gear, or other front-mounted options. *Drive cage* — **drive-specific** enclosure tied to backplane semantics; maps to `hw_type=backplane` (Lenovo aligned with HPE PR-3).

---

## Зафиксированные решения

| # | Вопрос | Решение |
|---|--------|---------|
| 1 | hba vs storage_controller — разделять? | **Да.** `hba` = FC HBA + SAS HBA (любой host bus adapter без встроенного RAID). `storage_controller` = только RAID с кешем/батареей (PERC/Smart Array/BOSS/MegaRAID). |
| 2 | transceiver выделять из sfp_cable? | **Да.** SFP/SFP28/QSFP **модули** → `transceiver`. DAC/AOC/patch cord → `cable`. |
| 3 | BASE rows нужен hw_type? | **Нет.** `hw_type_applies_to: [HW]`. BASE rows не получают `hw_type` — тип изделия читается из `device_type`. |
| 4 | enablement_kit — hw_type или device_type? | **Только `device_type`.** `entity_type=HW`, `device_type=enablement_kit`, `hw_type=None`. В `HW_TYPE_VOCAB` **не входит**. |
| 5 | software_license/service в hw_type? | **Нет.** `hw_type_applies_to` = `[HW]`. SOFTWARE/SERVICE — только `entity_type`. |
| 6 | power_cord — hw_type или device_type? | **Только `device_type`.** `hw_type_applies_to` = `[HW]`. Строки `power_cord` имеют `entity_type=HW`, `hw_type=None` (намеренно, per business rules). |

---

## Словарь (26 значений hw_type)

### Группа 1 — Основное изделие (только BASE rows)

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `server` | Server / Compute Node | Сервер / Вычислительный узел | PowerEdge R660, ProLiant DL380 Gen12 CTO, ThinkSystem SR630 V3, 1288H V7 |
| `switch` | Switch / Router | Коммутатор / Маршрутизатор | N9K-C93180YC-FX3, Catalyst 9500-48Y4C, C8500L-8S4X, S5700 |
| `storage_system` | Storage System | Система хранения данных | OceanStor Dorado 5000 V6 NVMe Controller Enclosure |
| `wireless_ap` | Wireless AP / Controller | Точка доступа Wi-Fi / Контроллер | AirEngine 9700-M1, AirEngine 5761R-11, AC6805 |

> `hw_type_applies_to: [HW]`. BASE rows используют `device_type` для идентификации изделия; `hw_type` не присваивается.

---

### Группа 2 — Вычислительные компоненты

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `cpu` | Processor / CPU | Процессор | Intel Xeon 6737P, AMD EPYC 9374F, Intel Xeon Silver 4509Y |
| `memory` | Memory / RAM | Оперативная память | HPE 64GB DDR5-6400 RDIMM, ThinkSystem 32GB TruDDR5, MEM-C8500L-16GB |
| `gpu` | GPU / AI Accelerator | Графический / AI-ускоритель | NVIDIA H200 NVL 141GB PCIe, NVIDIA L40 48GB, NVIDIA L4 24GB |

> **Миграция:** `ram` → `memory`.

---

### Группа 3 — Подсистема хранения

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `storage_drive` | Storage Drive | Накопитель (SSD / HDD / NVMe) | HPE 3.84TB NVMe U.3, HPE 480GB SATA SSD, ThinkSystem VA 480GB, Dorado 7.68TB NVMe |
| `storage_controller` | Storage Controller / RAID | RAID-контроллер | HPE MR416i-o OCP, PERC H965i, BOSS card, MegaRAID, Smart Array с кешем/батареей |
| `hba` | HBA (FC / SAS) | Адаптер шины (FC / SAS HBA) | HPE SN1620E 32Gb FC SecureHBA, SN1610E 32Gb FC, Emulex LPe32002 32Gb FC, HBA465e SAS, Broadcom SAS HBA |
| `backplane` | Backplane / Drive Cage | Объединительная панель / Корзина | HPE Tri-Mode U.3 Drive Cage Kit, ThinkSystem 1U 8×2.5" SAS/SATA Backplane, xFusion FusionServer Backplane |
| `storage_enclosure` | Storage Enclosure / Disk Enclosure | Дисковый отсек СХД (внешний) | Huawei OceanStor Disk Enclosure, Lenovo D1224 (планируется), Dell PowerVault MDxxx (планируется) |
| `io_module` | I/O Module (Storage) | Интерфейсный модуль СХД | 4p SmartIO FC SFP28 (OceanStor), 2p 40Gb ETH QSFP+, 4p 25Gb RDMA Scale-out |

> **Миграция:** `ssd` + `hdd` + `nvme` → `storage_drive`. `hba` device_type → `hw_type: hba` (было `storage_controller`).

**Граница `hba` / `storage_controller`:**

| Тип | `hw_type` | Признаки |
|-----|-----------|----------|
| FC HBA | `hba` | "Fibre Channel", "FC HBA", "SecureHBA", "HBA", модели Emulex/QLogic/Broadcom HBA |
| SAS HBA (passthrough) | `hba` | "SAS HBA", "Host Bus Adapter", HBA465e, режим passthrough/JBOD без RAID |
| RAID-контроллер | `storage_controller` | "PERC", "Smart Array", "RAID", "MR4xx", "BOSS", "MegaRAID", наличие кеша/BBU |

> `io_module` только для СХД Huawei OceanStor — подключаемые интерфейсные модули в корпус массива, не серверные PCIe-карты.

---

### Группа 4 — Сетевые компоненты

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `network_adapter` | Network Adapter (NIC) | Сетевой адаптер (NIC / OCP) | Mellanox MCX631432AS SFP28 OCP3, Broadcom BCM57414 OCP3, Intel E810-CQDA2 100Gb |
| `transceiver` | Optical Transceiver | Оптический трансивер | HPE 25Gb SFP28 SR 100m, SFP-25G-SR-S=, QSFP-100G-LR-S=, GLC-SX-MMD=, OMXD300201 SFP+ |
| `cable` | Cable (DAC / AOC / Fiber / Signal) | Кабель (DAC / AOC / оптический / сигнальный) | QSFP-100G-CU1M= DAC, HPE Premier Flex LC/LC OM4, SFP28-SFP28-25 AOC, XC-0405Y021 |

> **Миграция:** `sfp_cable` разделяется — SFP/QSFP оптические модули → `device_type: transceiver` → `hw_type: transceiver`; DAC/AOC/patch cord остаются через `device_type: sfp_cable` → `hw_type: cable`.

**Граница `transceiver` / `cable` по паттернам SKU:**

| Паттерн в SKU | `hw_type` | Пример |
|---|---|---|
| `-SR`, `-LR`, `-ER`, `-MMD`, `-LH`, `-CSR` | `transceiver` | SFP-25G-SR-S=, GLC-LH-SMD= |
| `-CU{N}M` (passive copper) | `cable` | QSFP-100G-CU1M= |
| Fiber patch cord (LC/PC, MPO/PC, DLC/PC) | `cable` | Patch Cord DLC/PC 3m |
| AOC (Active Optical Cable) | `cable` | SFP28-SFP28-25 AOC |

---

### Группа 5 — Питание

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `psu` | Power Supply Unit | Блок питания | HPE 2400W M-CRPS Titanium, NXA-PAC-650W-PE, ThinkSystem 750W Platinum, PAC900S12-T1 900W |

> **Кабели питания** (`power_cord`): `entity_type=HW`, `device_type=power_cord`, `hw_type=None` (намеренно, per business rules). Тип читается из `device_type`.

---

### Группа 6 — Охлаждение

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `fan` | Fan Module / Fan Kit | Модуль вентиляторов | HPE 2U High Performance Fan Kit, NXA-FAN-35CFM-PE, 4056+ Fan module, C9K-T1-FANTRAY |
| `heatsink` | Heatsink / Thermal Kit | Радиатор / термокит | HPE High Performance 2U Heat Sink Kit, ThinkSystem SR630 V3 Standard Heat Sink |

> **Миграция:** `cpu_heatsink` → `heatsink`.

---

### Группа 7 — Расширение и механика

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `riser` | PCIe Riser / Expansion Card | Плата расширения / Riser | HPE x8/x16/x8 Secondary Riser Kit, ThinkSystem 1U x16/x16 BF Riser1, 1×16X SLOT PCIe5.0 |
| `chassis` | Chassis / System Board | Шасси / Системная плата | ThinkSystem SR630 V3 MB, ThinkSystem V3 1U 10×2.5" Chassis |
| `rail` | Rail Kit / Rack Hardware | Направляющие / Крепёж для стойки | HPE Easy Install Rail 3 Kit, ThinkSystem Toolless Slide Rail Kit v2, Ball Bearing Rail Kit |
| `blank_filler` | Blank / Filler / Dummy PID | Заглушка / Филлер | HPE DDR4 DIMM Blank Kit, ThinkSystem 1×1 2.5" HDD Filler, NXK-AF-PE Airflow Dummy |

> **Миграция:** `mounting_kit` → `rail`. `blank` → `blank_filler`. `motherboard` → поглощается в `chassis`.

---

### Группа 8 — Управление и безопасность

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `management` | Management Module / BMC License | Модуль управления / BMC | HPE iLO Advanced License, XClarity Controller Platinum, HPE OneView FIO Bundle, Lenovo Front Operator Panel (LCD/LED status display) |
| `tpm` | TPM / Security / Root-of-Trust Module | Модуль безопасности TPM / RoT | TPM 2.0, Dell TPM 2.0 v3, Lenovo Root of Trust Module, RoT Module (PR-9a Q7b) |

> **PR-9a Q7b:** `tpm` is a **shared bucket** for both TPM 2.0 modules and Root of Trust (RoT) security modules. Lenovo documents these together as "Firmware and Root of Trust/TPM 2.0 Security Module"; both classes are functionally part of the platform's hardware root of trust and share the same management/security plane.

---

### Группа 9 — Аксессуары

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `accessory` | Accessory / Misc Hardware | Аксессуар / Прочее | NVIDIA NVLink Bridge 2-way/4-way, C9300L-STACK-A Stacking Module, RFID, Antenna |

---

## Отдельные device_type (вне HW_TYPE_VOCAB)

Эти значения существуют **только на уровне `device_type`**; `hw_type` либо `None`, либо мапится в существующий bucket через `device_type_map`:

| `device_type` | Описание | `entity_type` | `hw_type` |
|---|---|---|---|
| `power_cord` | Кабель питания (C13/C14/C15/C19) | HW | `None` |
| `enablement_kit` | Enablement / Option Kit (HPE FIO, xFusion option cables) | HW | `None` — намеренно |
| `front_panel` | Front Operator Panel / LCD system info display (LEDs, диагностический экран, ASM-модуль) | HW | `management` (Lenovo PR-9a Q7a) |
| `power_distribution_board` | Internal PDB / power interface board / power interconnect board | HW | `chassis` (Lenovo + HPE PR-9b Q8) |
| `interconnect_board` | PCIe Switch / Retimer / I-O Board (internal) | HW | `chassis` (Lenovo PR-9b Q8; slot reserved HPE) |
| `drive_cage` | HDD / HD / NVMe cage | HW | `backplane` (Lenovo PR-9c — HPE PR-3 precedent) |
| `media_bay` | Standard / generic media bay (front-mounted) | HW | `chassis` (Lenovo PR-9c Q9) |
| `air_duct` | Air Duct / Airduct — направляющая потока (не heatsink, не fan) | HW | `accessory` (Lenovo + xFusion PR-10) |
| `optical_drive` | DVD-RW / ODD / Optical Drive | HW | `storage_drive` (HPE PR-10) |

---

## Итоговый HW_TYPE_VOCAB (26 значений)

```python
HW_TYPE_VOCAB = frozenset({
    # Основное изделие (BASE rows)
    "server", "switch", "storage_system", "wireless_ap",
    # Вычислительные компоненты
    "cpu", "memory", "gpu",
    # Подсистема хранения
    "storage_drive", "storage_enclosure", "storage_controller", "hba", "backplane", "io_module",
    # Сеть
    "network_adapter", "transceiver", "cable",
    # Питание
    "psu",
    # Охлаждение
    "fan", "heatsink",
    # Расширение и механика
    "riser", "chassis", "rail", "blank_filler",
    # Управление
    "management", "tpm",
    # Аксессуары
    "accessory",
})
```

---

## Таблица миграции (old → new)

| Старый `hw_type` | Новый `hw_type` | Тип изменения | Затрагивает golden |
|---|---|---|---|
| `cpu` | `cpu` | без изменений | — |
| `ram` | `memory` | переименование | dl1–dl5 |
| `ssd` | `storage_drive` | объединение | dl1–dl5 |
| `hdd` | `storage_drive` | объединение | dl1–dl5 |
| `nvme` | `storage_drive` | объединение | dl1–dl5 |
| `storage_controller` | `storage_controller` | без изменений | — |
| *(device_type=hba → hw_type=storage_controller)* | `hba` | исправление маппинга | dl1–dl5 |
| `backplane` | `backplane` | без изменений | — |
| — | `io_module` | новый тип | только новые вендоры |
| `network_adapter` | `network_adapter` | без изменений | — |
| `cable` | `cable` | сужение scope | — |
| *(sfp_cable → network_adapter для SFP/QSFP модулей)* | `transceiver` | исправление: модули ≠ NIC | ccw_1, ccw_2 |
| `psu` | `psu` | без изменений | — |
| *(device_type=power_cord)* | `None` | intentional, per business rules | — |
| `fan` | `fan` | без изменений | — |
| `cpu_heatsink` | `heatsink` | переименование | dl2–dl5 |
| `riser` | `riser` | без изменений | — |
| `chassis` | `chassis` | без изменений | — |
| `gpu` | `gpu` | без изменений | — |
| `tpm` | `tpm` | без изменений | — |
| `motherboard` | `chassis` | поглощение | dl (редкие) |
| `mounting_kit` | `rail` | переименование | dl1–dl5, ccw_1, ccw_2 |
| `blank` | `blank_filler` | переименование | dl1–dl5, ccw_2 |
| `management` | `management` | без изменений | — |
| — | `server` | новый тип (BASE) | только новые вендоры |
| — | `switch` | новый тип (BASE) | ccw golden при добавлении BASE rules |
| — | `storage_system` | новый тип (BASE) | только новые вендоры |
| — | `wireless_ap` | новый тип (BASE) | только новые вендоры |
| — | `accessory` | новый тип | ccw_2 (stacking module) |
| — | `storage_enclosure` | новый тип (Q2 cross-vendor) | huawei `DT-HU-008` (storage_enclosure) |
| `motherboard` | `chassis` | reaffirmed Lenovo precedent (Q1) | lenovo `HW-L-040 + DT-L-040` (motherboard:chassis), dell legacy |
| `accessory` (Lenovo Front Operator Panel) | `management` (via `device_type=front_panel`) | promotion (Q7a, PR-9a) | lenovo L1, L3, L10, L11 — 5 rows reclassified |
| `accessory` (Lenovo RoT Module) | `tpm` (via `device_type=tpm`) | promotion (Q7b, PR-9a) | lenovo L3, L4, L5, L6, L11 — 7 rows reclassified |
| `accessory` (Lenovo Power Distribution / Interface / Interconnect Board) | `chassis` (via `device_type=power_distribution_board`) | promotion (Q8, PR-9b) | lenovo L1 (CB9J, CBA4), L3 (BV23, BV24), L10 (CBWP, C9N7) |
| `accessory` (Lenovo PCIe Switch / Retimer Card / I/O Board) | `chassis` (via `device_type=interconnect_board`) | promotion (Q8, PR-9b) | lenovo L1 (CB9Q, CBA3), L3 (BV26), L8 (CA7N), L9 (C7Y8) |
| `accessory` (HPE Power Distribution Board Kit) | `chassis` (via `device_type=power_distribution_board`) | promotion (Q8, PR-9b) | hpe hp3, hp8 — P57888-B21 (6 rows) |
| `chassis` (Lenovo HDD/HD/NVMe Cage) | `backplane` (via `device_type=drive_cage`) | promotion (Q9, PR-9c, mirrors HPE PR-3) | lenovo L2 (B97T, BWKY), L3 (BV2K) |
| `chassis` (Lenovo Media Bay) | `chassis` (via new `device_type=media_bay`) | promotion (Q9, PR-9c) | lenovo L4 (BQ2M), L7 (BQ2M ×2), L8 (C1YP) |
| `cable` (Lenovo "Cable Riser") | `riser` (via `device_type=riser`) | promotion (Q10d, PR-10) | lenovo L8 (C1YH) |
| `gpu` (Lenovo "GPU air duct" — C3RP, false-match through HW-L-007-GPU) | `accessory` (via new `device_type=air_duct`) | promotion + bug-fix (Q10e, PR-10) | lenovo L9 (C3RP) |
| `accessory` (Lenovo Air Duct / Airduct) | `accessory` (via new `device_type=air_duct`) | semantic refinement (Q10e, PR-10) | lenovo L2 (BP46 ×7), L3 (BV2A), L5 (BQ2Z ×3), L7 (B8NM ×2) |
| `accessory` (xFusion Air duct) | `accessory` (via new `device_type=air_duct`) | semantic refinement (Q10e, PR-10) | xfusion xf1 (2120Y164, 2120Y397), xf3 (21205150, 21205144 ×2), xf5 (21206640, 2120Y222 ×2), xf6 (2120Y164), xf7/xf8 (2120Y222) |
| `accessory` (HPE DVD-RW / Optical Drive) | `storage_drive` (via new `device_type=optical_drive`) | promotion (Q10f, PR-10) | hpe hp7 (726537-B21) |

---

## Cross-vendor divergences (intentional)

Following stakeholder decisions Q1–Q5 (handoff PR-1 → PR-4c), the taxonomy intentionally diverges across vendors for some `device_type` → `hw_type` mappings. Each divergence is encoded at the YAML layer (`rules/<vendor>_rules.yaml` `device_type_map`) — global aliases in `batch_audit.py` are used only for AI_MISMATCH suppression, never as an `hw_type` mapping.

### bezel (Q5)
- HPE: `device_type=bezel, hw_type=chassis` (existing precedent — kept).
- Lenovo: `device_type=bezel, hw_type=accessory` (rule `HW-L-045-BEZEL` + `DT-L-045-BEZEL` + `lenovo_rules.yaml` map `bezel: accessory`).

The global `DEVICE_TYPE_ALIASES["bezel"] = "chassis"` in `batch_audit.py` is preserved to honor HPE's existing semantics; Lenovo's local `bezel: accessory` mapping resolves the divergence per-file. `bezel` is in `DEVICE_TYPE_TRUST` so the pipeline's value is always trusted over the AI prediction.

### backplane (Q3)
- xFusion: `DT-XF-022-BACKPLANE` → `device_type=backplane, hw_type=backplane`.
- HPE: `device_type=drive_cage` → mapped via local `device_type_map` to `hw_type=backplane` (PR-3, `2f327d1`).
- Cross-vendor alias: `DEVICE_TYPE_ALIASES["drive_cage"] = "backplane"` (PR-4c, flipped from `chassis`) suppresses AI_MISMATCH when the AI says "backplane" and the pipeline says "drive_cage".

### storage_enclosure (Q2)
- Huawei: `device_type=storage_enclosure, hw_type=storage_enclosure` (rule `DT-HU-008`).
- Cross-vendor category — not tied to a specific OEM. Future Dell PowerVault, HPE MSA, Lenovo DE / D1224, NetApp DS expected to use this type.
- `storage_enclosure` is in `DEVICE_TYPE_TRUST` (PR-3); pipeline value is always trusted.

### motherboard (Q1)
- Lenovo: `device_type=motherboard, hw_type=chassis` (rules `HW-L-040 + DT-L-040` + `lenovo_rules.yaml` map `motherboard: chassis`, PR-4a `e73538e`).
- Dell: legacy regex-based hw_type rule emits `hw_type=chassis` directly without `device_type=motherboard` (no separate device_type promotion). Dell upgrade tracked separately.
- Global alias: `DEVICE_TYPE_ALIASES["motherboard"] = "chassis"` (PR-4a). `motherboard` added to `DEVICE_TYPE_TRUST`.

### GPU Base (Q4)
- Lenovo: `entity_type=BASE, device_type=server` (rule `BASE-L-020-GPU-BASE` + `DT-L-060-GPU-BASE`, PR-4b `2e9e91c`). "GPU Base" SKUs describe the multi-GPU complex chassis foundation (the BASE machine), not a discrete GPU component.
- BASE rows do not get `hw_type` (`hw_type_rules.applies_to: [HW]`); the type is read from `device_type=server`.

### Front Operator Panel (Q7a, PR-9a)
- Lenovo: `device_type=front_panel, hw_type=management` (rules `HW-L-046-FRONT-PANEL` + `DT-L-046-FRONT-PANEL` + `lenovo_rules.yaml` map `front_panel: management`). Lenovo Docs document Front Operator Panel as server controls/LEDs/status display — management class.
- Pattern is intentionally narrow: matches `Front Operator Panel` and `LCD system information display` only. BV2C "Serial Port and Port for External Operator Panel" is a rear-panel I/O accessory and stays at `accessory` via `HW-L-027-ACCESSORY`.
- `front_panel` is in `DEVICE_TYPE_TRUST` and aliased to `management` in `DEVICE_TYPE_ALIASES` (batch_audit.py) so AI predictions of "management" do not flag AI_MISMATCH.

### Root of Trust Module (Q7b, PR-9a)
- Lenovo: `device_type=tpm, hw_type=tpm` (rules `HW-L-047-ROT-MODULE` + `DT-L-047-ROT-MODULE`). Lenovo documents RoT as "Firmware and Root of Trust/TPM 2.0 Security Module" — same security bucket as TPM 2.0.
- Existing `HW-L-024-TPM` (`\bTPM\s+\d`) continues to handle bare "TPM 2.0" SKUs; new rule `HW-L-047-ROT-MODULE` covers `Root of Trust Module`, `RoT Module`, and HW variants of `Firmware and Root of Trust`. Both rules emit identical output (`device_type=tpm, hw_type=tpm`).
- HW-L-034 (legacy `Retimer|RoT|Root of Trust|Enablement Kit` → accessory) was narrowed to `Retimer|Enablement Kit` only; RoT is no longer routed to `accessory`.
- Note: `SW-L-010` (`\bFirmware\b.*\b(Root\s+of\s+Trust|Security\s+Module)\b`) fires BEFORE HW rules in the classifier pipeline, so SKUs whose option_name begins with "Firmware and Root of Trust Security Module" (e.g. BYQL/BM8S) continue to route to SOFTWARE — out of scope for PR-9a.

### Power Distribution Board (Q8, PR-9b)
- Lenovo: `device_type=power_distribution_board, hw_type=chassis` (rules `HW-L-053-PDB` + `DT-L-053-PDB` + `lenovo_rules.yaml` map `power_distribution_board: chassis`).
- HPE: `device_type=power_distribution_board, hw_type=chassis` (entity rule `HW-H-GLOBAL-034` unchanged + device-type rule renamed to `HW-H-080-PDB` with output flipped from `accessory` to `power_distribution_board` + `hpe_rules.yaml` map `power_distribution_board: chassis`).
- Pattern is intentionally narrow: requires the literal "Board" suffix. Lenovo regex `\bPower\s+(?:Distribution|Interface|Interconnect)\s+Board\b` covers "Power Distribution Board", "Power Interface Board", "Power Interconnect Board". HPE regex `(?i)power\s+distribution\s+board` covers HPE's "Power Distribution Board" / "Power Distribution Board Kit" SKU naming.
- HW-L-027-ACCESSORY catch-all was trimmed: `Power\s+(?:Distribution|Interface|Interconnect)` removed (extracted into `HW-L-053-PDB`). Cables ("Power Cord", "16-pin GPU Power Cable From Power Distribution Board") and PSU ("1100W Titanium Power Supply") do NOT match — they hit `HW-L-017-POWERCORD`, `HW-L-016-PSU`, or HPE cable rules first.
- `power_distribution_board` is in `DEVICE_TYPE_TRUST` and aliased to `chassis` in `DEVICE_TYPE_ALIASES` (batch_audit.py) so AI predictions of "chassis" or "accessory" do not flag AI_MISMATCH.

### Interconnect Board (Q8, PR-9b)
- Lenovo: `device_type=interconnect_board, hw_type=chassis` (rules `HW-L-049-INTERCONNECT-BOARD` + `DT-L-049-INTERCONNECT-BOARD` + `lenovo_rules.yaml` map `interconnect_board: chassis`). Replaces and broadens the prior PR-4c rule `HW-L-047-PCIE-SWITCH-BOARD` (which only caught PCIe Switch Board → accessory/accessory).
- HPE: device_type_map slot reserved (`interconnect_board: chassis`) but no HPE SKUs match yet — added for cross-vendor parity.
- Pattern requires "Board" or "Card" suffix: `\b(?:PCIe\s+Switch\s+Board|(?:PCIe\s+)?Retimer\s+(?:Card|Board)|(?:System\s+)?I[/-]?O\s+Board)\b`. Covers "PCIe Switch Board", "PCIe Retimer Card", "Retimer Board", "System I/O Board", "I/O Board".
- **Distinct from `motherboard`** (Q1, main system board): "ThinkSystem SR650 V3 MB" (BLL0) keeps routing to `HW-L-040-MOTHERBOARD` → `motherboard/chassis`. The interconnect regex never matches bare "MB" or "System Board".
- **Distinct from `io_module`** (Huawei storage pluggable): Huawei rules `HW-HU-001-IO-MODULE` / `DT-HU-001-IO-MODULE` apply only to Huawei files, and the lowercase "module" suffix (vs "Board") prevents cross-vendor regex collisions even at the pattern level.
- **Interaction with `HW-L-034` (Retimer / Enablement Kit)**: HW-L-049 fires first for "PCIe Retimer Card" / "Retimer Board"; HW-L-034 still catches bare "Retimer" or "Enablement Kit" (no Board/Card suffix) → `accessory`.
- HW-L-027-ACCESSORY catch-all was trimmed: `I\/O` removed from the catch-all (extracted into `HW-L-049-INTERCONNECT-BOARD`). Cables ("OCP I/O Adapter" without "Board") fall through.
- `interconnect_board` is in `DEVICE_TYPE_TRUST` and aliased to `chassis` in `DEVICE_TYPE_ALIASES` (batch_audit.py).

### HDD Cage / Drive Cage (Q9, PR-9c)
- Lenovo: `device_type=drive_cage, hw_type=backplane` (rules `HW-L-061-DRIVE-CAGE` + `DT-L-061-DRIVE-CAGE` + `lenovo_rules.yaml` map `drive_cage: backplane`). Mirrors HPE drive_cage semantics established in PR-3 (`drive_cage→backplane` flip from `chassis`).
- HPE: existing — `device_type=drive_cage, hw_type=backplane` via `HW-H-GLOBAL-028` / `HW-H-066` and `hpe_rules.yaml` map `drive_cage: backplane` (PR-3, `2f327d1`). Unchanged by PR-9c.
- Pattern requires literal "Cage" suffix: `\b(?:HDD|HD|NVMe(?:\s+HDD)?)\s+Cage\b`. Covers "HDD Cage", "HD Cage", "NVMe Cage", "NVMe HDD Cage", and numeric-prefixed variants like `MidBay 4X3.5" HDD Cage`, `Rear 4x2.5" NVMe HDD Cage`, `2.5" HD Cage`.
- HW-L-023-CHASSIS catch-all was trimmed from `(Chassis|HDD\s+Cage|HD\s+Cage|Media\s+Bay|Bezel)` to `(Chassis|Bezel)` — drive cages and media bays now have their own rules.
- "HDD Filler" (no "Cage" suffix) does NOT match — it routes to `blank_filler` via `DT-L-005-BLANK`.
- `drive_cage` added to `DEVICE_TYPE_TRUST` and already aliased to `backplane` in `DEVICE_TYPE_ALIASES` (PR-4c).

### Media Bay (Q9, PR-9c)
- Lenovo: `device_type=media_bay, hw_type=chassis` (rules `HW-L-062-MEDIA-BAY` + `DT-L-062-MEDIA-BAY` + `lenovo_rules.yaml` map `media_bay: chassis`). Brand-new device_type added for Lenovo "Media Bay" SKUs that are removable physical bays which may host front I/O panels, optical/tape devices, or other front-mounted gear — not always drive cages.
- **Distinct from `drive_cage`** (drive-specific, → backplane): Media Bay is more general; hw_type stays `chassis` (safer than `backplane`) because the bay's contents are device-agnostic.
- Pattern: `\bMedia\s+Bay\b` — narrow, requires both tokens contiguous. "Storage media" (no "Bay") and "Multimedia" (no `\b` before "Media") do NOT match.
- `media_bay` is in `DEVICE_TYPE_TRUST` and aliased to `chassis` in `DEVICE_TYPE_ALIASES` (batch_audit.py).

### Cable Riser (Q10d, PR-10)
- Lenovo: `device_type=riser, hw_type=riser` (rules `HW-L-063-CABLE-RISER` + `DT-L-063-CABLE-RISER`). Promotes "PCIe Cable Riser" SKUs (e.g. C1YH "ThinkSystem SR630 V4 x16/x16 PCIe Gen5 Cable Riser 1") from `cable/cable` to `riser/riser`.
- Pattern is intentionally narrow: `\bCable\s+Riser\b` — requires the literal "Cable Riser" bigram. Plain "PCIe Power Cable" / "GPU Power Cable" do NOT match (no Riser keyword) — they fall through to `HW-L-050-CABLE-THROUGH`.
- MUST fire BEFORE `HW-L-050-CABLE-THROUGH` (which would otherwise hijack via the literal "Cable" token) and BEFORE `HW-L-007-GPU` (no GPU keyword in the test SKU but kept for symmetry with riser-vs-cable precedence).
- A plain Riser SKU (no "Cable" prefix, e.g. "ThinkSystem SR650 V3 PCIe Gen5 Riser1 or 2 v2") still routes via the existing `HW-L-020-RISER`. The new rule is strictly additive.

### Air Duct (Q10e, PR-10)
- Lenovo: `device_type=air_duct, hw_type=accessory` (rules `HW-L-064-AIR-DUCT` + `DT-L-064-AIR-DUCT` + `lenovo_rules.yaml` map `air_duct: accessory`). Brand-new device_type added for Lenovo "Air Duct" / "Airduct" SKUs (BP46, BV2A, B8NM, BQ2Z, C3RP).
- xFusion: `device_type=air_duct, hw_type=accessory` (DT rule split — `DT-XF-018A-AIR-DUCT` for `Air duct` only + `DT-XF-018-ACCESSORY` for `Fan bracket` / `Extended radiator` only + `xfusion_rules.yaml` map `air_duct: accessory`). Entity rule `HW-XF-018-AIR-DUCT-ACCESSORY` itself unchanged. Affected SKUs: 2120Y164, 2120Y397, 21205150, 21205144, 21206640, 2120Y222.
- **Why `accessory` and NOT `cooling`:** the canonical 26-value `HW_TYPE_VOCAB` does NOT contain a `cooling` bucket. Per PR-10 spec, airflow guides map to the `accessory` bucket — distinct from `heatsink` (heat-conducting metal fin stack) and `fan` (active cooling).
- Pattern (Lenovo): `(?:\bAir\s*Duct\b|\bAirduct\b)(?!.*\bFiller\b)` — covers "Air Duct", "Air duct", "AirDuct", "Airduct" forms. Negative-lookahead `(?!.*\bFiller\b)` defends against "Air Duct Filler" (B8MP) which must keep routing to `blank_filler` via the earlier `DT-L-005-BLANK` rule.
- **Position:** Lenovo `HW-L-064-AIR-DUCT` MUST fire BEFORE `HW-L-007-GPU` (so C3RP "ThinkSystem 2U GPU air duct" no longer false-matches via the GPU keyword) AND BEFORE `HW-L-027-ACCESSORY` (which used to swallow Air Duct via its catch-all). xFusion `DT-XF-018A-AIR-DUCT` MUST fire BEFORE `DT-XF-018-ACCESSORY`.
- **Air Baffle is intentionally NOT included** in the new air_duct device_type — the PR-10 spec narrows on literal "Air Duct" tokens only. "Air Baffle" SKUs (BT6C, BT6E) keep routing to `accessory/accessory` via `HW-L-027-ACCESSORY`.
- HPE: no air_duct migration in PR-10. HPE "Air Baffle Kit" (P57887-B21) remains `accessory/accessory`.
- `air_duct` is in `DEVICE_TYPE_TRUST` and aliased to `accessory` in `DEVICE_TYPE_ALIASES` (batch_audit.py) so AI predictions of "accessory" do not flag AI_MISMATCH.

### Optical Drive (Q10f, PR-10)
- HPE: `device_type=optical_drive, hw_type=storage_drive` (rules `HW-H-081-OPTICAL-DRIVE` (renamed from `HW-H-081`) and `HW-H-082-DVD` (renamed from `HW-H-082`) — both now output `optical_drive` instead of `accessory`; entity rule `HW-H-GLOBAL-038` unchanged + `hpe_rules.yaml` map `optical_drive: storage_drive`).
- Pattern: `(?i)optical\s+drive` and `(?i)\bdvd\b`. Covers "DVD-RW Optical Drive", "DVD-ROM", "Optical Drive", "CD-ROM", "Blu-ray". Real production SKU: 726537-B21 "HPE 9.5mm SATA DVD-RW Optical Drive".
- **Mapped to `storage_drive`** — same bucket as HDD/SSD/NVMe storage drives. An optical disk drive IS a removable storage media reader; sharing the bucket simplifies storage-rollup queries.
- Lenovo: no optical_drive SKUs observed in fixtures; rules not extended in PR-10.
- xFusion: no optical_drive SKUs observed in fixtures; rules not extended in PR-10.
- Negative guards: HPE "Drive Cage Kit" (P75741-B21) does NOT match (regex requires `dvd|optical drive|cd-rom|blu-ray`); generic "SAS HDD" / "NVMe SSD" do NOT match — they keep their existing `storage_hdd` / `storage_nvme` device_types.
- `optical_drive` is in `DEVICE_TYPE_TRUST` and aliased to `storage_drive` in `DEVICE_TYPE_ALIASES` (batch_audit.py).

---

## Матрица покрытия по вендорам

| `hw_type` | Dell | HPE | Cisco | Lenovo | xFusion | Huawei СХД | Huawei WLAN |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `server` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `switch` | — | — | ✓ | — | — | — | ✓ |
| `storage_system` | — | — | — | — | — | ✓ | — |
| `wireless_ap` | — | — | — | — | — | — | ✓ |
| `cpu` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `memory` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `gpu` | ✓ | ✓ | — | — | — | — | — |
| `storage_drive` | ✓ | ✓ | — | ✓ | ✓ | ✓ | — |
| `storage_controller` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `hba` | ✓ | ✓ | — | — | ✓ | — | — |
| `backplane` | ✓ | ✓ (incl. `drive_cage:backplane`, PR-3) | — | ✓ (incl. `drive_cage:backplane`, PR-9c — mirrors HPE) | ✓ | — | — |
| `storage_enclosure` | — | — | — | — | — | ✓ | — |
| `io_module` | — | — | — | — | — | ✓ | — |
| `network_adapter` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `transceiver` | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| `cable` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `psu` | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `fan` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `heatsink` | ✓ | ✓ | — | ✓ | — | — | — |
| `riser` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `chassis` | ✓ | ✓ (incl. `power_distribution_board:chassis`) | — | ✓ (incl. `motherboard:chassis`, `power_distribution_board:chassis`, `interconnect_board:chassis`, `media_bay:chassis`) | — | — | — |
| `management` | ✓ | ✓ | ✓ | ✓ (incl. `front_panel:management`) | — | — | — |
| `tpm` | ✓ | — | — | ✓ (incl. RoT: `Root of Trust Module`) | — | — | — |
| `rail` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `blank_filler` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `accessory` | — | ✓ | ✓ | ✓ (incl. Lenovo-local `bezel:accessory`, `air_duct:accessory`) | ✓ (incl. `air_duct:accessory`) | — | ✓ |
| *`power_cord`* | *dt only* | *dt only* | *dt only* | *dt only* | *dt only* | — | — |
| *`enablement_kit`* | — | *dt only* | — | — | *dt only* | — | — |
| *`front_panel`* | — | — | — | *dt only → `management`* | — | — | — |
| *`power_distribution_board`* | — | *dt only → `chassis`* | — | *dt only → `chassis`* | — | — | — |
| *`interconnect_board`* | — | *dt only → `chassis`* | — | *dt only → `chassis`* | — | — | — |
| *`media_bay`* | — | — | — | *dt only → `chassis`* | — | — | — |
| *`drive_cage`* | — | *dt only → `backplane`* | — | *dt only → `backplane`* | — | — | — |
| *`air_duct`* | — | — | — | *dt only → `accessory`* | *dt only → `accessory`* | — | — |
| *`optical_drive`* | — | *dt only → `storage_drive`* | — | — | — | — | — |

---

## YAML-контракт (шпаргалка для правил)

```yaml
# hw_type_rules.applies_to — только HW; BASE и LOGISTIC намеренно не включаются
hw_type_rules:
  applies_to: [HW]

# device_type_rules.applies_to — для текущих YAML: HW, LOGISTIC, BASE
device_type_rules:
  applies_to: [HW, LOGISTIC, BASE]

# device_type_map — исправить hba:
device_type_map:
  hba: hba                       # было: hba → storage_controller  ← ИСПРАВИТЬ
  raid_controller: storage_controller
  transceiver: transceiver       # новый device_type для SFP/QSFP модулей
  sfp_cable: cable               # DAC/AOC/patch cord → cable (без изменений)

# Кабели питания — hw_type=None (intentional, per business rules):
# entity_type=HW, device_type=power_cord, hw_type=None

# Enablement kits — hw_type не присваивается:
# entity_type=HW, device_type=enablement_kit, hw_type=None ← намеренно
```

---

## Фильтрация в отчётах

| Задача | Фильтр |
|--------|--------|
| Все серверы в спецификации | `entity_type=BASE AND hw_type=server` |
| Сетевое оборудование (коммутаторы) | `entity_type=BASE AND hw_type=switch` |
| Все накопители (SSD+HDD+NVMe вместе) | `hw_type=storage_drive` |
| FC и SAS HBA (не RAID) | `hw_type=hba` |
| Только RAID-контроллеры | `hw_type=storage_controller` |
| Оптика для портов (трансиверы) | `hw_type=transceiver` |
| Кабели сигнальные (DAC/AOC/fiber) | `hw_type=cable` |
| Кабели питания | `device_type=power_cord` |
| Enablement / option kits | `device_type=enablement_kit` |
| Стоимость охлаждения | `hw_type IN (fan, heatsink)` |
| Управление (iDRAC/iLO/XCC) | `hw_type=management` |

---

*Source of truth для `HW_TYPE_VOCAB` в `src/core/classifier.py` и всех `*_rules.yaml`. Версия v2.6.0 — PR-11: консолидация cycle 2 (master matrix выше); **новых hw_type в cycle 2 не было**.*
