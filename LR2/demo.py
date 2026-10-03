from pprint import pprint

from article_aggregator import build_application


def make_scripted_source(responses):
    responses = list(responses)
    position = 0

    def fetch():
        nonlocal position

        if position >= len(responses):
            return responses[-1]

        response = responses[position]
        position += 1
        return response

    return fetch


HABR_ARTICLES = [
    {
        "id": "habr-1",
        "title": "  Замыкания   в Python  ",
        "text": "  Практическое введение в функции и области видимости.  ",
        "tags": [" Python ", "Functions", "python"],
        "rating": 42,
    },
    {
        "id": "habr-2",
        "title": "Генераторы без магии",
        "text": "Как работают yield и ленивые вычисления.",
        "tags": ["Python", "Generators"],
        "rating": 35,
    },
]

BLOG_ARTICLES = [
    {
        "id": "blog-1",
        "title": "Функции как объекты",
        "text": "Callback-функции, конвейеры и таблицы команд.",
        "tags": ["functions", "Architecture"],
        "rating": 18,
    }
]


def main():
    sources = {
        "habr": make_scripted_source([None, None, HABR_ARTICLES]),
        "blog": make_scripted_source([BLOG_ARTICLES]),
    }
    run = build_application(sources, max_failures=2)

    print("1. Успешно загружаем статьи из blog")
    pprint(run("fetch", "blog"))

    print("\n2. Habr дважды недоступен")
    pprint(run("fetch", "habr"))
    pprint(run("fetch", "habr"))

    print("\n3. Следующий запрос заблокирован и не вызывает источник")
    pprint(run("fetch", "habr"))
    pprint(run("status", "habr"))

    print("\n4. Сбрасываем монитор и повторяем загрузку")
    pprint(run("reset", "habr"))
    pprint(run("fetch", "habr"))

    print("\n5. Каталог")
    pprint(run("list"))

    print("\n6. Поиск Python-статей")
    pprint(run("search", "python", tag="python"))

    print("\n7. Статистика")
    pprint(run("stats"))


if __name__ == "__main__":
    main()
