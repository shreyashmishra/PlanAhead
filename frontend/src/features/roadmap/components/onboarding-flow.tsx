import { useState } from "react";
import type { Roadmap, RoadmapCourse, TermRoadmap } from "@/types/roadmap";
import { cn } from "@/lib/utils/cn";

interface OnboardingFlowProps {
  roadmap: Roadmap;
  onComplete: (completedCourseCodes: string[]) => void;
  onSkip: () => void;
}

export function OnboardingFlow({ roadmap, onComplete, onSkip }: OnboardingFlowProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedCodes, setCompletedCodes] = useState<Set<string>>(new Set());

  // All terms with requirements should be onboarded
  const onboardingTerms = roadmap.terms
    .filter((t) => t.requirements.some(r => r.course || r.group))
    .sort((a, b) => a.sequence - b.sequence);
  
  if (onboardingTerms.length === 0) {
    onComplete([]);
    return null;
  }

  const currentTerm = onboardingTerms[currentStep];
  const stepTitle = currentTerm.year === 0 ? "Foundation & Prerequisites" : currentTerm.label;

  const handleToggleCourse = (code: string) => {
    setCompletedCodes((prev) => {
      const next = new Set(prev);
      if (next.has(code)) next.delete(code);
      else next.add(code);
      return next;
    });
  };

  const handleNext = () => {
    if (currentStep < onboardingTerms.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(Array.from(completedCodes));
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/40 p-4 backdrop-blur-md">
      <div className="w-full max-w-2xl overflow-hidden rounded-[2.5rem] border border-white/60 bg-white shadow-2xl transition-all">
        {/* Header */}
        <div className="bg-ink px-8 py-10 text-white">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="font-display text-3xl font-bold">Personalize your track</h2>
            <button
              onClick={onSkip}
              className="text-sm font-semibold opacity-60 transition hover:opacity-100"
            >
              Skip for now
            </button>
          </div>
          <p className="text-white/70">
            Tell us which terms and courses you've already finished so we can show you what's left.
          </p>

          <div className="mt-8">
            <p className="text-sm font-medium text-white/40">
              Step {currentStep + 1} of {onboardingTerms.length}
            </p>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/20">
              <div
                className="h-full bg-teal transition-all duration-500 ease-out"
                style={{ width: `${((currentStep + 1) / onboardingTerms.length) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8">
          <div className="mb-8 flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-teal text-2xl font-bold text-white shadow-lg shadow-teal/20">
              {stepTitle}
            </div>
            <div>
              <h3 className="text-xl font-bold text-ink">
                {currentTerm.year === 0 ? "Initial Requirements" : `${currentTerm.season} · Year ${currentTerm.year}`}
              </h3>
              <p className="text-sm text-ink/50">Select courses you have completed in this category</p>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {currentTerm.requirements.map((req, idx) => {
              const course = req.course;
              if (!course) return null;

              const isSelected = completedCodes.has(course.code);

              return (
                <button
                  key={course.code + idx}
                  onClick={() => handleToggleCourse(course.code)}
                  className={cn(
                    "flex flex-col items-start rounded-2xl border p-4 text-left transition",
                    isSelected
                      ? "border-teal/50 bg-teal/5 ring-1 ring-teal/20"
                      : "border-ink/10 bg-cloud hover:border-ink/20",
                  )}
                >
                  <div className="flex w-full items-center justify-between gap-2">
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                        isSelected ? "bg-teal text-white" : "bg-ink/10 text-ink/50",
                      )}
                    >
                      {course.code}
                    </span>
                    {isSelected && (
                      <svg className="h-4 w-4 text-teal" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </div>
                  <h4 className="mt-3 font-semibold text-ink">{course.title}</h4>
                  <p className="mt-1 text-xs text-ink/50">{course.credits} credits</p>
                </button>
              );
            })}
          </div>

          {currentTerm.requirements.length === 0 && (
            <div className="rounded-2xl border border-dashed border-ink/10 p-8 text-center text-ink/40">
              No specific requirements defined for this category yet.
            </div>
          )}

          {/* Footer Actions */}
          <div className="mt-10 flex items-center justify-between border-t border-ink/5 pt-8">
            <button
              onClick={handleBack}
              disabled={currentStep === 0}
              className={cn(
                "rounded-xl px-6 py-3 text-sm font-bold uppercase tracking-widest transition",
                currentStep === 0
                  ? "pointer-events-none opacity-0"
                  : "text-ink/40 hover:bg-ink/5 hover:text-ink",
              )}
            >
              Back
            </button>

            <button
              onClick={handleNext}
              className="group flex items-center gap-3 rounded-2xl bg-ink px-8 py-4 font-bold text-white transition hover:-translate-y-0.5 hover:shadow-xl active:translate-y-0"
            >
              <span>{currentStep === onboardingTerms.length - 1 ? "Finish Setup" : "Next Category"}</span>
              <svg
                className="h-4 w-4 transition group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
