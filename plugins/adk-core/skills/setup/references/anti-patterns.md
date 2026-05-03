# `setup` — anti-patterns

- **Modifying `~/.zshenv` automatically.** Print the `export` lines; let the user paste them. The shell rc file is sensitive.
- **Auto-installing Homebrew, Docker, or any system tool.** Print the install command; let the user run it. These are big footguns (Homebrew bootstraps install path, sudo prompts, etc.).
- **Auto-minting API tokens.** Send the user to the vendor's UI with the URL.
- **Trying to start Docker for the user.** Print "open -a Docker" hint; don't run it.
- **Re-installing tools that are already present.** Idempotency means: detect, report, don't re-touch.
- **Skipping the `gh auth login` check.** A `gh` install without auth is a half-install for adk's purposes.
- **Asking 10 questions in one turn.** One at a time. Per the interaction contract.
- **Writing a raw secret into `~/.config/adk/*.md`.** Use `${ENV_VAR}` placeholders. The validator catches raw-token shapes (`github_pat_`, `sk-`, etc.).
- **Touching files outside `~/.config/adk/`.** This skill's blast radius is bounded to the meta-info folder + reading shell env.
- **Auto-overwriting a topic file the user has already edited.** Always show the diff and confirm.
- **Validating only at the end.** Validate after every topic edit so the user sees errors immediately.
