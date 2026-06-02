"use client";

import { useState, useCallback } from "react";
import { executeCode, executeProblem } from "@/app/lib/api";
import type { ExecutionEvent } from "@/app/types";

export function useExecution() {
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (code: string, vars: Record<string, unknown> = {}) => {
      setLoading(true);
      setError(null);
      try {
        const result = await executeCode(code, vars);
        if (!result.success && result.error) {
          setError(result.error);
          setEvents([]);
        } else {
          setEvents(result.events);
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Unknown error");
        setEvents([]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const runProblem = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await executeProblem(id);
      if (!result.success && result.error) {
        setError(result.error);
        setEvents([]);
      } else {
        setEvents(result.events);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return { events, loading, error, run, runProblem };
}
