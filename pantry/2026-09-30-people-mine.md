# People mine: Claude Code Game Dev

What people who use the product said in its own public places: issues, issue comments, discussions, pull requests, and forks that changed something. Optional third pantry source; a product with no outside voices yet leaves the Hits table empty and says so.

## How this fills

1. List the product's own repos (the kitchen law names them).
2. Read what people outside the maintainers wrote since the last run: issues (the `feedback` label first), issue comments, discussions and their comments, pull requests, and forks with commits ahead of the default branch.
3. One row per voice. Quote a short snippet and link the exact issue, comment, discussion, PR or commit. Say whether they gave credit consent when the source has a consent box.
4. Tag each row with the capability it is about, in the same words as the competitor map's matrix, so the queue can cite it next to competitor and X rows.
5. Never count stars as feedback, never infer sentiment the person did not state, never paraphrase a number. Maintainers' own issues are not voices.
6. Save as `YYYY-MM-DD-people-mine.md` beside the other dated files (keep this TEMPLATE).

Repo read: [HermeticOrmus/claude-code-game-development](https://github.com/HermeticOrmus/claude-code-game-development). This is the first run, so everything public was read.

## Hits

| Repo | Kind (bug/feature/question/praise/contribution) | Snippet | Link | Theme (matrix capability) | Credit consent |
|------|--------------------------------------------------|---------|------|---------------------------|----------------|
| claude-code-game-development (fork by air-nakamoto) | contribution | "Add Japanese usage guide (README.ja.md)" and "Provides a Japanese-language overview of how to use the repository" (commit message); the file opens "このドキュメントは、本リポジトリ（claude-code-game-development）の使い方を日本語で解説するものです。" | https://github.com/air-nakamoto/claude-code-game-development/commit/f6a287b71c61d4a155fbc4dd3b62fdf1000eadae | Translations (non-English docs) | not asked (a fork commit has no consent box) |

## Read log (what we read)

- Repo metadata (GitHub API `repos/HermeticOrmus/claude-code-game-development`): 11 forks, Discussions on, 1 open issue. Stars are not feedback and are not counted here.
- Issues and pull requests, all states (`issues?state=all`): #1 "Release v2.0.0" (closed), #2 "v2.0.0: rename marketplace, credit wshobson/agents, add 20 game plugins" (merged PR), #3 "Open the kitchen: pantry, Menu, contributor door" (open). All three by the maintainer, so no voices. #4 "Add frontmatter to the 67 command files that lack it" (open, `good first issue`) was opened by the maintainer during this run; not a voice either. No issue carries the `feedback` label yet.
- Issue comments (`issues/comments`): 1, by the maintainer on #1. No outside comments.
- Pull request review comments (`pulls/comments`): none.
- Discussions (GraphQL `discussions`): 0 threads. Categories exist: Announcements, General, Ideas, Polls, Q&A, Show and tell.
- Forks (`forks`), each branch compared with `main` through the compare API:
  - air-nakamoto: branch `claude/game-dev-repository-017nfLKbbabCj73wES1Mvkpb` is 2 commits ahead (the commit above and its merge from `claude/add-japanese-docs-TZ0Ug`); one file added, `README.ja.md`, 205 lines. Recorded as the row above.
  - ofmiceandcam98-eng: two branches with commits ahead (2 and 1) that replace the repo's content with a different project. Read; not feedback on this repo, so no row.
  - The other 9 forks: one branch each, 0 commits ahead of `main`. Nothing to read.
