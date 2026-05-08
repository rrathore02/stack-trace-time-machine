from stt.flaky import confirm, wrap_predicate


def test_confirms_real_failure_when_consistent():
    verdict = confirm(lambda: False, runs=3, fail_threshold=0.6)
    assert verdict.confirmed_failure
    # Short-circuits as soon as threshold is reached; with runs=3, threshold=0.6
    # that happens after the 2nd failure. So we should see >=2 failures, not 3.
    assert verdict.failures >= 2
    assert verdict.runs <= 3


def test_acquits_test_that_only_fails_once():
    calls = iter([False, True, True])
    verdict = confirm(lambda: next(calls), runs=3, fail_threshold=0.6)
    assert not verdict.confirmed_failure


def test_short_circuits_once_threshold_unreachable():
    # With threshold 0.6 and runs=3, two passes already make confirmation
    # impossible — confirm should stop early.
    calls_made = {"n": 0}

    def fn() -> bool:
        calls_made["n"] += 1
        return True  # always passes

    confirm(fn, runs=3, fail_threshold=0.6)
    assert calls_made["n"] <= 2


def test_wrap_predicate_passes_passes_through():
    """A passing inner predicate should never trigger re-runs."""
    calls = {"n": 0}

    def inner(_sha: str) -> bool:
        calls["n"] += 1
        return True

    wrapped = wrap_predicate(inner, runs=5, fail_threshold=0.6)
    assert wrapped("abc") is True
    assert calls["n"] == 1


def test_wrap_predicate_runs_one_when_runs_is_one():
    inner_calls = {"n": 0}

    def inner(_sha: str) -> bool:
        inner_calls["n"] += 1
        return False

    wrapped = wrap_predicate(inner, runs=1)
    wrapped("abc")
    assert inner_calls["n"] == 1
