"""
DSA Visualizer - AST Execution Engine
Parses Python code and generates granular execution events,
breaking down every expression evaluation step-by-step.
"""
import ast
import copy
from typing import Any, Optional
from app.models.events import (
    ExecutionEvent, EventType, MemoryState, VariableState,
    ExecutionResult
)


class StepError(Exception):
    pass


class ASTEngine:
    """
    Walks Python AST nodes and emits detailed execution events.
    Unlike Python Tutor, we trace EVERY sub-expression evaluation.
    """

    def __init__(self):
        self.events: list[ExecutionEvent] = []
        self.variables: dict[str, Any] = {}
        self.step_counter = 0
        self.call_stack: list[str] = ["<module>"]
        self.output_lines: list[str] = []

    def _next_step(self) -> int:
        self.step_counter += 1
        return self.step_counter

    def _snapshot_memory(self) -> MemoryState:
        """Snapshot current variable state for memory panel."""
        variables = {}
        for name, value in self.variables.items():
            variables[name] = VariableState(
                name=name,
                value=self._serialize_value(copy.deepcopy(value)),
                type=type(value).__name__,
                display=self._display_value(value)
            )
        return MemoryState(
            variables=variables,
            call_stack=list(self.call_stack),
            output=list(self.output_lines)
        )

    def _serialize_value(self, value: Any) -> Any:
        """Convert non-serializable types to JSON-safe equivalents."""
        if isinstance(value, range):
            return list(value)
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        return value

    def _display_value(self, value: Any) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, range):
            return f"range({value.start}, {value.stop}, {value.step})"
        return str(value)

    def _emit(self, event_type: EventType, description: str,
              expression: Optional[str] = None,
              result: Optional[Any] = None,
              highlight_vars: Optional[list[str]] = None,
              line_number: Optional[int] = None,
              metadata: Optional[dict] = None) -> ExecutionEvent:
        step = _next_step = self._next_step()
        memory = self._snapshot_memory()
        event = ExecutionEvent(
            step=step,
            event_type=event_type,
            description=description,
            expression=expression,
            result=self._serialize_value(result) if result is not None else None,
            result_display=self._display_value(result) if result is not None else None,
            memory=memory,
            highlight_vars=highlight_vars or [],
            line_number=line_number,
            metadata=self._serialize_value(metadata or {})
        )
        self.events.append(event)
        return event

    # ─── Expression Evaluators ────────────────────────────────────────────────

    def eval_expr(self, node: ast.expr, line: int) -> Any:
        """Recursively evaluate an expression, emitting events at each step."""
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            name = node.id
            if name not in self.variables:
                raise StepError(f"NameError: '{name}' is not defined")
            val = self.variables[name]
            self._emit(
                EventType.VARIABLE_READ,
                f"Read variable `{name}`",
                expression=name,
                result=val,
                highlight_vars=[name],
                line_number=line,
                metadata={"var_name": name}
            )
            return val

        elif isinstance(node, ast.Subscript):
            return self._eval_subscript(node, line)

        elif isinstance(node, ast.BinOp):
            return self._eval_binop(node, line)

        elif isinstance(node, ast.UnaryOp):
            return self._eval_unaryop(node, line)

        elif isinstance(node, ast.Compare):
            return self._eval_compare(node, line)

        elif isinstance(node, ast.BoolOp):
            return self._eval_boolop(node, line)

        elif isinstance(node, ast.List):
            return self._eval_list(node, line)

        elif isinstance(node, ast.Dict):
            return self._eval_dict(node, line)

        elif isinstance(node, ast.Call):
            return self._eval_call(node, line)

        elif isinstance(node, ast.IfExp):
            return self._eval_ifexp(node, line)

        elif isinstance(node, ast.Attribute):
            return self._eval_attribute(node, line)

        elif isinstance(node, ast.Tuple):
            elts = [self.eval_expr(e, line) for e in node.elts]
            return tuple(elts)

        else:
            # Fallback: compile and eval
            try:
                code = compile(ast.Expression(body=node), "<string>", "eval")
                return eval(code, {"__builtins__": {}}, self.variables)
            except Exception:
                return None

    def _eval_subscript(self, node: ast.Subscript, line: int) -> Any:
        container = self.eval_expr(node.value, line)
        container_src = ast.unparse(node.value)

        index = self.eval_expr(node.slice, line)
        index_src = ast.unparse(node.slice)

        # Show the subscript expression
        expr_str = f"{container_src}[{index_src}]"
        self._emit(
            EventType.SUBSCRIPT_EVAL,
            f"Evaluate `{container_src}[{index_src}]` → `{container_src}[{index}]`",
            expression=expr_str,
            line_number=line,
            metadata={"container": container_src, "index": index}
        )

        # Resolve the value
        result = container[index]
        self._emit(
            EventType.SUBSCRIPT_RESULT,
            f"`{container_src}[{index}]` = {self._display_value(result)}",
            expression=f"{container_src}[{index}]",
            result=result,
            line_number=line,
            metadata={"container": container_src, "index": index, "value": result}
        )
        return result

    def _eval_binop(self, node: ast.BinOp, line: int) -> Any:
        op_map = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
            ast.BitAnd: "&", ast.BitOr: "|", ast.BitXor: "^",
            ast.LShift: "<<", ast.RShift: ">>"
        }
        op_sym = op_map.get(type(node.op), "?")
        op_funcs = {
            ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
            ast.FloorDiv: lambda a, b: a // b, ast.Mod: lambda a, b: a % b,
            ast.Pow: lambda a, b: a ** b,
        }

        left_src = ast.unparse(node.left)
        right_src = ast.unparse(node.right)

        left_val = self.eval_expr(node.left, line)
        right_val = self.eval_expr(node.right, line)

        # Show fully-substituted expression
        self._emit(
            EventType.BINOP_EVAL,
            f"Evaluate `{self._display_value(left_val)} {op_sym} {self._display_value(right_val)}`",
            expression=f"{self._display_value(left_val)} {op_sym} {self._display_value(right_val)}",
            line_number=line,
            metadata={"left": left_val, "op": op_sym, "right": right_val}
        )

        op_fn = op_funcs.get(type(node.op))
        result = op_fn(left_val, right_val) if op_fn else None

        self._emit(
            EventType.BINOP_RESULT,
            f"`{self._display_value(left_val)} {op_sym} {self._display_value(right_val)}` = {self._display_value(result)}",
            expression=f"{left_src} {op_sym} {right_src}",
            result=result,
            line_number=line,
            metadata={"left": left_val, "op": op_sym, "right": right_val, "result": result}
        )
        return result

    def _eval_unaryop(self, node: ast.UnaryOp, line: int) -> Any:
        op_map = {ast.USub: "-", ast.UAdd: "+", ast.Not: "not ", ast.Invert: "~"}
        op_sym = op_map.get(type(node.op), "?")
        operand_val = self.eval_expr(node.operand, line)
        if isinstance(node.op, ast.USub):
            result = -operand_val
        elif isinstance(node.op, ast.Not):
            result = not operand_val
        else:
            result = operand_val
        self._emit(
            EventType.BINOP_RESULT,
            f"`{op_sym}{self._display_value(operand_val)}` = {self._display_value(result)}",
            expression=f"{op_sym}{ast.unparse(node.operand)}",
            result=result,
            line_number=line
        )
        return result

    def _eval_compare(self, node: ast.Compare, line: int) -> Any:
        op_map = {
            ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=",
            ast.Gt: ">", ast.GtE: ">=", ast.In: "in", ast.NotIn: "not in",
            ast.Is: "is", ast.IsNot: "is not"
        }
        left_val = self.eval_expr(node.left, line)
        result = True
        current = left_val

        for op, comparator in zip(node.ops, node.comparators):
            op_sym = op_map.get(type(op), "?")
            right_val = self.eval_expr(comparator, line)

            self._emit(
                EventType.COMPARISON_EVAL,
                f"Compare `{self._display_value(current)} {op_sym} {self._display_value(right_val)}`",
                expression=f"{self._display_value(current)} {op_sym} {self._display_value(right_val)}",
                line_number=line,
                metadata={"left": current, "op": op_sym, "right": right_val}
            )

            if isinstance(op, ast.Eq): cmp = current == right_val
            elif isinstance(op, ast.NotEq): cmp = current != right_val
            elif isinstance(op, ast.Lt): cmp = current < right_val
            elif isinstance(op, ast.LtE): cmp = current <= right_val
            elif isinstance(op, ast.Gt): cmp = current > right_val
            elif isinstance(op, ast.GtE): cmp = current >= right_val
            elif isinstance(op, ast.In): cmp = current in right_val
            elif isinstance(op, ast.NotIn): cmp = current not in right_val
            else: cmp = False

            self._emit(
                EventType.COMPARISON_RESULT,
                f"`{self._display_value(current)} {op_sym} {self._display_value(right_val)}` → {cmp}",
                expression=f"{self._display_value(current)} {op_sym} {self._display_value(right_val)}",
                result=cmp,
                line_number=line,
                metadata={"result": cmp}
            )

            result = result and cmp
            current = right_val
            if not result:
                break

        return result

    def _eval_boolop(self, node: ast.BoolOp, line: int) -> Any:
        op_sym = "and" if isinstance(node.op, ast.And) else "or"
        result = self.eval_expr(node.values[0], line)
        for value in node.values[1:]:
            if isinstance(node.op, ast.And) and not result:
                break
            if isinstance(node.op, ast.Or) and result:
                break
            right = self.eval_expr(value, line)
            self._emit(
                EventType.COMPARISON_EVAL,
                f"Evaluate `{self._display_value(result)} {op_sym} {self._display_value(right)}`",
                expression=f"{self._display_value(result)} {op_sym} {self._display_value(right)}",
                line_number=line
            )
            result = right
        return result

    def _eval_list(self, node: ast.List, line: int) -> list:
        elements = []
        for elt in node.elts:
            val = self.eval_expr(elt, line)
            elements.append(val)
        self._emit(
            EventType.ARRAY_INIT,
            f"Create list {elements}",
            expression=ast.unparse(node),
            result=elements,
            line_number=line,
            metadata={"elements": elements}
        )
        return elements

    def _eval_dict(self, node: ast.Dict, line: int) -> dict:
        result = {}
        for k, v in zip(node.keys, node.values):
            key = self.eval_expr(k, line) if k else None
            val = self.eval_expr(v, line)
            result[key] = val
        self._emit(
            EventType.DICT_INIT,
            f"Create dict {result}",
            expression=ast.unparse(node),
            result=result,
            line_number=line,
            metadata={"dict": result}
        )
        return result

    def _eval_call(self, node: ast.Call, line: int) -> Any:
        func_src = ast.unparse(node.func)
        args = [self.eval_expr(arg, line) for arg in node.args]

        self._emit(
            EventType.FUNCTION_CALL,
            f"Call `{func_src}({', '.join(self._display_value(a) for a in args)})`",
            expression=f"{func_src}({', '.join(self._display_value(a) for a in args)})",
            line_number=line,
            metadata={"func": func_src, "args": args}
        )

        # Built-in safe functions
        builtins = {
            "len": len, "range": range, "enumerate": enumerate,
            "int": int, "str": str, "float": float, "bool": bool,
            "list": list, "dict": dict, "set": set, "tuple": tuple,
            "min": min, "max": max, "abs": abs, "sum": sum,
            "sorted": sorted, "reversed": reversed,
            "print": self._safe_print,
            "append": None,  # handled via attribute
        }

        result = None
        try:
            if isinstance(node.func, ast.Name) and node.func.id in builtins:
                fn = builtins[node.func.id]
                result = fn(*args) if fn else None
            elif isinstance(node.func, ast.Attribute):
                obj = self.eval_expr(node.func.value, line)
                method = getattr(obj, node.func.attr, None)
                if method:
                    result = method(*args)
                    # Update variable if it's a mutable method
                    if isinstance(node.func.value, ast.Name):
                        var_name = node.func.value.id
                        self.variables[var_name] = obj
        except Exception as e:
            result = None

        self._emit(
            EventType.FUNCTION_RETURN,
            f"`{func_src}(...)` returned {self._display_value(result)}",
            expression=func_src,
            result=result,
            line_number=line,
            metadata={"func": func_src, "return_value": result}
        )
        return result

    def _eval_attribute(self, node: ast.Attribute, line: int) -> Any:
        obj = self.eval_expr(node.value, line)
        return getattr(obj, node.attr, None)

    def _eval_ifexp(self, node: ast.IfExp, line: int) -> Any:
        test = self.eval_expr(node.test, line)
        if test:
            return self.eval_expr(node.body, line)
        else:
            return self.eval_expr(node.orelse, line)

    def _safe_print(self, *args) -> None:
        line = " ".join(str(a) for a in args)
        self.output_lines.append(line)
        self._emit(
            EventType.PRINT_OUTPUT,
            f"Output: {line}",
            expression=f"print({line})",
            result=line,
            metadata={"output": line}
        )
        return None

    # ─── Statement Executors ─────────────────────────────────────────────────

    def exec_stmt(self, node: ast.stmt):
        line = getattr(node, "lineno", None)

        if isinstance(node, ast.Assign):
            self._exec_assign(node, line)
        elif isinstance(node, ast.AugAssign):
            self._exec_augassign(node, line)
        elif isinstance(node, ast.AnnAssign):
            self._exec_annassign(node, line)
        elif isinstance(node, ast.Expr):
            self.eval_expr(node.value, line)
        elif isinstance(node, ast.If):
            self._exec_if(node, line)
        elif isinstance(node, ast.For):
            self._exec_for(node, line)
        elif isinstance(node, ast.While):
            self._exec_while(node, line)
        elif isinstance(node, ast.Return):
            self._exec_return(node, line)
        elif isinstance(node, ast.FunctionDef):
            self._exec_funcdef(node, line)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            pass  # Skip imports in visualization
        elif isinstance(node, ast.Pass):
            pass
        elif isinstance(node, ast.Break):
            raise _BreakSignal()
        elif isinstance(node, ast.Continue):
            raise _ContinueSignal()

    def _exec_assign(self, node: ast.Assign, line: int):
        # Evaluate the right-hand side first
        rhs_src = ast.unparse(node.value)
        self._emit(
            EventType.ASSIGNMENT_START,
            f"Start evaluating: `{ast.unparse(node.targets[0])} = {rhs_src}`",
            expression=f"{ast.unparse(node.targets[0])} = {rhs_src}",
            line_number=line,
            metadata={"lhs": ast.unparse(node.targets[0]), "rhs": rhs_src}
        )

        value = self.eval_expr(node.value, line)

        # Assign to each target
        for target in node.targets:
            self._assign_target(target, value, line)

    def _assign_target(self, target: ast.expr, value: Any, line: int):
        if isinstance(target, ast.Name):
            name = target.id
            old_val = self.variables.get(name)
            self.variables[name] = value
            self._emit(
                EventType.VARIABLE_ASSIGN,
                f"Assign `{name}` = {self._display_value(value)}",
                expression=f"{name} = {self._display_value(value)}",
                result=value,
                highlight_vars=[name],
                line_number=line,
                metadata={"var_name": name, "value": value, "old_value": old_val}
            )
        elif isinstance(target, ast.Subscript):
            container = self.eval_expr(target.value, line)
            idx = self.eval_expr(target.slice, line)
            container[idx] = value
            container_name = ast.unparse(target.value)
            if isinstance(target.value, ast.Name):
                self.variables[target.value.id] = container
            self._emit(
                EventType.SUBSCRIPT_ASSIGN,
                f"Set `{container_name}[{idx}]` = {self._display_value(value)}",
                expression=f"{container_name}[{idx}] = {self._display_value(value)}",
                result=value,
                line_number=line,
                metadata={"container": container_name, "index": idx, "value": value}
            )
        elif isinstance(target, ast.Tuple):
            for i, elt in enumerate(target.elts):
                self._assign_target(elt, value[i], line)

    def _exec_augassign(self, node: ast.AugAssign, line: int):
        op_map = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.FloorDiv: "//", ast.Mod: "%"
        }
        op_sym = op_map.get(type(node.op), "?")
        target_src = ast.unparse(node.target)

        self._emit(
            EventType.ASSIGNMENT_START,
            f"Augmented assign: `{target_src} {op_sym}= {ast.unparse(node.value)}`",
            expression=f"{target_src} {op_sym}= {ast.unparse(node.value)}",
            line_number=line
        )

        old_val = self.eval_expr(node.target, line)
        new_val_rhs = self.eval_expr(node.value, line)

        # Create synthetic BinOp
        fake_binop = ast.BinOp(left=ast.Constant(value=old_val),
                               op=node.op,
                               right=ast.Constant(value=new_val_rhs))
        result = self._eval_binop(fake_binop, line)

        self._assign_target(node.target, result, line)

    def _exec_annassign(self, node: ast.AnnAssign, line: int):
        if node.value:
            self._exec_assign(
                ast.Assign(targets=[node.target], value=node.value, lineno=line),
                line
            )

    def _exec_if(self, node: ast.If, line: int):
        condition_src = ast.unparse(node.test)
        self._emit(
            EventType.IF_TEST,
            f"Test condition: `{condition_src}`",
            expression=condition_src,
            line_number=line,
            metadata={"condition": condition_src}
        )

        condition_val = self.eval_expr(node.test, line)

        self._emit(
            EventType.IF_BRANCH,
            f"Condition is {condition_val} → entering {'if' if condition_val else 'else'} branch",
            expression=condition_src,
            result=condition_val,
            line_number=line,
            metadata={"branch": "if" if condition_val else "else", "result": condition_val}
        )

        if condition_val:
            for stmt in node.body:
                self.exec_stmt(stmt)
        else:
            for stmt in node.orelse:
                self.exec_stmt(stmt)

    def _exec_for(self, node: ast.For, line: int):
        iter_src = ast.unparse(node.iter)
        target_src = ast.unparse(node.target)

        iterable = self.eval_expr(node.iter, line)
        
        # Convert range to list for display and metadata
        iterable_list = list(iterable) if isinstance(iterable, range) else iterable
        range_display = f"range({iterable.start}, {iterable.stop})" if isinstance(iterable, range) else str(iterable_list)

        self._emit(
            EventType.LOOP_START,
            f"Start `for {target_src} in {iter_src}` — iterating over {range_display}",
            expression=f"for {target_src} in {iter_src}",
            line_number=line,
            metadata={"target": target_src, "iterable": iter_src, "values": iterable_list}
        )

        for item in iterable:
            self._assign_target(node.target, item, line)

            self._emit(
                EventType.LOOP_ITER,
                f"Loop iteration: `{target_src}` = {self._display_value(item)}",
                expression=f"{target_src} = {self._display_value(item)}",
                result=item,
                highlight_vars=[target_src] if isinstance(node.target, ast.Name) else [],
                line_number=line,
                metadata={"target": target_src, "value": item}
            )

            try:
                for stmt in node.body:
                    self.exec_stmt(stmt)
            except _BreakSignal:
                self._emit(
                    EventType.LOOP_END,
                    f"Break — exit loop",
                    line_number=line
                )
                break
            except _ContinueSignal:
                continue

        self._emit(
            EventType.LOOP_END,
            f"Loop `for {target_src} in {iter_src}` complete",
            expression=f"for {target_src} in {iter_src}",
            line_number=line
        )

    def _exec_while(self, node: ast.While, line: int):
        condition_src = ast.unparse(node.test)
        iteration = 0
        max_iter = 1000  # Safety limit

        self._emit(
            EventType.LOOP_START,
            f"Start `while {condition_src}`",
            expression=f"while {condition_src}",
            line_number=line
        )

        while iteration < max_iter:
            self._emit(
                EventType.IF_TEST,
                f"Check while condition: `{condition_src}`",
                expression=condition_src,
                line_number=line
            )
            cond = self.eval_expr(node.test, line)
            if not cond:
                self._emit(
                    EventType.IF_BRANCH,
                    f"While condition is False — exit loop",
                    result=False,
                    line_number=line
                )
                break

            try:
                for stmt in node.body:
                    self.exec_stmt(stmt)
            except _BreakSignal:
                break
            except _ContinueSignal:
                pass

            iteration += 1

        self._emit(
            EventType.LOOP_END,
            f"While loop complete",
            expression=f"while {condition_src}",
            line_number=line
        )

    def _exec_return(self, node: ast.Return, line: int):
        if node.value:
            val = self.eval_expr(node.value, line)
            self._emit(
                EventType.FUNCTION_RETURN,
                f"Return {self._display_value(val)}",
                result=val,
                line_number=line
            )
            raise _ReturnSignal(val)
        raise _ReturnSignal(None)

    def _exec_funcdef(self, node: ast.FunctionDef, line: int):
        # Store function for future calls - simplified
        self._emit(
            EventType.FUNCTION_CALL,
            f"Define function `{node.name}`",
            expression=f"def {node.name}(...)",
            line_number=line,
            metadata={"func_name": node.name}
        )

    # ─── Main Entry Point ─────────────────────────────────────────────────────

    def execute(self, code: str, initial_vars: dict[str, Any] = None) -> ExecutionResult:
        """
        Parse and execute code, returning all events.
        """
        self.events = []
        self.variables = copy.deepcopy(initial_vars or {})
        self.step_counter = 0
        self.output_lines = []
        self.call_stack = ["<module>"]

        # Emit initial variable setup
        for name, val in self.variables.items():
            self._emit(
                EventType.VARIABLE_ASSIGN,
                f"Initialize `{name}` = {self._display_value(val)}",
                expression=f"{name} = {self._display_value(val)}",
                result=val,
                highlight_vars=[name],
                metadata={"var_name": name, "value": val, "is_initial": True}
            )

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ExecutionResult(
                events=[],
                error=f"SyntaxError: {e}",
                success=False,
                total_steps=0
            )

        error = None
        try:
            for node in tree.body:
                self.exec_stmt(node)
        except _ReturnSignal:
            pass
        except StepError as e:
            error = str(e)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        return ExecutionResult(
            events=self.events,
            error=error,
            success=error is None,
            total_steps=self.step_counter
        )


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value
