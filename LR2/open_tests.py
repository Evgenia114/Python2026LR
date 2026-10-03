from article_aggregator import (
    build_application,
    create_article,
    make_pipeline,
    make_service_monitor,
)


def make_scripted_source(responses):
    responses = list(responses)
    state = {"position": 0, "calls": 0}

    def fetch():
        state["calls"] += 1
        position = state["position"]
        state["position"] += 1
        return responses[min(position, len(responses) - 1)]

    return fetch, state


def raw_article(article_id="a-1", title="  Python   Functions ", **extra):
    article = {
        "id": article_id,
        "title": title,
        "text": "  Functions are objects.  ",
        "tags": [" Python ", "Functions", "python"],
        "rating": 10,
    }
    article.update(extra)
    return article


def test_create_article():
    tags = [" Python ", "Functions", "python", "  "]
    article = create_article(
        "a-1",
        "  Python   Functions ",
        "  Text.  ",
        source="habr",
        tags=tags,
        rating=10,
    )

    assert article == {
        "id": "a-1",
        "title": "Python Functions",
        "text": "Text.",
        "source": "habr",
        "tags": ["python", "functions"],
        "metadata": {"rating": 10},
    }
    assert tags == [" Python ", "Functions", "python", "  "]


def test_pipeline():
    normalize = make_pipeline(str.strip, str.lower, lambda text: text + "!")
    identity = make_pipeline()

    assert normalize("  PyThOn  ") == "python!"
    assert identity([1, 2]) == [1, 2]


def test_monitor():
    monitor = make_service_monitor(2)

    assert monitor["record"](False) is True
    assert monitor["record"](False) is False
    assert monitor["can_call"]() is False
    assert monitor["status"]()["failures"] == 2

    result = monitor["reset"]()
    assert result["available"] is True
    assert result["failures"] == 0


def test_fetch_and_catalog():
    source, _ = make_scripted_source([[raw_article()]])
    run = build_application({"habr": source}, max_failures=2)

    assert run("fetch", "habr") == {
        "status": "ok",
        "source": "habr",
        "received": 1,
        "added": 1,
        "updated": 0,
    }

    articles = run("list")
    assert len(articles) == 1
    assert articles[0]["title"] == "Python Functions"
    assert articles[0]["tags"] == ["python", "functions"]
    assert articles[0]["metadata"] == {"rating": 10}


def test_block_and_reset():
    source, source_state = make_scripted_source([None, None, [raw_article()]])
    run = build_application({"habr": source}, max_failures=2)

    assert run("fetch", "habr")["status"] == "unavailable"
    assert run("fetch", "habr")["status"] == "unavailable"
    assert run("fetch", "habr")["status"] == "blocked"
    assert source_state["calls"] == 2
    assert run("status", "habr")["available"] is False

    run("reset", "habr")
    assert run("fetch", "habr")["status"] == "ok"
    assert source_state["calls"] == 3


def test_search_and_safe_copies():
    source, _ = make_scripted_source(
        [[
            raw_article("a-1"),
            raw_article(
                "a-2",
                title="Closures",
                text="Lexical scope and state",
                tags=["Scope"],
                rating=20,
            ),
        ]]
    )
    run = build_application({"habr": source})
    run("fetch", "habr")

    assert [article["id"] for article in run("search", "functions")] == ["a-1"]
    assert [article["id"] for article in run("search", "", tag=" SCOPE ")] == ["a-2"]

    result = run("list")
    result[0]["title"] = "Changed"
    result[0]["tags"].append("changed")
    result[0]["metadata"]["rating"] = 999

    stored = run("list")[0]
    assert stored["title"] == "Python Functions"
    assert "changed" not in stored["tags"]
    assert stored["metadata"]["rating"] == 10


def test_stats_and_commands():
    habr, _ = make_scripted_source([[raw_article("h-1")]])
    blog, _ = make_scripted_source([[raw_article("b-1")]])
    run = build_application({"habr": habr, "blog": blog})

    run("fetch", "habr")

    assert run("stats") == {
        "total_articles": 1,
        "by_source": {"habr": 1, "blog": 0},
        "available_sources": ("habr", "blog"),
    }
    assert run("commands") == (
        "fetch",
        "list",
        "search",
        "stats",
        "status",
        "reset",
        "commands",
    )


def test_update_and_independence():
    first_source, _ = make_scripted_source(
        [
            [raw_article("same", title="First")],
            [raw_article("same", title="Updated"), raw_article("new", title="New")],
        ]
    )
    second_source, _ = make_scripted_source([[raw_article("other")]])

    first = build_application({"habr": first_source})
    second = build_application({"habr": second_source})

    first("fetch", "habr")
    assert first("fetch", "habr") == {
        "status": "ok",
        "source": "habr",
        "received": 2,
        "added": 1,
        "updated": 1,
    }
    assert [article["id"] for article in first("list")] == ["same", "new"]
    assert first("list")[0]["title"] == "Updated"
    assert second("list") == []


TESTS = [
    test_create_article,
    test_pipeline,
    test_monitor,
    test_fetch_and_catalog,
    test_block_and_reset,
    test_search_and_safe_copies,
    test_stats_and_commands,
    test_update_and_independence,
]


def main():
    passed = 0

    for test in TESTS:
        try:
            test()
        except Exception as error:
            print(f"FAIL: {test.__name__}: {type(error).__name__}: {error}")
        else:
            passed += 1
            print(f"OK:   {test.__name__}")

    print(f"\nОткрытые проверки: {passed}/{len(TESTS)}")
    return 0 if passed == len(TESTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
