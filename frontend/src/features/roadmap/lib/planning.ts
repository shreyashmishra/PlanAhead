import type {
  CourseStatus,
  ProgressSnapshot,
  RoadmapCourse,
  TermRoadmap,
} from "@/types/roadmap";

export interface PlanningRuleResult {
  allowed: boolean;
  reason: string | null;
}

interface EvaluateCoursePlanningArgs {
  activeTerm: TermRoadmap | null;
  targetTerm: TermRoadmap | null;
  course: Pick<RoadmapCourse, "code" | "prerequisiteCourseCodes">;
  effectiveCourseTermByCode: Map<string, string>;
  termByCode: Map<string, TermRoadmap>;
  progressSnapshot: ProgressSnapshot;
}

export function evaluateCoursePlanning({
  activeTerm,
  targetTerm,
  course,
  effectiveCourseTermByCode,
  termByCode,
  progressSnapshot,
}: EvaluateCoursePlanningArgs): PlanningRuleResult {
  if (!activeTerm) {
    return {
      allowed: false,
      reason: "Select an academic term in the pathway before planning courses.",
    };
  }

  if (!targetTerm || targetTerm.year <= 0) {
    return {
      allowed: false,
      reason: "Move this course into an academic term before planning it.",
    };
  }

  if (activeTerm.code !== targetTerm.code) {
    return {
      allowed: false,
      reason: `Planning is locked to ${activeTerm.label}. Select ${targetTerm.label} to work on this term instead.`,
    };
  }

  const unmet = course.prerequisiteCourseCodes.filter((prerequisiteCode) => {
    const prerequisiteTermCode = effectiveCourseTermByCode.get(prerequisiteCode);
    if (prerequisiteTermCode) {
      const prerequisiteTerm = termByCode.get(prerequisiteTermCode);
      return !prerequisiteTerm || prerequisiteTerm.sequence >= targetTerm.sequence;
    }

    const prerequisiteStatus = progressSnapshot.courseStatuses[prerequisiteCode];
    return !isPreviouslyTaken(prerequisiteStatus);
  });

  if (unmet.length === 0) {
    return { allowed: true, reason: null };
  }

  return {
    allowed: false,
    reason: buildPrerequisiteMessage(unmet),
  };
}

function isPreviouslyTaken(status: CourseStatus | undefined): boolean {
  return status === "IN_PROGRESS" || status === "COMPLETED";
}

function buildPrerequisiteMessage(courseCodes: string[]): string {
  if (courseCodes.length === 1) {
    return `Take ${courseCodes[0]} in an earlier term before planning this course.`;
  }

  return `Take ${joinCourseCodes(courseCodes)} in earlier terms before planning this course.`;
}

function joinCourseCodes(courseCodes: string[]): string {
  if (courseCodes.length <= 2) {
    return courseCodes.join(" and ");
  }

  return `${courseCodes.slice(0, -1).join(", ")}, and ${courseCodes[courseCodes.length - 1]}`;
}
