---
name: codex-plan
description: Create detailed implementation plan using Codex 5.3 with xhigh reasoning
user_invocable: true
argument_hint: "<what you want to plan>"
---

# Codex Plan Skill

You are being asked to create a detailed implementation plan using Codex. Your job is to:
1. Understand the user's planning request (shown below as `ARGUMENTS:`)
2. Ask clarifying questions using AskUserQuestion
3. Craft an excellent, detailed prompt for Codex
4. Execute Codex to generate and save the plan

**Always uses:** `gpt-5.3-codex` with `xhigh` reasoning
**Output:** `codex-plan.md` in current directory

---

## Step 1: Analyze the Request

The user's planning request appears at the end of this instruction as `ARGUMENTS: <request>`.

Identify:
- What is the core goal?
- What technology/domain is involved?
- What aspects are ambiguous or underspecified?
- What decisions would significantly impact the plan?

---

## Step 2: Ask Clarifying Questions (REQUIRED)

**Use AskUserQuestion tool** to ask 3-6 targeted questions before generating the plan.

Good clarifying questions:
- Narrow down scope and requirements
- Clarify technology choices
- Understand constraints (time, budget, team size)
- Identify must-haves vs nice-to-haves
- Uncover integration requirements
- Determine security/compliance needs

### Example Question Patterns

**For "implement auth":**
- What authentication methods? (email/password, OAuth, SSO, magic links)
- RBAC or just authenticated/unauthenticated?
- Backend stack? (Node/Express, Python/Django, etc.)
- Session storage? (Database, Redis, JWT stateless)
- Features needed? (password reset, email verification, 2FA)
- Compliance requirements? (SOC2, GDPR, HIPAA)

**For "build an API":**
- What resources/entities to manage?
- REST or GraphQL?
- Authentication method?
- Expected scale/traffic?
- Rate limiting, caching, versioning?

---

## Step 3: Gather Context

After getting answers:
- Read key files in the codebase if applicable
- Check existing architecture/patterns
- Note any existing plans or documentation

---

## Step 4: Craft the Codex Prompt

Create a detailed prompt that includes:
1. **Clear objective** - What plan needs to be created
2. **All requirements** - Everything learned from clarifying questions
3. **Constraints** - Technology choices, timeline, team size
4. **Context** - Relevant codebase info, existing patterns
5. **Plan structure** - Include the full template below
6. **Output instructions** - Write to `codex-plan.md` in current directory

**CRITICAL:** Tell Codex to NOT ask any clarifying questions - it has all the information it needs and should just write the plan and save the file.

### Example Codex Prompt

```
Create a detailed implementation plan for [TASK DESCRIPTION].

## Requirements
- [Requirement 1 from clarifying questions]
- [Requirement 2]
- [Requirement 3]
- NOT needed: [Things explicitly excluded]

## Plan Structure

Use this exact template structure:

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

### Task Guidelines
Each task must:
- Be specific and actionable (not vague)
- Have clear inputs and outputs
- Be independently testable
- Include file paths and specific code locations
- Include dependencies so parallel execution is possible
- Include complexity score (1-10)

Break large tasks into smaller ones:
- Bad: "Implement Google OAuth"
- Good:
  - "Add Google OAuth config to environment variables"
  - "Install and configure passport-google-oauth20 package"
  - "Create OAuth callback route handler in src/routes/auth.ts"
  - "Add Google sign-in button to login UI"
  - "Write integration tests for OAuth flow"

## Behavioral Constraints

<output_verbosity_spec>
- Default: 3-6 sentences or <=5 bullets for typical answers.
- Simple yes/no questions: <=2 sentences.
- Complex multi-step or multi-file tasks:
  - 1 short overview paragraph
  - then <=5 bullets tagged: What changed, Where, Risks, Next steps, Open questions.
- Avoid long narrative paragraphs; prefer compact bullets and short sections.
- Do not rephrase the user's request unless it changes semantics.
</output_verbosity_spec>

<design_and_scope_constraints>
- Implement EXACTLY and ONLY what the user requests.
- No extra features, no added components, no UX embellishments.
- Style aligned to the design system at hand.
- Do NOT invent colors, shadows, tokens, animations, or new UI elements unless requested or necessary.
- If any instruction is ambiguous, choose the simplest valid interpretation.
</design_and_scope_constraints>

<context_loading>
- Read ALL files that will be modified -- in full, not just the sections mentioned in the task.
- Also read key files they import from or that depend on them.
- Absorb surrounding patterns, naming conventions, error handling style, and architecture before writing any code.
- Do not ask clarifying questions about things that are answerable by reading the codebase.
</context_loading>

## Instructions
- Write the complete plan to a file called `codex-plan.md` in the current directory
- Do NOT ask any clarifying questions - you have all the information needed
- Be specific and actionable - include code snippets where helpful
- Follow test-driven development: specify what tests to write BEFORE implementation
- Identify task dependencies so parallel work is possible
- Just write the plan and save the file

Begin immediately.
```

---

## Step 5: Execute Codex (REQUIRED)

Run this exact command with your crafted prompt:

```bash
codex exec --full-auto --skip-git-repo-check \
  -c model=gpt-5.3-codex \
  -c model_reasoning_effort=xhigh \
  -c model_reasoning_summary=concise \
  --output-last-message /tmp/codex-plan-result.txt \
  "YOUR_CRAFTED_PROMPT_HERE"
```

Then show the results:
```bash
cat /tmp/codex-plan-result.txt
```

---

## Important Rules

1. **ALWAYS ask clarifying questions first** - Do not skip Step 2
2. **ALWAYS use gpt-5.3-codex with xhigh reasoning** - No exceptions
3. **ALWAYS tell Codex not to ask questions** - It should just execute
4. **ALWAYS use --full-auto flag**
5. **Output file**: `codex-plan.md` in current working directory

---

## Now Execute

The user's planning request is shown as `ARGUMENTS:` below. Analyze it and begin with Step 1.
