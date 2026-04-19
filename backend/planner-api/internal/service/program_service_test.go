package service

import (
	"testing"

	"planahead/planner-api/internal/model"
)

func TestEvaluateCourseIncludesPrerequisiteCourseCodes(t *testing.T) {
	requirement := model.CourseRequirementDefinition{
		Course: model.CourseDefinition{
			Code:    "CS 246",
			Title:   "Object-Oriented Software Development",
			Credits: 0.5,
		},
		Prerequisites: []model.PrerequisiteDefinition{
			{CourseCode: "CS 136"},
			{CourseCode: "MATH 135"},
			{CourseCode: "CS 136"},
		},
	}

	course := evaluateCourse(requirement, model.ProgressSnapshot{
		CourseStatuses:     map[string]model.CourseStatus{},
		ElectiveSelections: map[string]string{},
	}, true)

	if len(course.PrerequisiteCourseCodes) != 2 {
		t.Fatalf("expected 2 unique prerequisite codes, got %d", len(course.PrerequisiteCourseCodes))
	}

	if course.PrerequisiteCourseCodes[0] != "CS 136" || course.PrerequisiteCourseCodes[1] != "MATH 135" {
		t.Fatalf("unexpected prerequisite codes: %#v", course.PrerequisiteCourseCodes)
	}
}
