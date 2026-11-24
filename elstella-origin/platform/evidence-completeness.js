const REQUIRED_FOR_REVIEW = [
  "title",
  "sourceUrl",
  "identifier",
  "diseaseContext",
  "modelSystem",
  "cellPopulation",
  "finding",
  "exactLocation",
  "limitations",
  "reviewer",
  "reviewedAt"
];

/**
 * Checks whether a record contains the minimum metadata required to be
 * ready for human verification. This is a completeness check only.
 * It does not verify the source, judge scientific validity, or establish truth.
 */
function assessEvidenceCompleteness(record = {}) {
  const missing = REQUIRED_FOR_REVIEW.filter((field) => {
    const value = record[field];
    return value === undefined || value === null || String(value).trim() === "";
  });

  let sourceUrlValid = false;
  try {
    const url = new URL(record.sourceUrl);
    sourceUrlValid = url.protocol === "https:" || url.protocol === "http:";
  } catch {
    sourceUrlValid = false;
  }

  const issues = [...missing];
  if (!missing.includes("sourceUrl") && !sourceUrlValid) {
    issues.push("sourceUrl must be a valid HTTP(S) URL");
  }

  return {
    complete: issues.length === 0,
    missingOrInvalid: issues,
    status: issues.length === 0 ? "ready-for-human-verification" : "incomplete",
    disclaimer: "Completeness is not scientific verification."
  };
}

module.exports = { assessEvidenceCompleteness, REQUIRED_FOR_REVIEW };
