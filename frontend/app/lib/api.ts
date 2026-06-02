// DSA Visualizer - API Client

import type {
  ExecutionResult,
  DSAProblem,
  ProblemListItem,
} from "@/app/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchJSON<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function executeCode(
  code: string,
  initialVars: Record<string, unknown> = {}
): Promise<ExecutionResult> {
  return fetchJSON<ExecutionResult>("/execute", {
    method: "POST",
    body: JSON.stringify({ code, initial_vars: initialVars }),
  });
}

export async function getProblems(): Promise<ProblemListItem[]> {
  const data = await fetchJSON<{ problems: ProblemListItem[] }>("/problems");
  return data.problems;
}

export async function getProblem(id: string): Promise<DSAProblem> {
  return fetchJSON<DSAProblem>(`/problems/${id}`);
}

export async function executeProblem(id: string): Promise<ExecutionResult> {
  return fetchJSON<ExecutionResult>(`/problems/${id}/execute`, {
    method: "POST",
  });
}
