from insurminds.services.json_utils import JSONResponseError, parse_json_object


def test_parse_plain_json():
    assert parse_json_object('{"items": []}') == {"items": []}


def test_parse_fenced_json():
    assert parse_json_object('Resposta:\n```json\n{"ok": true}\n```') == {"ok": True}


def test_reject_non_object():
    try:
        parse_json_object("[1, 2]")
    except JSONResponseError:
        return
    raise AssertionError("Era esperado JSONResponseError")

