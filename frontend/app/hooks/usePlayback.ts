"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type { ExecutionEvent, PlaybackState } from "@/app/types";

interface UsePlaybackOptions {
  events: ExecutionEvent[];
  intervalMs?: number;
}

export function usePlayback({ events, intervalMs = 800 }: UsePlaybackOptions) {
  const [currentStep, setCurrentStep] = useState(0);
  const [playbackState, setPlaybackState] = useState<PlaybackState>("idle");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const totalSteps = events.length;
  const currentEvent = events[currentStep] ?? null;

  const stopInterval = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const pause = useCallback(() => {
    stopInterval();
    setPlaybackState("paused");
  }, [stopInterval]);

  const play = useCallback(() => {
    if (currentStep >= totalSteps - 1) {
      setCurrentStep(0);
    }
    setPlaybackState("playing");
    intervalRef.current = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= totalSteps - 1) {
          stopInterval();
          setPlaybackState("done");
          return prev;
        }
        return prev + 1;
      });
    }, intervalMs);
  }, [currentStep, totalSteps, intervalMs, stopInterval]);

  const stepForward = useCallback(() => {
    pause();
    setCurrentStep((prev) => Math.min(prev + 1, totalSteps - 1));
  }, [pause, totalSteps]);

  const stepBack = useCallback(() => {
    pause();
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, [pause]);

  const jumpTo = useCallback(
    (step: number) => {
      pause();
      setCurrentStep(Math.max(0, Math.min(step, totalSteps - 1)));
    },
    [pause, totalSteps]
  );

  const reset = useCallback(() => {
    pause();
    setCurrentStep(0);
    setPlaybackState("idle");
  }, [pause]);

  // Cleanup on unmount
  useEffect(() => () => stopInterval(), [stopInterval]);

  // Reset when events change
  useEffect(() => {
    stopInterval();
    setCurrentStep(0);
    setPlaybackState(events.length > 0 ? "paused" : "idle");
  }, [events, stopInterval]);

  return {
    currentStep,
    currentEvent,
    totalSteps,
    playbackState,
    isPlaying: playbackState === "playing",
    play,
    pause,
    stepForward,
    stepBack,
    jumpTo,
    reset,
    canStepBack: currentStep > 0,
    canStepForward: currentStep < totalSteps - 1,
  };
}
