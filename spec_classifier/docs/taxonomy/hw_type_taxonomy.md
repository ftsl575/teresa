# hw_type Taxonomy — Universal Device Type Dictionary
## Универсальный словарь типов устройств / spec_classifier teresa

**Version:** v1.1.0  
**Date:** 2026-02-28  
**Vendors covered:** Dell · HPE · Cisco CCW · Lenovo · xFusion · Huawei (OceanStor + WLAN)  
**Replaces:** `HW_TYPE_VOCAB` v1.2.0 (20 values) → v2.0.0 (**25 values**)

---

## Зафиксированные решения

| # | Вопрос | Решение |
|---|--------|---------|
| 1 | hba vs storage_controller — разделять? | **Да.** `hba` = FC HBA + SAS HBA (любой host bus adapter без встроенного RAID). `storage_controller` = только RAID с кешем/батареей (PERC/Smart Array/BOSS/MegaRAID). |
| 2 | transceiver выделять из sfp_cable? | **Да.** SFP/SFP28/QSFP **модули** → `transceiver`. DAC/AOC/patch cord → `cable`. |
| 3 | BASE rows нужен hw_type? | **Да.** `hw_type_applies_to: [HW, BASE]`. Без явного правила BASE → `hw_type: None` (не warning, не ошибка). |
| 4 | enablement_kit — hw_type или device_type? | **Только `device_type`.** `entity_type=HW`, `device_type=enablement_kit`, `hw_type=None`. В `HW_TYPE_VOCAB` **не входит**. |
| 5 | software_license/service в hw_type? | **Нет.** `hw_type_applies_to` = `[HW, BASE]`. SOFTWARE/SERVICE — только `entity_type`. |
| 6 | power_cord — hw_type или device_type? | **Только `device_type`.** `hw_type_applies_to` остаётся `[HW, BASE]`. Строки `power_cord` имеют `entity_type=HW`, `hw_type=None`. |

---

## Словарь (25 значений hw_type)

### Группа 1 — Основное изделие (только BASE rows)

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `server` | Server / Compute Node | Сервер / Вычислительный узел | PowerEdge R660, ProLiant DL380 Gen12 CTO, ThinkSystem SR630 V3, 1288H V7 |
| `switch` | Switch / Router | Коммутатор / Маршрутизатор | N9K-C93180YC-FX3, Catalyst 9500-48Y4C, C8500L-8S4X, S5700 |
| `storage_system` | Storage System | Система хранения данных | OceanStor Dorado 5000 V6 NVMe Controller Enclosure |
| `wireless_ap` | Wireless AP / Controller | Точка доступа Wi-Fi / Контроллер | AirEngine 9700-M1, AirEngine 5761R-11, AC6805 |

> `hw_type_applies_to: [HW, BASE]`. Если тип BASE-изделия не распознан — `hw_type: None` (не warning).

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
| `backplane` | Backplane / Drive Cage | Объединительная панель / Корзина | HPE Tri-Mode U.3 Drive Cage Kit, ThinkSystem 1U 8×2.5" SAS/SATA Backplane |
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

> **Кабели питания** (`power_cord`): `entity_type=HW`, `device_type=power_cord`, `hw_type=None`. `hw_type_applies_to` не включает `power_cord` — намеренное решение. Тип читается из `device_type`.

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
| `management` | Management Module / BMC License | Модуль управления / BMC | HPE iLO Advanced License, XClarity Controller Platinum, HPE OneView FIO Bundle |
| `tpm` | TPM / Security Module | Модуль безопасности TPM | TPM 2.0, Dell TPM 2.0 v3 |

---

### Группа 9 — Аксессуары

| Код (`hw_type`) | English Name | Русское наименование | Примеры |
|---|---|---|---|
| `accessory` | Accessory / Misc Hardware | Аксессуар / Прочее | NVIDIA NVLink Bridge 2-way/4-way, C9300L-STACK-A Stacking Module, RFID, Antenna |

---

## Отдельные device_type (вне HW_TYPE_VOCAB)

Эти значения существуют **только на уровне `device_type`**, `hw_type` всегда `None`:

| `device_type` | Описание | `entity_type` | `hw_type` |
|---|---|---|---|
| `power_cord` | Кабель питания (C13/C14/C15/C19) | HW | `None` — намеренно |
| `enablement_kit` | Enablement / Option Kit (HPE FIO, xFusion option cables) | HW | `None` — намеренно |

---

## Итоговый HW_TYPE_VOCAB (25 значений)

```python
HW_TYPE_VOCAB = frozenset({
    # Основное изделие (BASE rows)
    "server", "switch", "storage_system", "wireless_ap",
    # Вычислительные компоненты
    "cpu", "memory", "gpu",
    # Подсистема хранения
    "storage_drive", "storage_controller", "hba", "backplane", "io_module",
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
    # --- LEGACY (временно, удаляется после обновления golden в Фазах 2–3) ---
    "ram", "ssd", "hdd", "nvme", "cpu_heatsink",
    "motherboard", "mounting_kit", "blank",
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
| *(device_type=power_cord → hw_type=None)* | `None` | остаётся None | — |
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
| `backplane` | ✓ | ✓ | — | ✓ | — | — | — |
| `io_module` | — | — | — | — | — | ✓ | — |
| `network_adapter` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `transceiver` | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| `cable` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `psu` | ✓ | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| `fan` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `heatsink` | ✓ | ✓ | — | ✓ | — | — | — |
| `riser` | ✓ | ✓ | — | ✓ | ✓ | — | — |
| `chassis` | ✓ | — | — | ✓ | — | — | — |
| `management` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `tpm` | ✓ | — | — | ✓ | — | — | — |
| `rail` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `blank_filler` | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `accessory` | — | ✓ | ✓ | ✓ | — | — | ✓ |
| *`power_cord`* | *dt only* | *dt only* | *dt only* | *dt only* | *dt only* | — | — |
| *`enablement_kit`* | — | *dt only* | — | — | *dt only* | — | — |

---

## YAML-контракт (шпаргалка для правил)

```yaml
# hw_type_rules.applies_to — HW и BASE, LOGISTIC намеренно не включается
hw_type_rules:
  applies_to: [HW, BASE]

# device_type_rules.applies_to — без изменений
device_type_rules:
  applies_to: [HW, LOGISTIC]

# device_type_map — исправить hba:
device_type_map:
  hba: hba                       # было: hba → storage_controller  ← ИСПРАВИТЬ
  raid_controller: storage_controller
  transceiver: transceiver       # новый device_type для SFP/QSFP модулей
  sfp_cable: cable               # DAC/AOC/patch cord → cable (без изменений)

# Кабели питания — hw_type не присваивается:
# entity_type=HW, device_type=power_cord, hw_type=None ← намеренно

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

*Source of truth для `HW_TYPE_VOCAB` в `classifier.py` и всех `*_rules.yaml`. Версия v1.1.0.*
