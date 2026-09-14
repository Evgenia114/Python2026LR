# Лабораторная работа №1 — расширенный вариант

## Объекты, ссылки, изменяемость, копирование и hashability

Работа состоит из шести независимых мини-задач. В каждой нужно реализовать несколько функций и проследить, какие объекты должны быть новыми, какие — общими, а какие следует изменить на месте.

Работа выполняется в обычной IDE и сдаётся как Git-проект с файлами `.py`. Notebook для сдачи не нужен.

## Границы работы

В работе используются только идеи первого занятия и базовый синтаксис Python:

- имена и объекты;
- `is` и `==`;
- mutable и immutable объекты;
- aliasing;
- безопасное значение изменяемого аргумента по умолчанию;
- shallow copy и deep copy;
- изменяемый объект внутри tuple;
- hashability, `tuple` и `frozenset`.

В этой работе **не требуется**:

- писать собственные тесты;
- обрабатывать некорректные входные данные;
- использовать `try/except` или создавать исключения;
- использовать классы, декораторы, генераторы и type hints;
- устанавливать сторонние библиотеки.

Все входные данные в проверках корректны. Готовый `check.py` нужно только запускать; устройство чекера пока не является темой курса.

## Структура проекта

```text
README.md
student_info.py
task01_settings.py
task02_grid.py
task03_tag_index.py
task04_cards.py
task05_snapshots.py
task06_request_cache.py
check.py
```

Заполните `student_info.py`, затем реализуйте функции в `task*.py`. Имена файлов и функций менять нельзя.

## Запуск открытой проверки

```bash
python check.py
```

Полностью выполненная работа должна показать:

```text
Открытые проверки: 20/20
```

На сервере преподавателя выполняются дополнительные проверки с другими данными.

## Как читать примеры

Реализуемые функции **не должны самостоятельно печатать результат**. Они получают аргументы, при необходимости изменяют переданные объекты и возвращают значение через `return`.

В примерах `print(...)` вызывается снаружи только для того, чтобы показать ожидаемый результат. Проверки с `is` важны не меньше проверок с `==`:

- `==` проверяет равенство содержимого;
- `is` проверяет, является ли результат тем же самым объектом.

---

## Задача 1. Сеанс изменения настроек — 15 баллов

Файл: `task01_settings.py`

### `add_change`

```python
def add_change(key, value, changes=None):
    ...
```

**Вход:** строка `key`, произвольный объект `value` и необязательный список `changes`.

**Результат:** список изменений, в конец которого добавлен кортеж `(key, value)`. Объект `value` копировать не нужно.

Если `changes` не передан, каждый вызов должен получить новый список:

```python
first = add_change("theme", "dark")
second = add_change("language", "ru")

print(first)            # [("theme", "dark")]
print(second)           # [("language", "ru")]
print(first is second)  # False
```

Если список передан, изменяется и возвращается именно он.

```python
changes = [("theme", "light")]
result = add_change("theme", "dark", changes)

print(result)             # [("theme", "light"), ("theme", "dark")]
print(result is changes)  # True
```

### `apply_changes`

```python
def apply_changes(settings, changes):
    ...
```

**Вход:** словарь `settings` и список кортежей вида `(ключ, значение)`.

**Результат:** тот же словарь `settings`, изменённый в соответствии с журналом. Функция не создаёт новый словарь:

```python
settings = {"theme": "light", "language": "en"}
changes = [("theme", "dark"), ("font_size", 16)]

result = apply_changes(settings, changes)

print(result is settings)  # True
print(settings)
# {"theme": "dark", "language": "en", "font_size": 16}
```

Изменения применяются слева направо. Если ключ встречается несколько раз, остаётся последнее значение:

```python
settings = {"volume": 10}
apply_changes(settings, [("volume", 20), ("volume", 5)])

print(settings)  # {"volume": 5}
```

### `build_settings`

```python
def build_settings(base, changes):
    ...
```

**Вход:** исходный словарь `base` и список изменений вида `(ключ, значение)`.

**Результат:** новый словарь. Сначала необходимо получить глубокую копию `base`, затем применить изменения к копии. Исходный `base` изменяться не должен, включая вложенные контейнеры.

```python
base = {"theme": "light", "panels": {"left": ["files"]}}
result = build_settings(base, [("theme", "dark")])

result["panels"]["left"].append("search")

print(base["panels"]["left"])    # ["files"]
print(result["panels"]["left"])  # ["files", "search"]
print(result is base)              # False
```

---

## Задача 2. Сетка независимых карточек — 20 баллов

Файл: `task02_grid.py`

### `make_grid`

```python
def make_grid(rows, columns, template):
    ...
```

**Вход:** положительные целые числа `rows` и `columns`, а также словарь-шаблон `template`.

**Результат:** список из `rows` строк; каждая строка является списком из `columns` ячеек. Каждая ячейка должна содержать отдельную глубокую копию `template`.

```python
template = {"value": "", "marks": []}
grid = make_grid(2, 3, template)

grid[0][0]["marks"].append("selected")

print(grid[0][0])  # {"value": "", "marks": ["selected"]}
print(grid[0][1])  # {"value": "", "marks": []}
print(template)    # {"value": "", "marks": []}
print(grid[0] is grid[1])          # False
print(grid[0][0] is grid[0][1])    # False
```

Независимыми должны быть и строки сетки, и словари в ячейках, и вложенные изменяемые объекты шаблона.

### `update_cell`

```python
def update_cell(grid, row, column, field, value):
    ...
```

**Вход:** существующая сетка, корректные номера строки и столбца, строка `field` и значение `value`.

**Результат:** тот же объект `grid`. Функция должна изменить словарь, который уже находится в выбранной ячейке, а не заменить всю ячейку другим словарём.

```python
grid = make_grid(1, 2, {"value": "", "marks": []})
cell = grid[0][1]

result = update_cell(grid, 0, 1, "value", "A")

print(result is grid)       # True
print(grid[0][1] is cell)   # True
print(grid[0][1])           # {"value": "A", "marks": []}
print(grid[0][0])           # {"value": "", "marks": []}
```

### `replace_cell`

```python
def replace_cell(grid, row, column, new_cell):
    ...
```

**Вход:** сетка, корректные номера строки и столбца и новый словарь `new_cell`.

**Результат:** старый словарь, который находился в выбранной ячейке до замены. В самой сетке выбранная ячейка теперь должна ссылаться ровно на объект `new_cell`.

```python
old_cell = grid[0][1]
new_cell = {"value": "X", "marks": []}

result = replace_cell(grid, 0, 1, new_cell)

print(result is old_cell)       # True
print(grid[0][1] is new_cell)   # True
print(grid[0][1])               # {"value": "X", "marks": []}
```

`new_cell` копировать не нужно.

---

## Задача 3. Индекс документов по тегам — 20 баллов

Файл: `task03_tag_index.py`

Документ имеет вид:

```python
{"id": 101, "title": "Python objects", "tags": ["python", "course"]}
```

Теги одного документа не повторяются.

### `build_tag_index`

```python
def build_tag_index(documents):
    ...
```

**Вход:** список словарей-документов.

**Результат:** новый словарь, где ключ — тег, а значение — список документов с этим тегом:

```python
documents = [
    {"id": 1, "title": "Objects", "tags": ["python", "course"]},
    {"id": 2, "title": "Git", "tags": ["tools", "course"]},
]

index = build_tag_index(documents)

print([doc["id"] for doc in index["course"]])  # [1, 2]
print([doc["id"] for doc in index["python"]])  # [1]
print(index["python"][0] is documents[0])       # True
print(index["python"] is index["course"])      # False
```

Требования:

- списки разных тегов являются разными объектами;
- сами документы копировать не нужно;
- в индексе должны находиться те же словари, что и в `documents`;
- порядок документов внутри списка совпадает с порядком входного списка;
- список `documents` и сами документы функция не изменяет.

Один документ может находиться сразу в нескольких списках индекса. Это намеренный aliasing.

### `attach_tag`

```python
def attach_tag(document, tag, index):
    ...
```

**Вход:** словарь `document`, строка `tag` и уже существующий словарь `index`.

**Результат:** тот же объект `index`. Функция выполняет два согласованных изменения:

1. добавляет `tag` в `document["tags"]`;
2. добавляет исходный объект `document` в `index[tag]`.

Если ключа `tag` в индексе ещё нет, для него создаётся новый список.

Передаваемого тега ещё нет у документа, а документа ещё нет в списке этого тега.

```python
document = {"id": 1, "title": "Objects", "tags": ["python"]}
index = {"python": [document]}

result = attach_tag(document, "course", index)

print(result is index)                 # True
print(document["tags"])               # ["python", "course"]
print(index["course"][0]["id"])       # 1
print(index["course"][0] is document) # True
```

---

## Задача 4. Карточка с изменяемым содержимым — 15 баллов

Файл: `task04_cards.py`

Карточка представлена кортежем (`tuple`):

```text
(код, список_меток)
```

### `make_card`

```python
def make_card(code, labels=None):
    ...
```

**Вход:** строка `code` и необязательный список `labels`.

**Результат:** кортеж `(code, labels)`. Если `labels` не передан, разные вызовы должны получать разные пустые списки. Если список передан, карточка должна содержать именно его, без копирования.

```python
first = make_card("A-1")
second = make_card("A-2")
labels = ["new"]
third = make_card("A-3", labels)

print(first)                 # ("A-1", [])
print(second)                # ("A-2", [])
print(first[1] is second[1]) # False
print(third[1] is labels)    # True
```

### `add_label`

```python
def add_label(card, label):
    ...
```

**Вход:** карточка `card` и строка `label`.

**Результат:** исходный кортеж `card`. Изменяется только вложенный список меток.

```python
card = ("A-1", ["new"])
result = add_label(card, "sale")

print(result is card)  # True
print(card)            # ("A-1", ["new", "sale"])
```

### `change_code`

```python
def change_code(card, new_code):
    ...
```

**Вход:** карточка `card` и строка `new_code`.

**Результат:** новый кортеж с новым кодом, но с тем же объектом списка меток. Исходный кортеж не изменяется.

```python
card = ("A-1", ["new"])
changed = change_code(card, "A-2")

print(changed is card)             # False
print(changed[1] is card[1])       # True
print(card)                        # ("A-1", ["new"])
print(changed)                     # ("A-2", ["new"])
```

### `clone_card`

```python
def clone_card(card):
    ...
```

**Вход:** карточка `card`.

**Результат:** новый кортеж с тем же кодом и новым независимым списком меток.

```python
card = ("A-1", ["new"])
cloned = clone_card(card)
cloned[1].append("sale")

print(cloned is card)        # False
print(cloned[1] is card[1])  # False
print(card)                  # ("A-1", ["new"])
print(cloned)                # ("A-1", ["new", "sale"])
```

---

## Задача 5. Хранилище снимков состояния — 15 баллов

Файл: `task05_snapshots.py`

### `save_shallow`

```python
def save_shallow(history, state):
    ...
```

**Вход:** список снимков `history` и словарь `state`.

**Результат:** тот же список `history`, в конец которого добавлена поверхностная копия `state`. Внешний словарь снимка новый, но его вложенные объекты остаются общими с `state`.

```python
state = {"items": ["A"], "options": {"visible": True}}
history = []
result = save_shallow(history, state)

print(result is history)                    # True
print(history[0] is state)                  # False
print(history[0]["items"] is state["items"]) # True

state["items"].append("B")
print(history[0]["items"])                 # ["A", "B"]
```

### `save_deep`

```python
def save_deep(history, state):
    ...
```

**Вход:** список снимков `history` и словарь `state`.

**Результат:** тот же список `history`, в конец которого добавлена глубокая копия `state`. Вложенные изменяемые объекты снимка не должны быть общими с `state`.

```python
state = {"items": ["A"], "options": {"visible": True}}
history = []
result = save_deep(history, state)

state["items"].append("B")

print(result is history)       # True
print(history[0] is state)     # False
print(history[0]["items"])    # ["A"]
print(state["items"])         # ["A", "B"]
```

### `restore`

```python
def restore(history, index):
    ...
```

**Вход:** список сохранённых состояний `history` и корректный целочисленный индекс `index`.

**Результат:** глубокая копия `history[index]`. Изменение восстановленного объекта не должно изменять снимок в истории.

```python
state = {"items": ["A"], "options": {"visible": True}}
history = []
save_deep(history, state)

restored = restore(history, 0)
restored["items"].append("B")

print(history[0]["items"])  # ["A"]
print(restored["items"])    # ["A", "B"]
```

---

## Задача 6. Ключи и группировка запросов — 15 баллов

Файл: `task06_request_cache.py`

Запрос имеет фиксированную структуру:

```python
request = {
    "path": "/courses",
    "fields": ["name", "teacher"],
    "tags": {"python", "first-year"},
    "options": {"limit": 10, "active": True},
}
```

`path`, элементы `fields`, элементы `tags` и ключи `options` — строки. Значения `options` являются хешируемыми неизменяемыми объектами.

### `make_request_key`

```python
def make_request_key(request):
    ...
```

**Вход:** один словарь-запрос фиксированной структуры, показанной выше.

**Результат:** хешируемый кортеж вида:

```text
(
    path,
    fields_as_tuple,
    tags_as_frozenset,
    sorted_options_as_tuple,
)
```

Для примера выше последняя часть равна:

```python
(("active", True), ("limit", 10))
```

Полный пример результата удобнее проверять сравнением, поскольку порядок отображения `frozenset` может различаться:

```python
key = make_request_key(request)
expected = (
    "/courses",
    ("name", "teacher"),
    frozenset({"python", "first-year"}),
    (("active", True), ("limit", 10)),
)

print(key == expected)  # True
print(hash(key))         # некоторое целое число; ошибки быть не должно
```

Смысл полей:

- порядок `fields` имеет значение;
- порядок `tags` не имеет значения;
- порядок добавления элементов в `options` не имеет значения;
- исходный запрос изменять нельзя.

### `group_requests`

```python
def group_requests(requests):
    ...
```

**Вход:** список словарей-запросов.

**Результат:** новый словарь, который группирует исходные запросы по результату `make_request_key`:

```text
ключ запроса -> список исходных запросов с таким ключом
```

Эквивалентные запросы попадают в один список. Сами запросы копировать не нужно: в списках должны находиться исходные объекты. Порядок запросов внутри группы должен сохраняться.

```python
first = {
    "path": "/courses",
    "fields": ["name"],
    "tags": {"python", "new"},
    "options": {"limit": 10, "active": True},
}
second = {
    "path": "/courses",
    "fields": ["name"],
    "tags": {"new", "python"},
    "options": {"active": True, "limit": 10},
}
third = {
    "path": "/courses",
    "fields": ["teacher"],
    "tags": {"python", "new"},
    "options": {"limit": 10, "active": True},
}

groups = group_requests([first, second, third])
first_key = make_request_key(first)
third_key = make_request_key(third)

print(len(groups))                       # 2
print(groups[first_key] == [first, second]) # True
print(groups[third_key] == [third])      # True
print(groups[first_key][0] is first)     # True
```
---
## Как сдавать

1. Откройте полученный Git-репозиторий в IDE.
2. Заполните `student_info.py` и реализуйте функции.
3. По ходу работы запускайте `python check.py`.
4. Добейтесь результата `20/20`.
5. Сделайте финальный commit и отправьте его в удалённый репозиторий.

## Требования к проекту

- изменяйте только `student_info.py` и `task*.py`;
- не переименовывайте функции;
- не используйте `input()` и вывод при импорте;
- используйте только стандартную библиотеку;
- не добавляйте `.idea`, `.vscode`, `.venv`, `venv` и `__pycache__` в Git;
- делайте несколько небольших осмысленных коммитов.
