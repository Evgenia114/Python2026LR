"""Открытая проверка расширенной ЛР1. Изменять этот файл не нужно."""

from task01_settings import add_change, apply_changes, build_settings
from task02_grid import make_grid, replace_cell, update_cell
from task03_tag_index import attach_tag, build_tag_index
from task04_cards import add_label, change_code, clone_card, make_card
from task05_snapshots import restore, save_deep, save_shallow
from task06_request_cache import group_requests, make_request_key


passed = 0
total = 0


def check(name, condition):
    global passed, total
    total += 1
    try:
        result = condition()
    except Exception as error:
        print(f"[FAIL] {name}: {type(error).__name__}: {error}")
        return
    if result:
        passed += 1
        print(f"[ OK ] {name}")
    else:
        print(f"[FAIL] {name}")


def changes_have_safe_default():
    first = add_change("theme", "dark")
    second = add_change("language", "ru")
    return first == [("theme", "dark")] and second == [("language", "ru")] and first is not second


def changes_use_passed_list():
    changes = [("a", 1)]
    result = add_change("b", 2, changes)
    return result is changes and changes == [("a", 1), ("b", 2)]


def changes_apply_in_place():
    settings = {"a": 0}
    result = apply_changes(settings, [("a", 1), ("b", 2), ("a", 3)])
    return result is settings and settings == {"a": 3, "b": 2}


def settings_are_deeply_independent():
    base = {"panel": {"items": ["files"]}}
    result = build_settings(base, [("theme", "dark")])
    result["panel"]["items"].append("search")
    return base == {"panel": {"items": ["files"]}} and result["theme"] == "dark"


def grid_has_shape():
    template = {"value": ""}
    return make_grid(2, 3, template) == [[template, template, template], [template, template, template]]


def grid_cells_are_independent():
    template = {"marks": []}
    grid = make_grid(2, 2, template)
    grid[0][0]["marks"].append("X")
    cells = [cell for row in grid for cell in row]
    return (
        len({id(row) for row in grid}) == 2
        and len({id(cell) for cell in cells}) == 4
        and grid[0][1]["marks"] == []
        and template["marks"] == []
    )


def update_changes_existing_cell():
    grid = make_grid(1, 2, {"value": "", "marks": []})
    cell = grid[0][1]
    result = update_cell(grid, 0, 1, "value", "A")
    return result is grid and grid[0][1] is cell and cell["value"] == "A"


def replace_rebinds_one_cell():
    grid = make_grid(1, 2, {"value": ""})
    old = grid[0][0]
    new = {"value": "N"}
    result = replace_cell(grid, 0, 0, new)
    return result is old and grid[0][0] is new and grid[0][1] is not new


def index_has_expected_content_and_aliases():
    first = {"id": 1, "tags": ["python", "course"]}
    second = {"id": 2, "tags": ["course"]}
    index = build_tag_index([first, second])
    return index == {"python": [first], "course": [first, second]} and index["python"][0] is first


def index_lists_are_independent_and_input_untouched():
    documents = [{"id": 1, "tags": ["a", "b"]}]
    before = documents[0]["tags"].copy()
    index = build_tag_index(documents)
    index["a"].append({"id": 2, "tags": []})
    return index["a"] is not index["b"] and index["b"] == [documents[0]] and documents[0]["tags"] == before


def tag_is_attached_to_both_structures():
    document = {"id": 1, "tags": ["python"]}
    index = {"python": [document]}
    result = attach_tag(document, "course", index)
    return result is index and document["tags"] == ["python", "course"] and index["course"] == [document] and index["course"][0] is document


def card_creation_respects_identity():
    first = make_card("A")
    second = make_card("B")
    labels = ["new"]
    third = make_card("C", labels)
    return first == ("A", []) and second == ("B", []) and first[1] is not second[1] and third[1] is labels


def card_label_changes_inner_list():
    card = ("A", ["new"])
    result = add_label(card, "sale")
    return result is card and card == ("A", ["new", "sale"])


def changed_code_shares_labels():
    card = ("A", ["new"])
    result = change_code(card, "B")
    return result == ("B", ["new"]) and result is not card and result[1] is card[1]


def cloned_card_has_new_labels():
    card = ("A", ["new"])
    result = clone_card(card)
    return result == card and result is not card and result[1] is not card[1]


def shallow_snapshot_shares_nested_state():
    state = {"items": ["A"]}
    history = []
    result = save_shallow(history, state)
    return result is history and history[0] is not state and history[0]["items"] is state["items"]


def deep_snapshot_is_independent():
    state = {"items": ["A"], "options": {"flags": []}}
    history = []
    result = save_deep(history, state)
    return result is history and history[0] == state and history[0]["items"] is not state["items"] and history[0]["options"] is not state["options"]


def restored_state_is_independent():
    history = [{"items": ["A"]}]
    result = restore(history, 0)
    result["items"].append("B")
    return history == [{"items": ["A"]}] and result == {"items": ["A", "B"]}


def request_key_is_correct_and_hashable():
    request = {
        "path": "/courses",
        "fields": ["name", "teacher"],
        "tags": {"python", "first-year"},
        "options": {"limit": 10, "active": True},
    }
    key = make_request_key(request)
    expected = (
        "/courses",
        ("name", "teacher"),
        frozenset({"python", "first-year"}),
        (("active", True), ("limit", 10)),
    )
    return key == expected and hash(key) == hash(expected)


def equivalent_requests_are_grouped():
    first = {"path": "/x", "fields": ["a"], "tags": {"p", "q"}, "options": {"limit": 1, "active": True}}
    second = {"path": "/x", "fields": ["a"], "tags": {"q", "p"}, "options": {"active": True, "limit": 1}}
    third = {"path": "/x", "fields": ["b"], "tags": {"p", "q"}, "options": {"limit": 1, "active": True}}
    grouped = group_requests([first, second, third])
    first_key = make_request_key(first)
    third_key = make_request_key(third)
    return len(grouped) == 2 and grouped[first_key] == [first, second] and grouped[third_key] == [third] and grouped[first_key][0] is first


check("1. Безопасный журнал по умолчанию", changes_have_safe_default)
check("1. Изменение переданного журнала", changes_use_passed_list)
check("1. Последовательное применение изменений", changes_apply_in_place)
check("1. Независимая сборка настроек", settings_are_deeply_independent)
check("2. Размер сетки", grid_has_shape)
check("2. Независимость строк и ячеек", grid_cells_are_independent)
check("2. Изменение существующей ячейки", update_changes_existing_cell)
check("2. Замена ссылки на ячейку", replace_rebinds_one_cell)
check("3. Содержимое и aliases индекса", index_has_expected_content_and_aliases)
check("3. Независимые списки индекса", index_lists_are_independent_and_input_untouched)
check("3. Добавление тега", tag_is_attached_to_both_structures)
check("4. Создание карточек", card_creation_respects_identity)
check("4. Изменяемый список внутри tuple", card_label_changes_inner_list)
check("4. Новый код и общий список", changed_code_shares_labels)
check("4. Независимый клон карточки", cloned_card_has_new_labels)
check("5. Поверхностный снимок", shallow_snapshot_shares_nested_state)
check("5. Глубокий снимок", deep_snapshot_is_independent)
check("5. Независимое восстановление", restored_state_is_independent)
check("6. Хешируемый ключ запроса", request_key_is_correct_and_hashable)
check("6. Группировка эквивалентных запросов", equivalent_requests_are_grouped)

print(f"\nОткрытые проверки: {passed}/{total}")
if passed != total:
    raise SystemExit(1)

