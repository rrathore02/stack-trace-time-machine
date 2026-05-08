from stt.stack_trace import extract_python_files


SAMPLE_PYTRACE = """\
============================= test session starts =============================
collected 1 item

tests/test_thing.py F

================================== FAILURES ===================================
______________________________ test_thing_works _______________________________

    def test_thing_works():
>       assert thing.compute() == 42

tests/test_thing.py:7:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

src/thing.py:14: in compute
    return helper()
src/helpers.py:3: in helper
    raise ValueError("bad input")
E   ValueError: bad input

  File "/some/path/site-packages/_pytest/runner.py", line 99, in some_pytest_internal
    do_thing()
"""


def test_extracts_user_files_in_order():
    files = extract_python_files(SAMPLE_PYTRACE)
    assert files == ["tests/test_thing.py", "src/thing.py", "src/helpers.py"]


def test_drops_site_packages_and_pytest_internals():
    files = extract_python_files(SAMPLE_PYTRACE)
    assert not any("site-packages" in f for f in files)
    assert not any("_pytest" in f for f in files)


def test_handles_windows_paths():
    text = '  File "C:\\Users\\me\\proj\\src\\app.py", line 12'
    files = extract_python_files(text)
    assert files == ["C:/Users/me/proj/src/app.py"]


def test_returns_empty_for_unrelated_text():
    assert extract_python_files("nothing relevant here") == []


def test_dedupes_repeats():
    text = '  File "a.py", line 1\n  File "a.py", line 99'
    assert extract_python_files(text) == ["a.py"]
