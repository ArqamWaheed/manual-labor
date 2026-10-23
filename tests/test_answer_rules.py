from manual_labor.answer import parse_json


def test_parse_strips_think_block():
    assert parse_json('<think>hmm</think>{"not_in_manual": true}') == {"not_in_manual": True}


def test_parse_finds_json_in_text():
    assert parse_json('Sure: {"steps": ["a"], "pages": [3]}')["pages"] == [3]
