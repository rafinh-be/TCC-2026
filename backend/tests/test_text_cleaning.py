from text_cleaning import clean_latex_math


def test_replacement_table_inside_span():
    assert clean_latex_math("PA $\\ge 140$ mmHg") == "PA >= 140 mmHg"
    assert clean_latex_math("FC $\\le 100$") == "FC <= 100"
    assert clean_latex_math("dose de 5 $\\mu$g") == "dose de 5 µg"
    assert clean_latex_math("temperatura $38^\\circ$C") == "temperatura 38°C"


def test_text_command_is_unwrapped():
    assert clean_latex_math("$\\text{mg}/\\text{dL}$") == "mg/dL"


def test_text_outside_spans_is_untouched():
    text = "use snake_case e arquivo_final_v2.md com \\ge fora"
    assert clean_latex_math(text) == text


def test_snake_case_outside_and_math_inside_together():
    result = clean_latex_math("campo_um vale $\\ge 3$ em campo_dois")
    assert result == "campo_um vale >= 3 em campo_dois"


def test_spaces_collapse_only_inside_span():
    assert clean_latex_math("a   b $x   \\ge   y$ c   d") == "a   b x >= y c   d"


def test_multiple_spans():
    assert clean_latex_math("$\\ge 1$ e $\\le 2$") == ">= 1 e <= 2"


def test_longer_commands_are_not_mangled():
    assert clean_latex_math("$\\left( x \\right)$") == "\\left( x \\right)"


def test_empty_and_none_input():
    assert clean_latex_math("") == ""
    assert clean_latex_math(None) is None


def test_no_dollar_returns_identical_string():
    text = "texto  sem   matematica_aqui\n\noutro paragrafo"
    assert clean_latex_math(text) == text


def test_unpaired_dollar_is_untouched():
    text = "custa $5 e mais_um"
    assert clean_latex_math(text) == text
