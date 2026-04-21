import { cn } from "@/lib/utils/cn";
import type { CourseStatus, RoadmapCourse } from "@/types/roadmap";

interface CourseCardProps {
  course: RoadmapCourse;
  variant: "required" | "elective";
  onStatusChange: (status: CourseStatus) => void;
  onSelect?: () => void;
  onPrerequisiteComplete?: (code: string) => void;
  planningLocked?: boolean;
  planningHint?: string | null;
  selectionLocked?: boolean;
}

const statusOptions: Array<{ value: CourseStatus; label: string }> = [
  { value: "PLANNED", label: "Plan" },
  { value: "IN_PROGRESS", label: "Active" },
  { value: "COMPLETED", label: "Done" },
];

const statusClasses: Record<CourseStatus, string> = {
  NOT_STARTED: "border-ink/10 bg-white text-ink/70",
  PLANNED: "border-mint bg-mint/45 text-teal",
  IN_PROGRESS: "border-sand bg-sand/60 text-amber",
  COMPLETED: "border-teal/30 bg-teal text-white",
};

export function CourseCard({
  course,
  variant,
  onStatusChange,
  onPrerequisiteComplete,
  onSelect,
  planningLocked = false,
  planningHint = null,
  selectionLocked = false,
}: CourseCardProps) {
  return (
    <article
      className={cn(
        "rounded-[1.6rem] border p-4 shadow-sm transition",
        variant === "required" ? "border-ink/8 bg-white" : "border-teal/10 bg-mist/80",
        course.isSelected ? "ring-2 ring-teal/25" : "",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-ink px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-white">
              {course.code}
            </span>
            <span
              className={cn(
                "rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em]",
                statusClasses[course.status],
              )}
            >
              {course.status.replace("_", " ")}
            </span>
          </div>
          <h4 className="mt-3 font-display text-xl text-ink">{course.title}</h4>
          <p className="mt-1 text-sm text-ink/65">
            {course.subject ?? "Course"} · {course.credits.toFixed(1)} credits
          </p>
        </div>

        {onSelect ? (
          <button
            type="button"
            onClick={onSelect}
            disabled={selectionLocked}
            className={cn(
              "rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] transition",
              course.isSelected
                ? "bg-teal text-white"
                : "border border-teal/20 bg-white text-teal hover:bg-teal/5",
              selectionLocked && "cursor-not-allowed border-ink/10 bg-ink/5 text-ink/35 hover:bg-ink/5",
            )}
          >
            {course.isSelected ? "Selected" : "Select"}
          </button>
        ) : null}
      </div>

      {course.prerequisiteMessage ? (
        <div
          className={cn(
            "mt-4 rounded-2xl p-4",
            course.prerequisitesMet
              ? "bg-mint/45 text-teal"
              : "bg-rose/8 text-rose",
          )}
        >
          <p className="text-sm font-medium leading-relaxed">{course.prerequisiteMessage}</p>
          
          {!course.prerequisitesMet && course.prerequisiteCourseCodes.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {course.prerequisiteCourseCodes.map((code) => (
                <button
                  key={code}
                  onClick={() => onPrerequisiteComplete?.(code)}
                  className="group flex items-center gap-1.5 rounded-lg border border-rose/20 bg-white/60 px-2 py-1.5 text-[10px] font-bold uppercase tracking-wider text-rose shadow-sm transition hover:bg-white active:scale-95"
                  title={`Mark ${code} as completed`}
                >
                  <span>{code}</span>
                  <span className="opacity-40 transition group-hover:opacity-100">+ Done</span>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : null}

      {course.notes ? (
        <p className="mt-3 text-sm leading-6 text-ink/65">{course.notes}</p>
      ) : null}

      {planningHint ? (
        <p className="mt-3 rounded-2xl bg-ink/5 px-3 py-2 text-sm text-ink/60">
          {planningHint}
        </p>
      ) : null}

      <div className="mt-4 flex flex-wrap gap-2">
        {statusOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onStatusChange(option.value)}
            disabled={planningLocked}
            className={cn(
              "rounded-full px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] transition",
              course.status === option.value
                ? "bg-ink text-white"
                : "border border-ink/10 bg-white text-ink/70 hover:border-ink/20",
              planningLocked && "cursor-not-allowed border-ink/10 bg-ink/5 text-ink/35 hover:border-ink/10",
            )}
          >
            {option.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => onStatusChange("NOT_STARTED")}
          className="rounded-full border border-ink/10 bg-white px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-ink/55 transition hover:border-rose/20 hover:text-rose"
        >
          Clear
        </button>
      </div>
    </article>
  );
}
