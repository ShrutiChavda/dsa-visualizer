"""
DSA Visualizer - Event Models
Defines the data structures for all execution events.
"""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class EventType(str, Enum):
    # Variables
    VARIABLE_ASSIGN = "variable_assign"
    VARIABLE_READ = "variable_read"

    # Assignments
    ASSIGNMENT_START = "assignment_start"
    SUBSCRIPT_ASSIGN = "subscript_assign"

    # Expressions
    BINOP_EVAL = "binop_eval"
    BINOP_RESULT = "binop_result"
    SUBSCRIPT_EVAL = "subscript_eval"
    SUBSCRIPT_RESULT = "subscript_result"
    COMPARISON_EVAL = "comparison_eval"
    COMPARISON_RESULT = "comparison_result"

    # Control flow
    IF_TEST = "if_test"
    IF_BRANCH = "if_branch"

    # Loops
    LOOP_START = "loop_start"
    LOOP_ITER = "loop_iter"
    LOOP_END = "loop_end"

    # Functions
    FUNCTION_CALL = "function_call"
    FUNCTION_RETURN = "function_return"

    # Data structures
    ARRAY_INIT = "array_init"
    DICT_INIT = "dict_init"

    # Output
    PRINT_OUTPUT = "print_output"


# Color coding for event types
EVENT_COLORS: dict[EventType, str] = {
    EventType.VARIABLE_ASSIGN: "#22d3ee",
    EventType.VARIABLE_READ: "#a78bfa",
    EventType.ASSIGNMENT_START: "#fbbf24",
    EventType.SUBSCRIPT_ASSIGN: "#34d399",
    EventType.BINOP_EVAL: "#f97316",
    EventType.BINOP_RESULT: "#fb923c",
    EventType.SUBSCRIPT_EVAL: "#60a5fa",
    EventType.SUBSCRIPT_RESULT: "#93c5fd",
    EventType.COMPARISON_EVAL: "#f472b6",
    EventType.COMPARISON_RESULT: "#ec4899",
    EventType.IF_TEST: "#fde047",
    EventType.IF_BRANCH: "#facc15",
    EventType.LOOP_START: "#4ade80",
    EventType.LOOP_ITER: "#86efac",
    EventType.LOOP_END: "#bbf7d0",
    EventType.FUNCTION_CALL: "#c084fc",
    EventType.FUNCTION_RETURN: "#d8b4fe",
    EventType.ARRAY_INIT: "#38bdf8",
    EventType.DICT_INIT: "#7dd3fc",
    EventType.PRINT_OUTPUT: "#94a3b8",
}

EVENT_ICONS: dict[EventType, str] = {
    EventType.VARIABLE_ASSIGN: "📝",
    EventType.VARIABLE_READ: "👁",
    EventType.ASSIGNMENT_START: "⚡",
    EventType.SUBSCRIPT_ASSIGN: "🔧",
    EventType.BINOP_EVAL: "🔢",
    EventType.BINOP_RESULT: "✅",
    EventType.SUBSCRIPT_EVAL: "🔍",
    EventType.SUBSCRIPT_RESULT: "📌",
    EventType.COMPARISON_EVAL: "⚖️",
    EventType.COMPARISON_RESULT: "🎯",
    EventType.IF_TEST: "❓",
    EventType.IF_BRANCH: "↩️",
    EventType.LOOP_START: "🔄",
    EventType.LOOP_ITER: "➡️",
    EventType.LOOP_END: "🏁",
    EventType.FUNCTION_CALL: "📞",
    EventType.FUNCTION_RETURN: "↩",
    EventType.ARRAY_INIT: "📦",
    EventType.DICT_INIT: "🗂️",
    EventType.PRINT_OUTPUT: "🖨️",
}


class VariableState(BaseModel):
    name: str
    value: Any
    type: str
    display: str


class MemoryState(BaseModel):
    variables: dict[str, VariableState]
    call_stack: list[str]
    output: list[str]


class ExecutionEvent(BaseModel):
    step: int
    event_type: EventType
    description: str
    expression: Optional[str] = None
    result: Optional[Any] = None
    result_display: Optional[str] = None
    memory: MemoryState
    highlight_vars: list[str] = []
    line_number: Optional[int] = None
    metadata: dict[str, Any] = {}
    color: Optional[str] = None
    icon: Optional[str] = None

    def model_post_init(self, __context):
        self.color = EVENT_COLORS.get(self.event_type, "#64748b")
        self.icon = EVENT_ICONS.get(self.event_type, "•")


class ExecutionResult(BaseModel):
    events: list[ExecutionEvent]
    error: Optional[str] = None
    success: bool
    total_steps: int


class ExecuteRequest(BaseModel):
    code: str
    initial_vars: dict[str, Any] = {}
    problem_id: Optional[str] = None


class DSAProblem(BaseModel):
    id: str
    title: str
    description: str
    code: str
    initial_vars: dict[str, Any]
    tags: list[str]
    difficulty: str
