# Claude Code setup

The Toolbox installer copies the skill and its role profiles into the chosen skill directory. The skill can use those profiles as guidance with the host's delegation tools.

To register native Claude Code agents, copy the desired Markdown files from [the bundled agent definitions](../assets/claude/agents/) into `~/.claude/agents/` or a project's `.claude/agents/`. Review any same-name definitions before replacing them. Start a new session and check the agents with `/agents`.

If you want the bundled delegation rules applied across projects, review [delegation.md](../assets/claude/rules/delegation.md) and explicitly install it under `~/.claude/rules/`. The template may be copied to `~/.claude/templates/launch-profile.template.md` for the native launch workflow. Fill in your own `~/.claude/launch-profile.md` locally with the applicable machine, budget, and authorization rules.
