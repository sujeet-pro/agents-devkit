/**
 * @module interactive
 * Interactive loop helper for PR review sessions.
 * Provides data structures and helpers to track accept/reject/edit/skip
 * decisions across a list of review findings.
 */

/**
 * Severity levels ordered from highest to lowest priority.
 * @type {Record<string, number>}
 */
const SEVERITY_ORDER = {
  error: 0,
  warning: 1,
  suggestion: 2,
  info: 3,
};

/**
 * Format a single review finding for display.
 *
 * @param {object} finding - A review finding object.
 * @param {string} finding.file - File path where the finding occurs.
 * @param {number} [finding.line] - Line number (optional).
 * @param {string} finding.severity - One of "error", "warning",
 *   "suggestion", "info".
 * @param {string} finding.description - Human-readable description.
 * @param {string} [finding.suggestion] - Suggested fix (optional).
 * @returns {string} Formatted multi-line string for display.
 */
export function formatFinding(finding) {
  const parts = [];

  // Location
  const location = finding.line
    ? `${finding.file}:${finding.line}`
    : finding.file;
  parts.push(`[${(finding.severity || "info").toUpperCase()}] ${location}`);

  // Description
  parts.push(`  ${finding.description}`);

  // Suggestion
  if (finding.suggestion) {
    parts.push(`  Suggestion: ${finding.suggestion}`);
  }

  return parts.join("\n");
}

/**
 * @typedef {object} ReviewSession
 * @property {Array<object>} findings - Original findings array.
 * @property {Array<string|null>} actions - Action per finding index:
 *   "accepted", "rejected", "edited", "skipped", or null (unprocessed).
 * @property {Array<string|null>} editedTexts - Edited text per finding
 *   index, or null if not edited.
 * @property {number} currentIndex - Index of the next unprocessed finding.
 */

/**
 * Create a new review session from a list of findings.
 * Findings are sorted by severity (errors first) then by file and line.
 *
 * @param {Array<object>} findings - Array of finding objects.
 * @returns {ReviewSession} A fresh session with all findings unprocessed.
 */
export function createReviewSession(findings) {
  // Sort: severity (most severe first), then file, then line
  const sorted = [...findings].sort((a, b) => {
    const sevA = SEVERITY_ORDER[a.severity] ?? 99;
    const sevB = SEVERITY_ORDER[b.severity] ?? 99;
    if (sevA !== sevB) return sevA - sevB;

    const fileComp = (a.file || "").localeCompare(b.file || "");
    if (fileComp !== 0) return fileComp;

    return (a.line || 0) - (b.line || 0);
  });

  return {
    findings: sorted,
    actions: new Array(sorted.length).fill(null),
    editedTexts: new Array(sorted.length).fill(null),
    currentIndex: 0,
  };
}

/**
 * Get the next unprocessed finding in the session.
 *
 * @param {ReviewSession} session - The review session.
 * @returns {{finding: object, index: number} | null} The next finding and
 *   its index, or null if all findings have been processed.
 */
export function getNextFinding(session) {
  for (let i = session.currentIndex; i < session.findings.length; i++) {
    if (session.actions[i] === null) {
      session.currentIndex = i;
      return { finding: session.findings[i], index: i };
    }
  }
  return null;
}

/**
 * Mark a finding with an action.
 *
 * @param {ReviewSession} session - The review session.
 * @param {number} index - Index of the finding to mark.
 * @param {"accepted"|"rejected"|"edited"|"skipped"} action - The action taken.
 * @param {string} [editedText] - Replacement text when action is "edited".
 * @throws {Error} If the index is out of bounds or the action is invalid.
 */
export function markFinding(session, index, action, editedText) {
  if (index < 0 || index >= session.findings.length) {
    throw new Error(
      `Finding index ${index} out of bounds (0..${session.findings.length - 1})`
    );
  }

  const validActions = ["accepted", "rejected", "edited", "skipped"];
  if (!validActions.includes(action)) {
    throw new Error(
      `Invalid action "${action}". Must be one of: ${validActions.join(", ")}`
    );
  }

  session.actions[index] = action;

  if (action === "edited" && editedText !== undefined) {
    session.editedTexts[index] = editedText;
  }

  // Advance currentIndex past this finding
  if (index === session.currentIndex) {
    session.currentIndex = index + 1;
  }
}

/**
 * Get a summary of the session's current state.
 *
 * @param {ReviewSession} session - The review session.
 * @returns {{accepted: number, rejected: number, edited: number, skipped: number, total: number}}
 */
export function getSessionSummary(session) {
  const summary = { accepted: 0, rejected: 0, edited: 0, skipped: 0, total: session.findings.length };

  for (const action of session.actions) {
    if (action === "accepted") summary.accepted++;
    else if (action === "rejected") summary.rejected++;
    else if (action === "edited") summary.edited++;
    else if (action === "skipped") summary.skipped++;
  }

  return summary;
}

/**
 * Return the findings that have been accepted or edited — these are the
 * comments ready to be posted to a PR.
 *
 * For edited findings the original finding is returned with an
 * `editedText` property added.
 *
 * @param {ReviewSession} session - The review session.
 * @returns {Array<object>} Findings ready to post.
 */
export function getAcceptedComments(session) {
  const comments = [];

  for (let i = 0; i < session.findings.length; i++) {
    const action = session.actions[i];
    if (action === "accepted") {
      comments.push({ ...session.findings[i] });
    } else if (action === "edited") {
      comments.push({
        ...session.findings[i],
        editedText: session.editedTexts[i],
      });
    }
  }

  return comments;
}
