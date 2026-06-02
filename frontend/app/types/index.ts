// DSA Visualizer - TypeScript Types

export type EventType =
  | "variable_assign"
  | "variable_read"
  | "assignment_start"
  | "subscript_assign"
  | "binop_eval"
  | "binop_result"
  | "subscript_eval"
  | "subscript_result"
  | "comparison_eval"
  | "comparison_result"
  | "if_test"
  | "if_branch"
  | "loop_start"
  | "loop_iter"
  | "loop_end"
  | "function_call"
  | "function_return"
  | "array_init"
  | "dict_init"
  | "print_output";

export interface VariableState {
  name: string;
  value: unknown;
  type: string;
  display: string;
}

export interface MemoryState {
  variables: Record<string, VariableState>;
  call_stack: string[];
  output: string[];
}

export interface ExecutionEvent {
  step: number;
  event_type: EventType;
  description: string;
  expression?: string;
  result?: unknown;
  result_display?: string;
  memory: MemoryState;
  highlight_vars: string[];
  line_number?: number;
  metadata: Record<string, unknown>;
  color?: string;
  icon?: string;
}

export interface ExecutionResult {
  events: ExecutionEvent[];
  error?: string;
  success: boolean;
  total_steps: number;
}

export interface DSAProblem {
  id: string;
  title: string;
  description: string;
  code: string;
  initial_vars: Record<string, unknown>;
  tags: string[];
  difficulty: "Easy" | "Medium" | "Hard";
}

export interface ProblemListItem {
  id: string;
  title: string;
  description: string;
  difficulty: "Easy" | "Medium" | "Hard";
  tags: string[];
}

export type PlaybackState = "playing" | "paused" | "idle" | "done";
