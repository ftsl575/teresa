# Current State — spec_classifier (teresa)

## Версия
1.2.0

## Дата последнего аудита
2026-03-01

## Активные вендоры
- Dell (spec export)
- Cisco (CCW — Commerce Workspace)

## Статус классификации
- unknown_count = 0 на всех датасетах (dl1–dl5, ccw_1, ccw_2)
- hw_type_null_count = 0

## Известные проблемы
- Смотри CHANGELOG.md [Unreleased]

## Структура docs/
- docs/user/       — инструкции для пользователей
- docs/dev/        — инструкции для разработчиков
- docs/schemas/    — контракты данных (DATA_CONTRACTS.md)
- docs/taxonomy/   — справочники типов
- docs/rules/      — документация правил классификации
- docs/product/    — TECHNICAL_OVERVIEW.md (единственный актуальный обзор)
- docs/archive/    — замёрзшие материалы (не актуальны)

## Workflow
Claude анализирует репо → пишет промпты → Cursor выполняет →
Claude проводит аудит после каждого набора изменений.
