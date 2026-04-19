package waterloo

import "testing"

func TestParseCoursePrerequisitesParsesUniqueCodes(t *testing.T) {
	result := parseCoursePrerequisites(
		"Prereq: CS 135, MATH137, and one of CS 135 or MATH 137.",
		false,
	)

	if len(result) != 2 {
		t.Fatalf("expected 2 unique prerequisites, got %d", len(result))
	}

	if result[0].CourseCode != "CS 135" || result[1].CourseCode != "MATH 137" {
		t.Fatalf("unexpected prerequisite codes: %#v", result)
	}

	for _, prerequisite := range result {
		if prerequisite.IsCorequisite {
			t.Fatal("expected parsed prerequisites to not be marked as corequisites")
		}
	}
}

func TestParseCoursePrerequisitesMarksCorequisites(t *testing.T) {
	result := parseCoursePrerequisites("Coreq: PHYS121L or PHYS 121.", true)

	if len(result) != 2 {
		t.Fatalf("expected 2 corequisites, got %d", len(result))
	}

	for _, prerequisite := range result {
		if !prerequisite.IsCorequisite {
			t.Fatal("expected parsed requirements to be marked as corequisites")
		}
	}

	if result[0].CourseCode != "PHYS 121L" || result[1].CourseCode != "PHYS 121" {
		t.Fatalf("unexpected corequisite codes: %#v", result)
	}
}
