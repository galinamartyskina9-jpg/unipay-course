# Исходные проверки ЛР6

Успешных проверок: **35**. Ожидаемых падений: **7**.

Не завершены новое поведение, его сочетание с прежними правилами и подключение. Отдельные проверки сравнивают настройки одного класса и поведение после отказа.

Падения ниже связаны с конкретными требованиями [TASK.md](TASK.md). После обязательной части все они должны пройти. Бонус проверяется отдельно и не входит в эти числа.

## Новые последовательности и конфигурации

- `tests.test_progression::test_progression_default_assembly_uses_group`
- `tests.test_progression::test_progression_extra_lab06`
- `tests.test_progression::test_progression_group_bad_result_and_error`
- `tests.test_progression::test_progression_group_order_snapshot_and_identity`

## Предметный контракт и общий интерфейс

- `tests.test_contract::test_extension_denies_only_its_condition`
- `tests.test_contract::test_extension_is_registered`
- `tests.test_review_contract::test_review_contactless_flag_three_cases`

## Порядок проверки

Из корня проекта: `python check.py lab06`. Сначала прочитайте первый traceback и ожидаемый результат сценария. Не отключайте тесты, которые пока не проходят.

Ошибка импорта или установки не относится к заданию. Если исходный набор результатов отличается, сохраните вывод и сообщите преподавателю; не удаляйте решения и служебные файлы.
