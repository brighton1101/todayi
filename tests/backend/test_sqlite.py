from todayi.backend.sqlite import SqliteBackend, SqliteEntry, SqliteTag
from todayi.backend.filter import EntryFilterSettings
from todayi.model.tag import Tag


def test_reconcile_tags():
    backend = SqliteBackend(":memory:")
    session = backend._session
    dbtag = SqliteTag(name="hello", uuid="abc")
    session.add(dbtag)
    session.commit()
    tags = [
        Tag("hello", uuid="123"),
        Tag("abc", uuid="234"),
    ]
    reconciled = backend.reconcile_tags(tags)
    assert reconciled[0].name == "hello"
    assert reconciled[0].uuid == "abc"
    assert reconciled[1].name == "abc"
    assert reconciled[1].uuid == "234"


def test_read_entries_tag_filtering():
    backend = SqliteBackend(":memory:")
    session = backend._session
    tags = [
        SqliteTag(name="a", uuid="random"),
        SqliteTag(name="b", uuid="random2"),
        SqliteTag(name="c", uuid="random3"),
        SqliteTag(name="d", uuid="random4"),
    ]
    session.add_all(tags)
    session.commit()
    entries = [
        SqliteEntry(content="Entry 1", uuid="morerandom", tags=[tags[0], tags[1]]),
        SqliteEntry(content="Entry 2", uuid="morerandom2", tags=[tags[2], tags[3]]),
    ]
    session.add_all(entries)
    session.commit()

    res1 = backend.read_entries(
        EntryFilterSettings(
            without_tags=[
                Tag(name="a", uuid="qwerty"),
                Tag(name="b", uuid="lasjfd"),
            ]
        )
    )
    assert res1[0].content == "Entry 2"

    res2 = backend.read_entries(
        EntryFilterSettings(
            with_tags=[
                Tag(name="c", uuid="qwerty"),
                Tag(name="d", uuid="lasjfd"),
            ]
        )
    )[0]
    assert res2.content == "Entry 2"

    no_entries = backend.read_entries(
        EntryFilterSettings(
            with_tags=[
                Tag(name="b", uuid="qwerty"),
            ],
            without_tags=[Tag(name="a", uuid="lol")],
        )
    )
    assert len(no_entries) == 0


def test_read_entries_content_filtering():
    backend = SqliteBackend(":memory:")
    session = backend._session
    entries = [
        SqliteEntry(content="Entry 1", uuid="morerandom"),
        SqliteEntry(content="Entry 2", uuid="morerandom2"),
    ]
    session.add_all(entries)
    session.commit()

    res1 = backend.read_entries(EntryFilterSettings(content_contains="entry"))
    contents = [e.content for e in res1]
    assert "Entry 1" in contents
    assert "Entry 2" in contents

    res2 = backend.read_entries(EntryFilterSettings(content_equals="Entry 1"))
    assert len(res2) == 1
    assert res2[0].content == "Entry 1"

    res3 = backend.read_entries(
        EntryFilterSettings(
            content_contains="entry",
            content_not_equals="Entry 2",
        )
    )
    assert len(res3) == 1
    assert res3[0].content == "Entry 1"


def test_read_entries_datetime_filtering():
    pass
