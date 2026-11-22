from core.manager import check_tool


def test_check_tool_returns_expected_fields():
    result = check_tool("kicad")

    assert "name" in result
    assert "installed" in result
    assert "path" in result
    assert "version" in result