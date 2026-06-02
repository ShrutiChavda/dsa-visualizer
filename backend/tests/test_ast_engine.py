"""
Tests for the DSA Visualizer AST Engine
"""
import pytest
from app.core.ast_engine import ASTEngine
from app.models.events import EventType


def engine():
    return ASTEngine()


class TestBasicAssignment:
    def test_integer_assignment(self):
        e = engine()
        result = e.execute("x = 5")
        assert result.success
        last_var_assign = next(
            ev for ev in reversed(result.events)
            if ev.event_type == EventType.VARIABLE_ASSIGN
        )
        assert last_var_assign.metadata["var_name"] == "x"
        assert last_var_assign.metadata["value"] == 5

    def test_list_assignment(self):
        e = engine()
        result = e.execute("nums = [1, 2, 3]")
        assert result.success
        array_init = next(
            ev for ev in result.events
            if ev.event_type == EventType.ARRAY_INIT
        )
        assert array_init.result == [1, 2, 3]


class TestBinaryOps:
    def test_subtraction_emits_binop_events(self):
        e = engine()
        result = e.execute("target = 9\nnums = [2, 7]\ni = 0\nneed = target - nums[i]")
        assert result.success
        types = [ev.event_type for ev in result.events]
        assert EventType.BINOP_EVAL in types
        assert EventType.BINOP_RESULT in types
        assert EventType.SUBSCRIPT_EVAL in types
        assert EventType.SUBSCRIPT_RESULT in types

    def test_addition(self):
        e = engine()
        result = e.execute("a = 3\nb = 4\nc = a + b")
        assert result.success
        final = result.events[-1]
        assert final.metadata.get("value") == 7


class TestControlFlow:
    def test_if_branch_taken(self):
        e = engine()
        result = e.execute("x = 5\nif x > 3:\n    y = 1")
        assert result.success
        branch_evs = [ev for ev in result.events if ev.event_type == EventType.IF_BRANCH]
        assert len(branch_evs) >= 1
        assert branch_evs[0].metadata["branch"] == "if"

    def test_if_else_branch(self):
        e = engine()
        result = e.execute("x = 1\nif x > 3:\n    y = 1\nelse:\n    y = 0")
        assert result.success
        branch_evs = [ev for ev in result.events if ev.event_type == EventType.IF_BRANCH]
        assert branch_evs[0].metadata["branch"] == "else"


class TestLoops:
    def test_for_loop_emits_iter_events(self):
        e = engine()
        result = e.execute("total = 0\nfor i in range(3):\n    total = total + i")
        assert result.success
        iter_evs = [ev for ev in result.events if ev.event_type == EventType.LOOP_ITER]
        assert len(iter_evs) == 3

    def test_while_loop(self):
        e = engine()
        result = e.execute("x = 0\nwhile x < 3:\n    x = x + 1")
        assert result.success


class TestTwoSum:
    def test_two_sum_full(self):
        e = engine()
        code = """\
nums = [2, 7, 11, 15]
target = 9
seen = {}
for i in range(len(nums)):
    need = target - nums[i]
    if need in seen:
        result = [seen[need], i]
    else:
        seen[nums[i]] = i
"""
        result = e.execute(code)
        assert result.success
        assert result.total_steps > 10
        # Check that 'need' gets assigned correctly in the first iteration
        need_assigns = [
            ev for ev in result.events
            if ev.event_type == EventType.VARIABLE_ASSIGN
            and ev.metadata.get("var_name") == "need"
        ]
        assert need_assigns[0].metadata["value"] == 7  # 9 - 2


class TestBinarySearch:
    def test_binary_search(self):
        e = engine()
        code = """\
nums = [1, 3, 5, 7, 9]
target = 7
left = 0
right = len(nums) - 1
result = -1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        result = mid
        left = right + 1
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
"""
        result = e.execute(code)
        assert result.success
        result_assigns = [
            ev for ev in result.events
            if ev.event_type == EventType.VARIABLE_ASSIGN
            and ev.metadata.get("var_name") == "result"
            and ev.metadata.get("value") != -1
        ]
        assert len(result_assigns) >= 1
        assert result_assigns[0].metadata["value"] == 3  # index of 7
