const test = require("node:test");
const assert = require("node:assert/strict");
const { assessEvidenceCompleteness } = require("../platform/evidence-completeness.js");

const completeRecord = {
  title: "Example primary study",
  sourceUrl: "https://example.org/article",
  identifier: "10.0000/example",
  diseaseContext: "Defined cardiac disease context",
  modelSystem: "Human tissue",
  cellPopulation: "Cardiac fibroblasts",
  finding: "Finding copied with context from the source",
  exactLocation: "Results, paragraph 2",
  limitations: "Limitations reported by the authors",
  reviewer: "Reviewer initials",
  reviewedAt: "2026-11-24"
};

test("complete record passes metadata gate but is not called verified", () => {
  const result = assessEvidenceCompleteness(completeRecord);
  assert.equal(result.complete, true);
  assert.equal(result.status, "ready-for-human-verification");
  assert.match(result.disclaimer, /not scientific verification/i);
});

test("missing source location and reviewer fail the gate", () => {
  const result = assessEvidenceCompleteness({
    ...completeRecord,
    exactLocation: "",
    reviewer: ""
  });
  assert.equal(result.complete, false);
  assert.ok(result.missingOrInvalid.includes("exactLocation"));
  assert.ok(result.missingOrInvalid.includes("reviewer"));
});

test("non-HTTP source URL fails the gate", () => {
  const result = assessEvidenceCompleteness({
    ...completeRecord,
    sourceUrl: "javascript:alert(1)"
  });
  assert.equal(result.complete, false);
  assert.ok(result.missingOrInvalid.some((item) => item.includes("HTTP(S)")));
});
