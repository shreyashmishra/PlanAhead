import { useEffect, useMemo, useState } from "react";

import { CourseCard } from "@/features/roadmap/components/course-card";
import { ElectiveGroupCard } from "@/features/roadmap/components/elective-group-card";
import { evaluateCoursePlanning } from "@/features/roadmap/lib/planning";
import type {
  CourseStatus,
  ProgressSnapshot,
  Roadmap,
  RoadmapCourse,
  TermRequirement,
  TermRoadmap,
} from "@/types/roadmap";
import { cn } from "@/lib/utils/cn";

interface RoadmapBoardProps {
  roadmap: Roadmap | null;
  progressSnapshot: ProgressSnapshot;
  onCourseStatusChange: (courseCode: string, status: CourseStatus) => void;
  onElectiveSelect: (groupCode: string, courseCode: string) => void;
  onElectiveStatusChange: (groupCode: string, courseCode: string, status: CourseStatus) => void;
  onElectiveClear: (groupCode: string) => void;
  currentUserKey: string | null;
  isGuest?: boolean;
}

function shortLabel(term: TermRoadmap): string {
  return term.label;
}

function groupByYear(
  terms: TermRoadmap[],
): { year: number; label: string; items: TermRoadmap[] }[] {
  const sorted = [...terms].sort((a, b) => a.sequence - b.sequence);
  const map = new Map<number, TermRoadmap[]>();

  for (const term of sorted) {
    const items = map.get(term.year) ?? [];
    items.push(term);
    map.set(term.year, items);
  }

  return Array.from(map.entries())
    .sort(([left], [right]) => left - right)
    .map(([year, items]) => ({
      year,
      label: year === 0 ? "Requirements" : `Year ${year}`,
      items,
    }));
}

function termCompletion(term: TermRoadmap): number {
  return term.totalCount > 0 ? term.completedCount / term.totalCount : 0;
}

function requirementKey(requirement: TermRequirement): string | null {
  return requirement.course?.code ?? requirement.group?.code ?? null;
}

function requirementStatus(requirement: TermRequirement): CourseStatus {
  if (requirement.course) {
    return requirement.course.status;
  }

  if (requirement.group) {
    return requirement.group.status;
  }

  return "NOT_STARTED";
}

function standardAcademicTerms(existingTerms: TermRoadmap[]): TermRoadmap[] {
  const existingTermLabels = new Set(existingTerms.map((term) => term.label));
  const standardTerms = [
    { year: 1, term: "1A", season: "FALL", sequence: 100 },
    { year: 1, term: "1B", season: "WINTER", sequence: 101 },
    { year: 2, term: "2A", season: "FALL", sequence: 200 },
    { year: 2, term: "2B", season: "WINTER", sequence: 201 },
    { year: 3, term: "3A", season: "FALL", sequence: 300 },
    { year: 3, term: "3B", season: "WINTER", sequence: 301 },
    { year: 4, term: "4A", season: "FALL", sequence: 400 },
    { year: 4, term: "4B", season: "WINTER", sequence: 401 },
  ];

  return standardTerms
    .filter((term) => !existingTermLabels.has(term.term))
    .map((term) => ({
      code: `term-${term.term.toLowerCase()}`,
      label: term.term,
      year: term.year,
      season: term.season as TermRoadmap["season"],
      sequence: term.sequence,
      completedCount: 0,
      totalCount: 0,
      requirements: [],
    }));
}

export function RoadmapBoard({
  roadmap,
  progressSnapshot,
  onCourseStatusChange,
  onElectiveSelect,
  onElectiveStatusChange,
  onElectiveClear,
  currentUserKey,
  isGuest,
}: RoadmapBoardProps) {
  const [plannedTerms, setPlannedTerms] = useState<Record<string, string>>({});
  const [termOverrides, setTermOverrides] = useState<Record<string, boolean>>({});
  const [activePlanningTermCode, setActivePlanningTermCode] = useState<string | null>(null);
  const [planningMessage, setPlanningMessage] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && !isGuest && currentUserKey) {
      const stored = localStorage.getItem(`plannedTerms_${currentUserKey}`);
      if (stored) {
        try {
          setPlannedTerms(JSON.parse(stored));
        } catch {
          setPlannedTerms({});
        }
        return;
      }
    }

    setPlannedTerms({});
  }, [currentUserKey, isGuest]);

  useEffect(() => {
    if (typeof window !== "undefined" && !isGuest && currentUserKey) {
      const stored = localStorage.getItem(`termOverrides_${currentUserKey}`);
      if (stored) {
        try {
          setTermOverrides(JSON.parse(stored));
        } catch {
          setTermOverrides({});
        }
        return;
      }
    }

    setTermOverrides({});
  }, [currentUserKey, isGuest]);

  const planningData = useMemo(() => {
    if (!roadmap) {
      return null;
    }

    const sourceTermMap = new Map<string, string>();
    const requirementByKey = new Map<string, TermRequirement>();
    const allRequirements: TermRequirement[] = [];

    for (const term of roadmap.terms) {
      for (const requirement of term.requirements) {
        const key = requirementKey(requirement);
        if (!key) {
          continue;
        }

        sourceTermMap.set(key, term.code);
        requirementByKey.set(key, requirement);
        allRequirements.push(requirement);
      }
    }

    const finalTerms = [...roadmap.terms, ...standardAcademicTerms(roadmap.terms)].map((term) => ({
      ...term,
      completedCount: 0,
      totalCount: 0,
      requirements: [] as TermRequirement[],
    }));

    const termByCode = new Map(finalTerms.map((term) => [term.code, term]));

    for (const requirement of allRequirements) {
      const key = requirementKey(requirement);
      if (!key) {
        continue;
      }

      const targetTermCode = plannedTerms[key] ?? sourceTermMap.get(key);
      const targetTerm = targetTermCode ? termByCode.get(targetTermCode) : null;
      if (!targetTerm) {
        continue;
      }

      targetTerm.requirements.push(requirement);
    }

    const sortedTerms = finalTerms
      .map((term) => ({
        ...term,
        completedCount: term.requirements.reduce(
          (count, requirement) =>
            count + (requirementStatus(requirement) === "COMPLETED" ? 1 : 0),
          0,
        ),
        totalCount: term.requirements.length,
        requirements: [...term.requirements].sort((left, right) => left.sequence - right.sequence),
      }))
      .sort((left, right) => left.sequence - right.sequence);

    const sortedTermByCode = new Map(sortedTerms.map((term) => [term.code, term]));
    const effectiveCourseTermByCode = new Map<string, string>();

    for (const term of sortedTerms) {
      for (const requirement of term.requirements) {
        if (requirement.course) {
          effectiveCourseTermByCode.set(requirement.course.code, term.code);
        }
        if (requirement.group?.selectedCourseCode) {
          effectiveCourseTermByCode.set(requirement.group.selectedCourseCode, term.code);
        }
      }
    }

    return {
      groups: groupByYear(sortedTerms),
      pathwayTerms: sortedTerms.filter((term) => term.year > 0),
      requirementByKey,
      sortedTerms,
      termByCode: sortedTermByCode,
      effectiveCourseTermByCode,
    };
  }, [plannedTerms, roadmap]);

  useEffect(() => {
    if (!planningData) {
      setActivePlanningTermCode(null);
      return;
    }

    setActivePlanningTermCode((current) =>
      current && planningData.termByCode.has(current) ? current : null,
    );
  }, [planningData]);

  if (!roadmap || !planningData) {
    return (
      <section className="rounded-[2rem] border border-white/60 bg-white/80 p-12 text-center shadow-panel backdrop-blur">
        <div className="mx-auto max-w-sm">
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-cloud">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path
                d="M6 8h20M6 14h14M6 20h10"
                stroke="#102336"
                strokeOpacity="0.35"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <h2 className="font-display text-2xl text-ink">
            Your academic pathway appears here
          </h2>
          <p className="mt-3 text-sm leading-6 text-ink/55">
            Select a program on the left to load your personalized roadmap from
            1A to 4B.
          </p>
        </div>
      </section>
    );
  }

  const activePlanningTerm = activePlanningTermCode
    ? planningData.termByCode.get(activePlanningTermCode) ?? null
    : null;

  const hasPathway = planningData.pathwayTerms.length > 0;
  const planningBannerMessage =
    planningMessage ??
    (activePlanningTerm
      ? `Planning ${activePlanningTerm.label}. You can only move courses into this term, and prerequisites must already sit in earlier terms.`
      : hasPathway
        ? "Select an academic term in the pathway to start planning that term."
        : null);

  const persistPlannedTerms = (next: Record<string, string>) => {
    if (typeof window !== "undefined" && !isGuest && currentUserKey) {
      localStorage.setItem(`plannedTerms_${currentUserKey}`, JSON.stringify(next));
    }
  };

  const persistTermOverrides = (next: Record<string, boolean>) => {
    if (typeof window !== "undefined" && !isGuest && currentUserKey) {
      localStorage.setItem(`termOverrides_${currentUserKey}`, JSON.stringify(next));
    }
  };

  const setPlannedTermsAndPersist = (
    updater: (previous: Record<string, string>) => Record<string, string>,
  ) => {
    setPlannedTerms((previous) => {
      const next = updater(previous);
      persistPlannedTerms(next);
      return next;
    });
  };

  const setTermOverridesAndPersist = (
    updater: (previous: Record<string, boolean>) => Record<string, boolean>,
  ) => {
    setTermOverrides((previous) => {
      const next = updater(previous);
      persistTermOverrides(next);
      return next;
    });
  };

  const evaluateTermPlanning = (term: TermRoadmap) => {
    if (!activePlanningTerm) {
      return {
        allowed: false,
        reason: "Select an academic term in the pathway before planning courses.",
      };
    }

    if (term.year > 0 && activePlanningTerm.code !== term.code) {
      return {
        allowed: false,
        reason: `Planning is locked to ${activePlanningTerm.label}. Select ${term.label} to plan this term.`,
      };
    }

    return { allowed: true, reason: null };
  };

  const resolvePlanningTargetTerm = (term: TermRoadmap) =>
    term.year > 0 ? term : activePlanningTerm;

  const termLoad = (term: TermRoadmap | null) => {
    if (!term || term.year <= 0) {
      return 0;
    }

    return term.requirements.length;
  };

  const termCapacity = (term: TermRoadmap | null) => {
    if (!term || term.year <= 0) {
      return 0;
    }

    return termOverrides[term.code] ? 7 : 5;
  };

  const buildLoadMessage = (term: TermRoadmap, nextLoad: number, capacity: number) => {
    if (nextLoad > 7) {
      return `${term.label} is already at the maximum overload of 7 courses.`;
    }

    if (capacity === 5 && nextLoad > 5) {
      return `${term.label} is at the 5-course limit. Approve an overload to add a 6th or 7th course.`;
    }

    if (capacity === 7 && nextLoad > 7) {
      return `${term.label} cannot exceed 7 courses, even with an overload.`;
    }

    return null;
  };

  const evaluateTermLoad = (
    targetTerm: TermRoadmap | null,
    requirementCode: string,
  ) => {
    if (!targetTerm || targetTerm.year <= 0) {
      return { allowed: true, reason: null as string | null };
    }

    const currentTermCode = plannedTerms[requirementCode] ?? planningData.effectiveCourseTermByCode.get(requirementCode);
    if (currentTermCode === targetTerm.code) {
      return { allowed: true, reason: null as string | null };
    }

    const nextLoad = termLoad(targetTerm) + 1;
    const capacity = termCapacity(targetTerm);
    const reason = buildLoadMessage(targetTerm, nextLoad, capacity);

    return {
      allowed: reason === null,
      reason,
    };
  };

  const persistRequirementInActiveTerm = (requirementCode: string, term: TermRoadmap) => {
    if (term.year <= 0) {
      return;
    }

    setPlannedTermsAndPersist((previous) => ({
      ...previous,
      [requirementCode]: term.code,
    }));
  };

  const evaluateCourseForTerm = (
    course: RoadmapCourse,
    term: TermRoadmap,
    loadRequirementCode: string = course.code,
  ) =>
    {
      const targetTerm = resolvePlanningTargetTerm(term);
      const prerequisiteRule = evaluateCoursePlanning({
        activeTerm: activePlanningTerm,
        targetTerm,
        course,
        effectiveCourseTermByCode: planningData.effectiveCourseTermByCode,
        termByCode: planningData.termByCode,
        progressSnapshot,
      });

      if (!prerequisiteRule.allowed) {
        return prerequisiteRule;
      }

      return evaluateTermLoad(targetTerm, loadRequirementCode);
    };

  const handleDragStart = (event: React.DragEvent, key: string) => {
    event.dataTransfer.setData("requirementKey", key);
    event.dataTransfer.effectAllowed = "move";

    const target = event.currentTarget;
    setTimeout(() => {
      target.classList.add("opacity-50", "scale-95");
    }, 0);
  };

  const handleDragEnd = (event: React.DragEvent) => {
    event.currentTarget.classList.remove("opacity-50", "scale-95");
  };

  const handleDrop = (event: React.DragEvent, termCode: string) => {
    event.preventDefault();
    event.currentTarget.classList.remove("bg-white/40", "border-teal/50");

    const requirementKeyValue = event.dataTransfer.getData("requirementKey");
    const targetTerm = planningData.termByCode.get(termCode);
    if (!requirementKeyValue || !targetTerm) {
      return;
    }

    const requirement = planningData.requirementByKey.get(requirementKeyValue);
    if (!requirement) {
      return;
    }

    const termRule = evaluateTermPlanning(targetTerm);
    if (!termRule.allowed) {
      setPlanningMessage(termRule.reason);
      return;
    }

    const loadRule = evaluateTermLoad(targetTerm, requirementKeyValue);
    if (!loadRule.allowed) {
      setPlanningMessage(loadRule.reason);
      return;
    }

    if (requirement.course) {
      const courseRule = evaluateCoursePlanning({
        activeTerm: activePlanningTerm,
        targetTerm,
        course: requirement.course,
        effectiveCourseTermByCode: planningData.effectiveCourseTermByCode,
        termByCode: planningData.termByCode,
        progressSnapshot,
      });

      if (!courseRule.allowed) {
        setPlanningMessage(courseRule.reason);
        return;
      }
    }

    if (requirement.group?.selectedCourseCode) {
      const selectedOption = requirement.group.options.find(
        (option) => option.code === requirement.group?.selectedCourseCode,
      );

      if (selectedOption) {
        const optionRule = evaluateCoursePlanning({
          activeTerm: activePlanningTerm,
          targetTerm,
          course: selectedOption,
          effectiveCourseTermByCode: planningData.effectiveCourseTermByCode,
          termByCode: planningData.termByCode,
          progressSnapshot,
        });

        if (!optionRule.allowed) {
          setPlanningMessage(optionRule.reason);
          return;
        }
      }
    }

    setPlannedTermsAndPersist((previous) => ({
      ...previous,
      [requirementKeyValue]: termCode,
    }));
    setPlanningMessage(`Planning ${targetTerm.label}.`);
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const handleDragEnter = (event: React.DragEvent, term: TermRoadmap) => {
    event.preventDefault();
    if (!activePlanningTerm || activePlanningTerm.code !== term.code) {
      return;
    }
    event.currentTarget.classList.add("bg-white/40", "border-teal/50");
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.currentTarget.classList.remove("bg-white/40", "border-teal/50");
  };

  const clearTermPlan = (key: string) => {
    setPlannedTermsAndPersist((previous) => {
      const next = { ...previous };
      delete next[key];
      return next;
    });
    setPlanningMessage(null);
  };

  const handlePathwayTermClick = (term: TermRoadmap) => {
    setActivePlanningTermCode((current) => {
      if (current === term.code) {
        setPlanningMessage("Select an academic term in the pathway to start planning that term.");
        return null;
      }

      setPlanningMessage(
        `Planning ${term.label}. You can only move courses into this term, and prerequisites must already sit in earlier terms.`,
      );
      return term.code;
    });
  };

  const approveTermOverride = (term: TermRoadmap) => {
    if (term.year <= 0) {
      return;
    }

    setTermOverridesAndPersist((previous) => ({
      ...previous,
      [term.code]: true,
    }));
    setPlanningMessage(`${term.label} overload approved. This term can now hold up to 7 courses.`);
  };

  const currentTermLoad = termLoad(activePlanningTerm);
  const currentTermCapacity = termCapacity(activePlanningTerm);
  const loadAlert =
    activePlanningTerm && activePlanningTerm.year > 0
      ? currentTermLoad >= 7
        ? `${activePlanningTerm.label} is at the maximum overload of 7 courses.`
        : currentTermLoad >= 5 && !termOverrides[activePlanningTerm.code]
          ? `${activePlanningTerm.label} is at the 5-course limit. Approve an overload to add a 6th or 7th course.`
          : currentTermLoad >= 5
            ? `${activePlanningTerm.label} is running as an overload at ${currentTermLoad}/${currentTermCapacity} courses.`
            : null
      : null;

  return (
    <section className="space-y-5">
      {planningBannerMessage ? (
        <div className="rounded-[1.6rem] border border-ink/8 bg-white/75 px-4 py-3 text-sm text-ink/70 shadow-sm">
          {planningBannerMessage}
        </div>
      ) : null}

      {loadAlert && activePlanningTerm ? (
        <div className="flex items-center justify-between gap-3 rounded-[1.6rem] border border-amber/25 bg-sand/35 px-4 py-3 text-sm text-ink/75 shadow-sm">
          <p>{loadAlert}</p>
          {!termOverrides[activePlanningTerm.code] && currentTermLoad >= 5 && currentTermLoad < 7 ? (
            <button
              type="button"
              onClick={() => approveTermOverride(activePlanningTerm)}
              className="rounded-full bg-ink px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-ink/90"
            >
              Approve Overload
            </button>
          ) : null}
        </div>
      ) : null}

      {hasPathway && (
        <div className="rounded-[2rem] border border-white/70 bg-white/80 p-5 shadow-panel backdrop-blur">
          <p className="mb-4 text-xs font-semibold uppercase tracking-[0.24em] text-ink/50">
            Academic Pathway
          </p>
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {planningData.pathwayTerms.map((term, index) => {
              const pct = termCompletion(term);
              const isDone = pct >= 1;
              const isActive = pct > 0 && pct < 1;
              const isSelected = activePlanningTermCode === term.code;

              return (
                <div key={term.code} className="flex flex-shrink-0 items-center gap-1.5">
                  <button
                    type="button"
                    onClick={() => handlePathwayTermClick(term)}
                    className={cn(
                      "flex min-w-[52px] flex-col items-center gap-1 rounded-xl px-3 py-2.5 text-center transition",
                      isSelected
                        ? "bg-ink text-white shadow-sm"
                        : isDone
                          ? "bg-teal text-white"
                          : isActive
                            ? "bg-sand/80 text-amber"
                            : "border border-ink/8 bg-cloud text-ink/50",
                    )}
                  >
                    <span className="text-xs font-bold tracking-wide">
                      {shortLabel(term)}
                    </span>
                    <span className="text-[10px] opacity-70">
                      {term.completedCount}/{term.totalCount}
                    </span>
                  </button>
                  {index < planningData.pathwayTerms.length - 1 && (
                    <svg
                      className="flex-shrink-0 text-ink/20"
                      width="14"
                      height="14"
                      viewBox="0 0 14 14"
                      fill="none"
                    >
                      <path
                        d="M3 7h8M8 4l3 3-3 3"
                        stroke="currentColor"
                        strokeWidth="1.4"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {planningData.groups.map(({ year, label: groupLabel, items }) => {
        if (year === 0 && items.every((term) => term.requirements.length === 0)) {
          return null;
        }

        return (
          <div key={year} className="space-y-3">
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "rounded-full px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.2em]",
                  year === 0 ? "bg-ink/8 text-ink/60" : "bg-ink text-white",
                )}
              >
                {groupLabel}
              </div>
              <div className="h-px flex-1 bg-ink/10" />
            </div>

            <div
              className={cn(
                "grid gap-4",
                year > 0 ? "xl:grid-cols-2" : "xl:grid-cols-1",
              )}
            >
              {items.map((term) => {
                const pct = termCompletion(term);
                const isAcademic = term.year > 0;
                const isPlanningTerm = activePlanningTermCode === term.code;
                const load = termLoad(term);
                const capacity = termCapacity(term);
                const isAtStandardLimit = isAcademic && load >= 5;

                return (
                  <article
                    key={term.code}
                    onDrop={(event) => handleDrop(event, term.code)}
                    onDragOver={handleDragOver}
                    onDragEnter={(event) => handleDragEnter(event, term)}
                    onDragLeave={handleDragLeave}
                    className={cn(
                      "flex flex-col rounded-[1.7rem] border border-ink/8 bg-cloud p-5 transition-colors",
                      isPlanningTerm && "border-teal/40 ring-2 ring-teal/15",
                    )}
                  >
                    <div className="mb-4 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        {isAcademic ? (
                          <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-ink text-sm font-bold text-white">
                            {shortLabel(term)}
                          </div>
                        ) : (
                          <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-ink/8">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                              <path
                                d="M3 5h12M3 9h8M3 13h10"
                                stroke="#102336"
                                strokeOpacity="0.4"
                                strokeWidth="1.5"
                                strokeLinecap="round"
                              />
                            </svg>
                          </div>
                        )}
                        <div>
                          <h3 className="font-display text-xl leading-tight text-ink">
                            {isAcademic
                              ? term.season === "FALL"
                                ? `Fall · Year ${term.year}`
                                : term.season === "WINTER"
                                  ? `Winter · Year ${term.year}`
                                  : `Spring · Year ${term.year}`
                              : term.label}
                          </h3>
                          {isPlanningTerm ? (
                            <p className="mt-1 text-xs font-semibold uppercase tracking-[0.18em] text-teal">
                              Planning Now
                            </p>
                          ) : null}
                          {isAcademic ? (
                            <p className="mt-1 text-xs text-ink/45">
                              {termOverrides[term.code]
                                ? `${load}/${capacity} courses · overload active`
                                : `${load}/5 courses`}
                            </p>
                          ) : null}
                        </div>
                      </div>

                      {term.totalCount > 0 && (
                        <div className="rounded-2xl bg-white px-3 py-2 text-right shadow-sm">
                          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ink/40">
                            Done
                          </p>
                          <p className="mt-0.5 font-display text-xl text-ink">
                            {term.completedCount}/{term.totalCount}
                          </p>
                        </div>
                      )}
                    </div>

                    {term.totalCount > 0 && (
                      <div className="mb-4 h-1.5 overflow-hidden rounded-full bg-ink/8">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-teal to-amber transition-all duration-500"
                          style={{ width: `${pct * 100}%` }}
                        />
                      </div>
                    )}

                    <div className="min-h-[50px] space-y-3 rounded-xl">
                      {isAtStandardLimit ? (
                        <div
                          className={cn(
                            "rounded-2xl border px-4 py-3 text-sm shadow-sm",
                            load >= 7
                              ? "border-rose/20 bg-rose/8 text-rose"
                              : "border-amber/20 bg-sand/35 text-ink/75",
                          )}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <p>
                              {load >= 7
                                ? `${term.label} is full at 7 courses.`
                                : termOverrides[term.code]
                                  ? `${term.label} is running an overload at ${load}/${capacity} courses.`
                                  : `${term.label} has reached the 5-course limit.`}
                            </p>
                            {!termOverrides[term.code] && load >= 5 && load < 7 ? (
                              <button
                                type="button"
                                onClick={() => approveTermOverride(term)}
                                className="rounded-full bg-ink px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-ink/90"
                              >
                                Approve Overload
                              </button>
                            ) : null}
                          </div>
                        </div>
                      ) : null}

                      {term.requirements.length === 0 && isPlanningTerm ? (
                        <div className="rounded-2xl border border-dashed border-teal/25 bg-white/60 px-4 py-5 text-sm text-ink/55">
                          Drag eligible courses into {term.label} to plan this term.
                        </div>
                      ) : null}

                      {term.requirements.map((requirement) => {
                        const key = requirementKey(requirement);
                        if (!key) {
                          return null;
                        }

                        if (requirement.course) {
                          const isMoved = Boolean(plannedTerms[requirement.course.code]);
                          const planningRule = evaluateCourseForTerm(requirement.course, term);
                          return (
                            <div
                              key={`${term.code}-${requirement.course.code}`}
                              draggable
                              onDragStart={(event) => handleDragStart(event, requirement.course!.code)}
                              onDragEnd={handleDragEnd}
                              className="relative cursor-move"
                            >
                              <CourseCard
                                course={requirement.course}
                                variant="required"
                                planningLocked={!planningRule.allowed}
                                planningHint={planningRule.reason}
                                onStatusChange={(status) => {
                                  if (status !== "NOT_STARTED" && !planningRule.allowed) {
                                    setPlanningMessage(planningRule.reason);
                                    return;
                                  }
                                  const targetTerm = resolvePlanningTargetTerm(term);
                                  if (status !== "NOT_STARTED" && targetTerm) {
                                    persistRequirementInActiveTerm(requirement.course!.code, targetTerm);
                                  }
                                  setPlanningMessage(null);
                                  onCourseStatusChange(requirement.course!.code, status);
                                }}
                              />
                              {isMoved ? (
                                <button
                                  type="button"
                                  onClick={() => clearTermPlan(requirement.course!.code)}
                                  className="absolute right-2 top-2 rounded-full bg-rose/10 p-1 text-xs text-rose shadow-sm transition hover:bg-rose/20"
                                  title="Reset to default term"
                                >
                                  Reset
                                </button>
                              ) : null}
                            </div>
                          );
                        }

                        if (requirement.group) {
                          const isMoved = Boolean(plannedTerms[requirement.group.code]);
                          const groupRule = evaluateTermPlanning(term);

                          return (
                            <div
                              key={`${term.code}-${requirement.group.code}`}
                              draggable
                              onDragStart={(event) => handleDragStart(event, requirement.group!.code)}
                              onDragEnd={handleDragEnd}
                              className="relative cursor-move"
                            >
                              <ElectiveGroupCard
                                group={requirement.group}
                                groupPlanningLocked={!groupRule.allowed}
                                getOptionPlanningState={(courseCode) => {
                                  const option = requirement.group!.options.find(
                                    (candidate) => candidate.code === courseCode,
                                  );
                                  if (!option) {
                                    return {
                                      planningLocked: true,
                                      planningHint: "Unable to plan this elective right now.",
                                      selectionLocked: true,
                                    };
                                  }

                                  const optionRule = evaluateCourseForTerm(option, term, requirement.group!.code);
                                  return {
                                    planningLocked: !optionRule.allowed,
                                    planningHint: optionRule.reason,
                                    selectionLocked: !optionRule.allowed,
                                  };
                                }}
                                onSelectOption={(courseCode) => {
                                  const option = requirement.group!.options.find(
                                    (candidate) => candidate.code === courseCode,
                                  );
                                  if (!option) {
                                    return;
                                  }

                                  const optionRule = evaluateCourseForTerm(option, term, requirement.group!.code);
                                  if (!optionRule.allowed) {
                                    setPlanningMessage(optionRule.reason);
                                    return;
                                  }

                                  const targetTerm = resolvePlanningTargetTerm(term);
                                  if (targetTerm) {
                                    persistRequirementInActiveTerm(requirement.group!.code, targetTerm);
                                  }
                                  setPlanningMessage(null);
                                  onElectiveSelect(requirement.group!.code, courseCode);
                                }}
                                onOptionStatusChange={(courseCode, status) => {
                                  const option = requirement.group!.options.find(
                                    (candidate) => candidate.code === courseCode,
                                  );
                                  if (!option) {
                                    return;
                                  }

                                  const optionRule = evaluateCourseForTerm(option, term, requirement.group!.code);
                                  if (status !== "NOT_STARTED" && !optionRule.allowed) {
                                    setPlanningMessage(optionRule.reason);
                                    return;
                                  }

                                  const targetTerm = resolvePlanningTargetTerm(term);
                                  if (status !== "NOT_STARTED" && targetTerm) {
                                    persistRequirementInActiveTerm(requirement.group!.code, targetTerm);
                                  }
                                  setPlanningMessage(null);
                                  onElectiveStatusChange(requirement.group!.code, courseCode, status);
                                }}
                                onClearSelection={() => {
                                  if (!groupRule.allowed) {
                                    setPlanningMessage(groupRule.reason);
                                    return;
                                  }

                                  setPlanningMessage(null);
                                  onElectiveClear(requirement.group!.code);
                                }}
                              />
                              {isMoved ? (
                                <button
                                  type="button"
                                  onClick={() => clearTermPlan(requirement.group!.code)}
                                  className="absolute right-2 top-2 z-10 rounded-full bg-rose/10 p-1 text-xs text-rose shadow-sm transition hover:bg-rose/20"
                                  title="Reset to default term"
                                >
                                  Reset
                                </button>
                              ) : null}
                            </div>
                          );
                        }

                        return null;
                      })}
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        );
      })}
    </section>
  );
}
