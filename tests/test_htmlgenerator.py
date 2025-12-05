import pytest

from app import HTMLGenerator


def test_calculate_word_count_simple():
    structure = {
        "title": "T",
        "description": "D",
        "cover_page": {
            "id": "cover",
            "title": "封面",
            "content": [
                {"id": "h1", "type": "heading", "text": "你好"},
                {"id": "p1", "type": "paragraph", "text": "这是一个测试。"}
            ]
        },
        "pages": [
            {"id": "pg1", "content": [{"id": "p2", "type": "paragraph", "text": "更多内容"}]}
        ],
        "config": {"theme": "light"}
    }

    # 计算字数应等于字符串长度之和（简单实现）
    expected = len("你好") + len("这是一个测试。") + len("更多内容")
    assert HTMLGenerator.calculate_word_count(structure) == expected
