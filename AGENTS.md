# Nestor Agent repository instructions

## Track repository work in GitHub Projects

Use the [NESTOR AGENT board](https://github.com/users/tranvanhuy-hichan/projects/1) and an issue in `tranvanhuy-hichan/ai-nestor-agent` for every repository task, including investigations, reviews, code, and documentation.

1. Before starting, read the board and search repository issues for the task. Use the issue the user supplied if it covers the work. Otherwise reuse the matching open issue. If a closed issue covers the same unfinished work, reopen it when appropriate. Create an issue only when there is no suitable one. Include the goal, scope, and acceptance criteria.
2. Read the issue and its comments to recover prior decisions and check whether someone is already working on it. Coordinate on the existing issue if work overlaps. Add the issue to the board if it is missing. Set its status to `In progress` when you start. Verify that the project shows the issue and the intended status.
3. Record meaningful milestones on the issue, including decisions that affect the outcome, blockers, and handoffs. Before ending the task, post a concise summary of what changed, checks run and their results, any remaining work, and links to relevant commits or PRs when available. Keep secrets and private material out of the public repository's issues and comments.
4. Put work awaiting review or merge in `In review` and keep the issue open. Set `Done` and close the issue when the acceptance criteria are met and any required merge has landed. Use `Backlog` for deferred work, `Ready` for work queued to start, and `Bug` for bugs awaiting triage. Verify the final status and include the issue link in your handoff.
5. If GitHub is unavailable or access is missing, report the failed operation. Keep the issue or project URL if known and preserve a concise handoff in the task response for later sync. When access returns, search again before creating anything and add the missing history to the matching issue.

Use an available GitHub integration or the GitHub CLI. For example, with `ISSUE_URL` set to the existing or newly created issue URL:

```bash
gh project item-list 1 --owner tranvanhuy-hichan --format json
gh issue list -R tranvanhuy-hichan/ai-nestor-agent --state all --search "task keywords"
gh issue view "$ISSUE_URL" --comments
gh project item-add 1 --owner tranvanhuy-hichan --url "$ISSUE_URL"
gh project item-edit 1 --owner tranvanhuy-hichan --url "$ISSUE_URL" --field Status --value "In progress"
```
