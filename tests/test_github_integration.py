from stt.github_integration import build_revert_pr


def test_build_revert_pr_includes_sha_and_test():
    pr = build_revert_pr(
        bad_sha="abcdef1234567890",
        base_branch="main",
        bisect_log=[("aaa111", True), ("bbb222", False)],
        failing_test="tests/test_x.py::test_y",
    )
    assert "abcdef1234567890" in pr.body
    assert "tests/test_x.py::test_y" in pr.body
    assert pr.branch == "stt/revert-abcdef12"
    assert pr.base == "main"


def test_build_revert_pr_renders_log():
    pr = build_revert_pr(
        bad_sha="ff" * 20,
        base_branch="main",
        bisect_log=[("aaa111", True), ("bbb222", False)],
        failing_test="t",
    )
    assert "aaa111" in pr.body and "bbb222" in pr.body
    assert "pass" in pr.body and "fail" in pr.body


def test_build_revert_pr_truncates_huge_traces():
    pr = build_revert_pr(
        bad_sha="00" * 20,
        base_branch="main",
        bisect_log=[],
        failing_test="t",
        stack_trace="x" * 10_000,
    )
    # Truncated to ~2000 chars + the surrounding markdown.
    assert len(pr.body) < 4000
