# Plan

Use this template to file an executable unit of work as a sub-issue of a parent Issue (User Story, Bug, or Tech Task). A Plan is the atomic chunk that produces one or more PRs and closes when its scope is delivered. The parent Issue closes when all its Plans close.

## Parent Issue

Issue number of the parent (User Story / Bug / Tech Task). After creation, link this Plan as a native sub-issue of the parent via `gh api -X POST repos/{owner}/{repo}/issues/{parent}/sub_issues -F sub_issue_id={this_id}`.

<!-- placeholder: e.g. #140 -->

## Why

What problem does this Plan close inside the parent's scope? Tie it to the parent's Definition of Done.

<!-- placeholder: e.g. Without renaming simple-task → tech-task, every subsequent Plan that depends on the new template name is blocked. -->

## What

Concrete deliverable. What files change? What stays out (handled by sibling Plans)?

<!-- placeholder:
- Rename .github/ISSUE_TEMPLATE/simple-task.yml → tech-task.yml
- Rename framework/templates/contributing_templates/simple-task.md → tech-task.md
- Add bug.yml and plan.yml templates
- Out of scope (sibling Plans): governance lexis rewrite, kata updates
-->

## How

Implementation approach + Definition of Done. Concrete steps, files involved, success criteria.

<!-- placeholder:
- Branch tech/{N}-rename-templates-add-bug-plan
- git mv preserves history
- Add status: todo to labels: array of every non-Epic template
- DoD: gh issue create against tech-task template carries status: todo automatically; bug + plan templates render in GitHub UI
-->

Steps + Definition of Done:

## Estimated PRs

Select one:
- **1** — single atomic PR
- **2–3** — small chain, possibly stacked
- **4–6** — medium chain; consider further decomposition
- **7+** — too large; re-decompose into more Plans

## Additional Context

Dependencies on sibling Plans, blocking external work, links to designs/docs, or any other relevant context (optional).

---

> After creation, link this Plan as a sub-issue of the Parent via `gh api -X POST repos/{owner}/{repo}/issues/{parent}/sub_issues -F sub_issue_id={this_id}`.
