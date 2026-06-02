"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useExecution } from "@/app/hooks/useExecution";
import { usePlayback } from "@/app/hooks/usePlayback";
import { getProblems, getProblem } from "@/app/lib/api";
import type { ProblemListItem, ExecutionEvent, VariableState } from "@/app/types";

// ─── Utility ─────────────────────────────────────────────────────────────────

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "null";
  if (typeof v === "string") return `"${v}"`;
  if (Array.isArray(v)) return `[${v.map(formatValue).join(", ")}]`;
  if (typeof v === "object") {
    const entries = Object.entries(v as Record<string, unknown>)
      .map(([k, val]) => `${formatValue(k)}: ${formatValue(val)}`)
      .join(", ");
    return `{${entries}}`;
  }
  return String(v);
}

const DIFFICULTY_COLORS: Record<string, string> = {
  Easy: "text-emerald-400 border-emerald-400/30 bg-emerald-400/10",
  Medium: "text-amber-400 border-amber-400/30 bg-amber-400/10",
  Hard: "text-red-400 border-red-400/30 bg-red-400/10",
};

const EVENT_CATEGORY: Record<string, string> = {
  variable_assign: "assign",
  variable_read: "read",
  assignment_start: "assign",
  subscript_assign: "assign",
  binop_eval: "math",
  binop_result: "math",
  subscript_eval: "access",
  subscript_result: "access",
  comparison_eval: "compare",
  comparison_result: "compare",
  if_test: "branch",
  if_branch: "branch",
  loop_start: "loop",
  loop_iter: "loop",
  loop_end: "loop",
  function_call: "function",
  function_return: "function",
  array_init: "data",
  dict_init: "data",
  print_output: "output",
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function CodePanel({
  code,
  onCodeChange,
  currentLine,
  currentEvent,
  readOnly = false,
}: {
  code: string;
  onCodeChange: (c: string) => void;
  currentLine?: number;
  currentEvent?: ExecutionEvent | null;
  readOnly?: boolean;
}) {
  const lines = code.split("\n");
  const highlightedVars = new Set(currentEvent?.highlight_vars || []);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5">
        <span className="text-[10px] font-mono uppercase tracking-widest text-slate-500">
          Code Editor
        </span>
        <div className="ml-auto flex gap-1.5">
          {["#ff5f57", "#ffbd2e", "#28c840"].map((c, i) => (
            <div key={i} className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="flex font-mono text-sm leading-6 min-h-full">
          {/* Line numbers */}
          <div className="select-none px-3 pt-3 text-right text-slate-600 bg-black/20 border-r border-white/5 min-w-[2.5rem]">
            {lines.map((_, i) => (
              <div
                key={i}
                className={`transition-colors h-6 flex items-center justify-end ${
                  currentLine === i + 1 ? "text-amber-400 font-bold bg-amber-400/10" : ""
                }`}
              >
                {i + 1}
              </div>
            ))}
          </div>

          {/* Code content */}
          <div className="relative flex-1 overflow-x-auto">
            {/* Highlight current line */}
            {currentLine && (
              <motion.div
                layoutId="line-highlight"
                className="absolute left-0 right-0 bg-amber-400/10 border-l-4 border-amber-400 pointer-events-none"
                style={{
                  top: `${(currentLine - 1) * 1.5}rem`,
                  height: "1.5rem",
                  marginTop: "0.75rem",
                }}
                transition={{ type: "spring", stiffness: 400, damping: 40 }}
              />
            )}

            {/* Code with inline annotations */}
            <div className="relative p-3">
              {lines.map((line, lineIdx) => {
                const isCurrentLine = currentLine === lineIdx + 1;
                const lineVars = new Map<number, { var: string; value: string; color: string }>();

                // Find variables in this line that are highlighted
                if (isCurrentLine && currentEvent) {
                  highlightedVars.forEach((varName) => {
                    const regex = new RegExp(`\\b${varName}\\b`, "g");
                    let match;
                    while ((match = regex.exec(line)) !== null) {
                      lineVars.set(match.index, {
                        var: varName,
                        value: currentEvent.result_display || "",
                        color: currentEvent.color || "#fbbf24",
                      });
                    }
                  });
                }

                return (
                  <div key={lineIdx} className="relative group h-6 flex items-center">
                    <textarea
                      className="flex-1 bg-transparent text-amber-100 outline-none caret-amber-400 resize-none overflow-hidden"
                      value={line}
                      onChange={(e) => {
                        const newLines = [...lines];
                        newLines[lineIdx] = e.target.value;
                        onCodeChange(newLines.join("\n"));
                      }}
                      readOnly={readOnly}
                      spellCheck={false}
                      style={{ minHeight: "1.5rem", lineHeight: "1.5rem" }}
                    />

                    {/* Inline annotations - appear right next to the line */}
                    {isCurrentLine && currentEvent && (
                      <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        className="ml-4 flex items-center gap-2 whitespace-nowrap shrink-0"
                      >
                        <span className="text-lg">{currentEvent.icon}</span>
                        <div className="flex items-center gap-1 px-2 py-1 rounded-lg border border-amber-400/50 bg-amber-400/15">
                          <span className="text-xs font-bold text-amber-100">
                            {currentEvent.event_type === "loop_iter"
                              ? `Loop: ${currentEvent.metadata?.value}`
                              : currentEvent.event_type === "variable_assign"
                              ? `${highlightedVars.size > 0 ? Array.from(highlightedVars)[0] : "var"}`
                              : ""}
                          </span>
                          <span className="text-amber-300 font-mono text-xs font-bold">
                            = {currentEvent.result_display}
                          </span>
                        </div>
                      </motion.div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function EventCard({
  event,
  isActive,
  onClick,
}: {
  event: ExecutionEvent;
  isActive: boolean;
  onClick: () => void;
}) {
  const category = EVENT_CATEGORY[event.event_type] || "other";
  const categoryColors: Record<string, string> = {
    assign: "border-cyan-500/40 bg-cyan-500/5",
    read: "border-violet-500/40 bg-violet-500/5",
    math: "border-orange-500/40 bg-orange-500/5",
    access: "border-blue-500/40 bg-blue-500/5",
    compare: "border-pink-500/40 bg-pink-500/5",
    branch: "border-yellow-500/40 bg-yellow-500/5",
    loop: "border-emerald-500/40 bg-emerald-500/5",
    function: "border-purple-500/40 bg-purple-500/5",
    data: "border-sky-500/40 bg-sky-500/5",
    output: "border-slate-500/40 bg-slate-500/5",
  };

  return (
    <motion.div
      layout
      onClick={onClick}
      className={`
        cursor-pointer rounded-lg border p-3 transition-all
        ${isActive
          ? "border-amber-400/60 bg-amber-400/10 shadow-[0_0_20px_rgba(251,191,36,0.15)]"
          : `${categoryColors[category] || "border-white/5 bg-white/2"} hover:border-white/20`
        }
      `}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <div className="flex items-start gap-2">
        <span className="text-base leading-none mt-0.5 shrink-0">
          {event.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span
              className="text-[9px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded"
              style={{
                color: event.color,
                background: `${event.color}18`,
                border: `1px solid ${event.color}30`,
              }}
            >
              {category}
            </span>
            <span className="text-[10px] text-slate-600 font-mono">
              #{event.step}
            </span>
          </div>
          <p className="text-xs text-amber-100 leading-snug truncate">
            {event.description}
          </p>
          {event.expression && (
            <code className="text-[10px] text-cyan-300/70 font-mono mt-0.5 block truncate">
              {event.expression}
            </code>
          )}
        </div>
        {event.result_display !== undefined && event.result_display !== null && (
          <span
            className="shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded font-bold"
            style={{ color: event.color, background: `${event.color}15` }}
          >
            {event.result_display}
          </span>
        )}
      </div>
    </motion.div>
  );
}

function VariablesPanel({ event }: { event: ExecutionEvent | null }) {
  if (!event) return (
    <div className="flex items-center justify-center h-full text-slate-600 text-sm">
      Run code to see variables
    </div>
  );

  const vars = Object.values(event.memory.variables);
  const highlighted = new Set(event.highlight_vars);

  return (
    <div className="p-3 space-y-2">
      <AnimatePresence mode="popLayout">
        {vars.map((v) => (
          <motion.div
            key={v.name}
            layout
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`
              rounded-lg border p-2.5 transition-all
              ${highlighted.has(v.name)
                ? "border-amber-400/50 bg-amber-400/8 shadow-[0_0_15px_rgba(251,191,36,0.1)]"
                : "border-white/5 bg-white/2"
              }
            `}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5 mb-1">
                  {highlighted.has(v.name) && (
                    <motion.div
                      className="w-2 h-2 rounded-full bg-amber-400"
                      animate={{ scale: [1, 1.5, 1] }}
                      transition={{ repeat: 1, duration: 0.4 }}
                    />
                  )}
                  <span className="text-xs font-mono font-bold text-amber-100">
                    {v.name}
                  </span>
                  <span className="text-[9px] text-amber-400/60 border border-amber-400/30 px-1 rounded">
                    {v.type}
                  </span>
                </div>
                <VariableValueDisplay value={v.value} name={v.name} />
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Output */}
      {event.memory.output.length > 0 && (
        <div className="border border-amber-400/30 rounded-lg p-2.5 bg-amber-400/8">
          <div className="text-[9px] uppercase tracking-widest text-amber-400/70 mb-2 font-bold">
            📤 Output
          </div>
          {event.memory.output.map((line, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="font-mono text-xs text-emerald-300"
            >
              &gt; {line}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function VariableValueDisplay({ value, name }: { value: unknown; name: string }) {
  if (Array.isArray(value)) {
    return (
      <div className="flex flex-wrap gap-1 mt-1">
        {value.map((item, i) => (
          <motion.span
            key={`${name}-${i}`}
            layout
            className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-amber-100 border border-amber-400/30"
          >
            <span className="text-amber-400/60 text-[8px]">[{i}]</span>{" "}
            {formatValue(item)}
          </motion.span>
        ))}
      </div>
    );
  }

  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    return (
      <div className="space-y-0.5 mt-1">
        {entries.map(([k, v]) => (
          <div key={k} className="flex gap-1 text-[10px] font-mono">
            <span className="text-violet-300">{formatValue(k)}</span>
            <span className="text-amber-400/50">:</span>
            <span className="text-amber-100">{formatValue(v)}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <span className="text-[10px] font-mono text-amber-400/50">{"{}"}</span>
        )}
      </div>
    );
  }

  return (
    <div className="font-mono text-sm font-bold text-amber-300 mt-0.5">
      {formatValue(value)}
    </div>
  );
}

function MemoryPanel({ event }: { event: ExecutionEvent | null }) {
  if (!event) {
    return (
      <div className="flex items-center justify-center h-full text-slate-600 text-sm">
        Memory state will appear here
      </div>
    );
  }

  return (
    <div className="p-3 space-y-3">
      {/* Current event detail */}
      <div className="rounded-lg border border-amber-400/20 bg-amber-400/5 p-3">
        <div className="text-[9px] uppercase tracking-widest text-amber-400/70 mb-2 font-bold">
          Current Event
        </div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">{event.icon}</span>
          <div>
            <div
              className="text-[9px] font-bold uppercase tracking-widest"
              style={{ color: event.color }}
            >
              {event.event_type.replace(/_/g, " ")}
            </div>
            <div className="text-xs text-amber-100">{event.description}</div>
          </div>
        </div>
        {event.expression && (
          <div className="bg-black/30 rounded p-2 font-mono text-xs text-amber-300 break-all">
            {event.expression}
          </div>
        )}
        {event.result_display !== undefined && event.result_display !== null && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-[10px] text-amber-400/60">Result:</span>
            <span
              className="font-mono text-sm font-bold"
              style={{ color: event.color }}
            >
              {event.result_display}
            </span>
          </div>
        )}
      </div>

      {/* Call stack */}
      <div className="rounded-lg border border-amber-400/20 bg-amber-400/5 p-2.5">
        <div className="text-[9px] uppercase tracking-widest text-amber-400/70 mb-2 font-bold">
          Call Stack
        </div>
        {event.memory.call_stack.map((frame, i) => (
          <div key={i} className="flex items-center gap-2 py-1">
            <div className="w-1 h-1 rounded-full bg-amber-400 shrink-0" />
            <span className="font-mono text-xs text-amber-200">{frame}</span>
          </div>
        ))}
      </div>

      {/* Line number */}
      {event.line_number && (
        <div className="rounded-lg border border-amber-400/20 bg-amber-400/5 p-2.5">
          <div className="text-[9px] uppercase tracking-widest text-amber-400/70 mb-1 font-bold">
            Source Location
          </div>
          <span className="font-mono text-xs text-amber-300">
            Line {event.line_number}
          </span>
        </div>
      )}
    </div>
  );
}

function PlaybackControls({
  isPlaying,
  canStepBack,
  canStepForward,
  currentStep,
  totalSteps,
  onPlay,
  onPause,
  onStepBack,
  onStepForward,
  onReset,
  onJumpTo,
  speed,
  onSpeedChange,
}: {
  isPlaying: boolean;
  canStepBack: boolean;
  canStepForward: boolean;
  currentStep: number;
  totalSteps: number;
  onPlay: () => void;
  onPause: () => void;
  onStepBack: () => void;
  onStepForward: () => void;
  onReset: () => void;
  onJumpTo: (n: number) => void;
  speed: number;
  onSpeedChange: (s: number) => void;
}) {
  const progress = totalSteps > 0 ? (currentStep / (totalSteps - 1)) * 100 : 0;

  const speedLabel = (val: number) => {
    if (val > 1000) return `${(val / 1000).toFixed(2)}× (slow)`;
    if (val < 1000) return `-${Math.round((1000 / val) * 10) / 10}×`;
    return "1×";
  };

  return (
    <div className="border-t border-amber-400/20 bg-black/20 px-4 py-3">
      {/* Progress bar */}
      <div
        className="relative h-1.5 bg-amber-400/20 rounded-full mb-3 cursor-pointer border border-amber-400/30"
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          const ratio = (e.clientX - rect.left) / rect.width;
          onJumpTo(Math.round(ratio * (totalSteps - 1)));
        }}
      >
        <motion.div
          className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-amber-400 to-orange-400 rounded-full"
          style={{ width: `${progress}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 40 }}
        />
        {/* Thumb */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.8)] -ml-2"
          style={{ left: `${progress}%` }}
          transition={{ type: "spring", stiffness: 300, damping: 40 }}
        />
      </div>

      <div className="flex items-center gap-3">
        {/* Step counter */}
        <span className="text-[10px] font-mono text-amber-400/70 tabular-nums w-16 shrink-0 font-bold">
          {currentStep + 1} / {totalSteps}
        </span>

        {/* Controls */}
        <div className="flex items-center gap-1 flex-1 justify-center">
          <CtrlBtn onClick={onReset} title="Reset" disabled={currentStep === 0 && !isPlaying}>
            ⏮
          </CtrlBtn>
          <CtrlBtn onClick={onStepBack} disabled={!canStepBack} title="Previous step">
            ⏪
          </CtrlBtn>

          <motion.button
            onClick={isPlaying ? onPause : onPlay}
            disabled={totalSteps === 0}
            className={`
              w-10 h-10 rounded-xl font-bold text-lg transition-all
              disabled:opacity-30 disabled:cursor-not-allowed
              ${isPlaying
                ? "bg-rose-500/20 border border-rose-500/40 text-rose-300 hover:bg-rose-500/30"
                : "bg-amber-500/20 border border-amber-500/40 text-amber-300 hover:bg-amber-500/30"
              }
            `}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isPlaying ? "⏸" : "▶"}
          </motion.button>

          <CtrlBtn onClick={onStepForward} disabled={!canStepForward} title="Next step">
            ⏩
          </CtrlBtn>
        </div>

        {/* Speed control */}
        <div className="flex items-center gap-1.5 w-48 shrink-0 justify-end">
          <span className="text-[10px] text-amber-400/70 font-bold">Speed</span>
          <select
            value={speed}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
            className="bg-amber-500/10 border border-amber-400/40 text-amber-300 text-[10px] rounded px-2 py-1 outline-none hover:bg-amber-500/20 cursor-pointer font-bold"
          >
            <option value={6000}>-10×</option>
            <option value={5000}>-5×</option>
            <option value={4000}>-2×</option>
            <option value={3000}>-1×</option>
            <option value={2000}>0.5×</option>
            <option value={1000}>1×</option>
            <option value={500}>2×</option>
            <option value={250}>4×</option>
          </select>
        </div>
      </div>
    </div>
  );
}

function CtrlBtn({
  children,
  onClick,
  disabled,
  title,
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  title?: string;
}) {
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-400/40 text-amber-400
                 hover:bg-amber-500/20 hover:text-amber-300 transition-all
                 disabled:opacity-30 disabled:cursor-not-allowed text-sm font-bold"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function DSAVisualizerPage() {
  const [code, setCode] = useState(`nums = [2, 7, 11, 15]
target = 9
seen = {}

for i in range(len(nums)):
    need = target - nums[i]
    if need in seen:
        result = [seen[need], i]
    else:
        seen[nums[i]] = i`);

  const [problems, setProblems] = useState<ProblemListItem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<string | null>(null);
  const [speed, setSpeed] = useState(1000);
  const [activeTab, setActiveTab] = useState<"timeline" | "variables" | "memory">("timeline");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const timelineRef = useRef<HTMLDivElement>(null);

  const { events, loading, error, run, runProblem } = useExecution();
  const {
    currentStep,
    currentEvent,
    totalSteps,
    isPlaying,
    play,
    pause,
    stepForward,
    stepBack,
    jumpTo,
    reset,
    canStepBack,
    canStepForward,
  } = usePlayback({ events, intervalMs: speed });

  // Auto-scroll timeline
  useEffect(() => {
    if (timelineRef.current) {
      const el = timelineRef.current.children[currentStep] as HTMLElement;
      el?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }, [currentStep]);

  // Load problems on mount
  useEffect(() => {
    getProblems().then(setProblems).catch(console.error);
  }, []);

  const handleRun = async () => {
    await run(code);
  };

  const handleSelectProblem = async (id: string) => {
    setSelectedProblem(id);
    try {
      const p = await getProblem(id);
      setCode(p.code);
      await runProblem(id);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f0a1a] text-amber-100 flex flex-col" style={{
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      background: "radial-gradient(ellipse at 20% 0%, #1a0f2e 0%, #0f0a1a 60%)",
    }}>
      {/* ── Header ── */}
      <header className="border-b border-amber-400/20 bg-black/40 backdrop-blur-sm px-4 py-3 flex items-center gap-4 shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-sm font-black text-black">
            ⚡
          </div>
          <div>
            <h1 className="text-sm font-bold text-amber-300 tracking-wide">DSA Visualizer</h1>
            <p className="text-[9px] text-amber-400/60 uppercase tracking-widest">
              Step-by-step code execution
            </p>
          </div>
        </div>

        <div className="flex-1" />

        <button
          onClick={handleRun}
          disabled={loading}
          className="
            flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-bold
            bg-gradient-to-r from-amber-500/20 to-orange-500/20
            border border-amber-400/40
            text-amber-300 hover:text-amber-200
            hover:from-amber-500/30 hover:to-orange-500/30
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all
          "
        >
          {loading ? (
            <>
              <span className="inline-block w-3 h-3 border-2 border-amber-400/30 border-t-amber-400 rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            <>▶ Run & Visualize</>
          )}
        </button>

        <button
          onClick={() => setSidebarOpen((x) => !x)}
          className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-400/40 text-amber-400 hover:text-amber-300 text-sm flex items-center justify-center transition-all"
        >
          ☰
        </button>
      </header>

      <div className="flex flex-1 min-h-0">
        {/* ── Left Sidebar: Problem List ── */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 220, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 40 }}
              className="border-r border-amber-400/20 bg-black/20 flex flex-col overflow-hidden shrink-0"
            >
              <div className="px-3 py-2.5 border-b border-amber-400/20">
                <span className="text-[9px] uppercase tracking-widest text-amber-400/70 font-bold">
                  Problems
                </span>
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {problems.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => handleSelectProblem(p.id)}
                    className={`
                      w-full text-left rounded-lg p-2.5 transition-all border
                      ${selectedProblem === p.id
                        ? "border-amber-400/40 bg-amber-400/10 text-amber-100"
                        : "border-transparent hover:border-amber-400/20 hover:bg-amber-500/5 text-amber-400/70 hover:text-amber-300"
                      }
                    `}
                  >
                    <div className="text-[11px] font-bold truncate mb-1">
                      {p.title}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                          p.difficulty === "Easy"
                            ? "text-emerald-400 border-emerald-400/30 bg-emerald-400/10"
                            : p.difficulty === "Medium"
                            ? "text-amber-400 border-amber-400/30 bg-amber-400/10"
                            : "text-red-400 border-red-400/30 bg-red-400/10"
                        }`}
                      >
                        {p.difficulty}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* ── Main Content ── */}
        <div className="flex-1 flex min-w-0 min-h-0">
          {/* Code panel (left 40%) */}
          <div
            className="border-r border-amber-400/20 flex flex-col"
            style={{ width: "40%" }}
          >
            <CodePanel
              code={code}
              onCodeChange={setCode}
              currentLine={currentEvent?.line_number}
              currentEvent={currentEvent}
            />

            {/* Error */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="border-t border-red-500/20 bg-red-500/5 px-4 py-2"
                >
                  <p className="text-xs text-red-400 font-mono">{error}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right panel (60%) */}
          <div className="flex-1 flex flex-col min-w-0 min-h-0">
            {/* Tabs */}
            <div className="flex border-b border-amber-400/20 bg-black/20 shrink-0">
              {(["timeline", "variables", "memory"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`
                    px-4 py-2.5 text-[10px] uppercase tracking-widest font-bold transition-all relative
                    ${activeTab === tab ? "text-amber-400" : "text-amber-400/50 hover:text-amber-400"}
                  `}
                >
                  {tab === "timeline" ? "⏱ Timeline" : tab === "variables" ? "📦 Variables" : "🧠 Memory"}
                  {activeTab === tab && (
                    <motion.div
                      layoutId="tab-indicator"
                      className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-amber-400 to-transparent"
                    />
                  )}
                </button>
              ))}

              <div className="ml-auto px-3 flex items-center">
                {totalSteps > 0 && (
                  <span className="text-[9px] font-mono text-amber-400/70 font-bold">
                    {totalSteps} steps
                  </span>
                )}
              </div>
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-y-auto">
              {activeTab === "timeline" && (
                <div className="p-3 space-y-1.5" ref={timelineRef}>
                  {events.length === 0 && !loading && (
                    <div className="flex flex-col items-center justify-center py-16 text-center">
                      <div className="text-4xl mb-3">⚡</div>
                      <p className="text-amber-400/70 text-sm">
                        Press <span className="text-amber-300 font-bold">Run & Visualize</span> to start
                      </p>
                      <p className="text-amber-400/50 text-xs mt-1">
                        Or select a problem from the sidebar
                      </p>
                    </div>
                  )}

                  {loading && (
                    <div className="flex items-center justify-center py-16 gap-3 text-amber-400/70 text-sm">
                      <span className="inline-block w-4 h-4 border-2 border-amber-400/30 border-t-amber-400 rounded-full animate-spin" />
                      Analyzing code…
                    </div>
                  )}

                  {events.map((event, idx) => (
                    <EventCard
                      key={event.step}
                      event={event}
                      isActive={idx === currentStep}
                      onClick={() => jumpTo(idx)}
                    />
                  ))}
                </div>
              )}

              {activeTab === "variables" && (
                <VariablesPanel event={currentEvent} />
              )}

              {activeTab === "memory" && (
                <MemoryPanel event={currentEvent} />
              )}
            </div>

            {/* Playback controls */}
            {totalSteps > 0 && (
              <PlaybackControls
                isPlaying={isPlaying}
                canStepBack={canStepBack}
                canStepForward={canStepForward}
                currentStep={currentStep}
                totalSteps={totalSteps}
                onPlay={play}
                onPause={pause}
                onStepBack={stepBack}
                onStepForward={stepForward}
                onReset={reset}
                onJumpTo={jumpTo}
                speed={speed}
                onSpeedChange={setSpeed}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
