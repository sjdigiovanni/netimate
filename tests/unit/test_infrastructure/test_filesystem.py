# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pytest
from netimate.infrastructure.template_provider.filesystem import FileSystemTemplateProvider


@pytest.fixture
def template_provider(tmp_path):
    # Create a dummy template file
    (tmp_path / "dummy.textfsm").write_text("Value TEST (.*)\n\nStart\n  ^${TEST}$$")
    (tmp_path / "dummy.ttp").write_text("{{ TEST }}")
    return FileSystemTemplateProvider([str(tmp_path)])


def test_read_existing_textfsm_template(template_provider):
    content = template_provider._get("dummy.textfsm")
    assert "Value TEST" in content


def test_read_existing_ttp_template(template_provider):
    content = template_provider._get("dummy.ttp")
    assert "{{ TEST }}" in content


def test_template_not_found(template_provider):
    with pytest.raises(FileNotFoundError):
        template_provider._get("nonexistent.textfsm")


def test_parse_textfsm(template_provider):
    raw_output = "HelloWorld"
    parsed = template_provider.parse("dummy.textfsm", raw_output)
    assert isinstance(parsed, list)
    assert parsed[0]["TEST"] == "HelloWorld"


def test_parse_ttp(template_provider):
    raw_output = "HelloWorld"
    parsed = template_provider.parse("dummy.ttp", raw_output)
    assert isinstance(parsed, dict)
    assert "TEST" in parsed
    assert parsed["TEST"] == "HelloWorld"


def test_parse_no_template_path(template_provider):
    output = template_provider.parse(None, "raw text")
    assert output is None


def test_exists_true(template_provider):
    assert template_provider.exists("dummy.textfsm") is True


def test_exists_false(template_provider):
    assert template_provider.exists("nonexistent.textfsm") is False


def test_list_templates(template_provider):
    templates = list(template_provider.list_templates())
    assert "dummy.textfsm" in templates
    assert "dummy.ttp" in templates
