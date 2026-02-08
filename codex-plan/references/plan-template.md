# Plan Template

Use this structure when instructing Codex to generate plans.

---

```markdown
# Plan: [Task Name]

**Generated**: [Date]
**Estimated Complexity**: [Low/Medium/High]

## Overview
[Brief summary of what needs to be done and the general approach, including recommended libraries/tools]

## Prerequisites
- [Dependencies or requirements that must be met first]
- [Tools, libraries, or access needed]

## Phase 1: [Phase Name]
**Goal**: [What this phase accomplishes]

### Task 1.1: [Task Name]
- **Location**: [File paths or components involved]
- **Description**: [What needs to be done]
- **Dependencies**: [Task IDs this depends on, e.g., "None" or "1.2, 2.1"]
- **Complexity**: [1-10]
- **Test-First Approach**:
  - [Test to write before implementation]
  - [What the test should verify]
- **Acceptance Criteria**:
  - [Specific, testable criteria]

### Task 1.2: [Task Name]
[Same structure...]

## Phase 2: [Phase Name]
[...]

## Testing Strategy
- **Unit Tests**: [What to unit test, frameworks to use]
- **Integration Tests**: [API/service integration tests]
- **E2E Tests**: [Critical user flows to test end-to-end]
- **Test Coverage Goals**: [Target coverage percentage]

## Dependency Graph
[Show which tasks can run in parallel vs which must be sequential]
- Tasks with no dependencies: [list - these can start immediately]
- Task dependency chains: [show critical path]

## Potential Risks
- [Things that could go wrong]
- [Mitigation strategies]

## Rollback Plan
- [How to undo changes if needed]
```

---

## Task Guidelines

Each task must:
- Be specific and actionable (not vague)
- Have clear inputs and outputs
- Be independently testable
- Include file paths and specific code locations
- Include dependencies so parallel execution is possible
- Include complexity score (1-10)

Break large tasks into smaller ones:

**Bad:**
- "Implement Google OAuth"

**Good:**
- "Add Google OAuth config to environment variables"
- "Install and configure passport-google-oauth20 package"
- "Create OAuth callback route handler in src/routes/auth.ts"
- "Add Google sign-in button to login UI"
- "Write integration tests for OAuth flow"
