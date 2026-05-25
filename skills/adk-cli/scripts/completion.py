"""completion.py — `adk completion <shell>` emits a static completion script.

Usage:
  adk completion bash > ~/.local/share/bash-completion/completions/adk
  adk completion zsh  > ~/.zsh/completions/_adk  (then `compinit` once)
  adk completion fish > ~/.config/fish/completions/adk.fish

install.py also wires this up automatically when --install-completions is passed.
"""
from __future__ import annotations

import argparse
import sys
import textwrap


# Top-level subcommands and their nested subcommands.
SUBCMDS = {
    "skill-run":   [],
    "skill-preflight": [],
    "pr-sync":    [],
    "pr-scan":    [],
    "pr":         ["open", "context-refresh", "merge-status", "merge"],
    "pr-queue":   ["list", "show", "add", "update", "clean", "ready-to-merge",
                   "release", "get-next", "remind"],
    "pr-task":    ["prepare", "info", "list", "validate", "clean-orphans"],
    "repo":       ["add", "update", "list", "branch", "migrate"],
    "doctor":     [],
    "pr-review-all": [],
    "pr-review":  [],
    "completion": ["bash", "zsh", "fish"],
}

# Top-level + commonly-used flags. Per-subcommand flags omitted for brevity —
# `--help` always tab-completes via the binary itself.
COMMON_FLAGS = ["-y", "--yes", "--help", "-h"]


def emit_bash() -> str:
    top = " ".join(SUBCMDS.keys())
    # Build a case statement for nested subcommands.
    nested_cases = []
    for cmd, subs in SUBCMDS.items():
        if not subs:
            continue
        nested_cases.append(f'        {cmd})\n            COMPREPLY=( $(compgen -W "{" ".join(subs)}" -- "$cur") )\n            ;;')
    nested_case_block = "\n".join(nested_cases) if nested_cases else "        *) ;;"
    return textwrap.dedent(f"""\
        # adk completion (bash). Source: `adk completion bash`.
        _adk_complete() {{
            local cur prev words cword
            _init_completion || return

            if [[ $cword -eq 1 ]]; then
                COMPREPLY=( $(compgen -W "{top} --help -h" -- "$cur") )
                return
            fi
            local subcmd="${{words[1]}}"
            if [[ $cword -eq 2 ]]; then
                case "$subcmd" in
        {nested_case_block}
                esac
                return
            fi
            # Dynamic: `adk repo update <TAB>` → completes from `adk repo list --names-only`.
            if [[ "$subcmd" == "repo" && "${{words[2]}}" == "update" && $cword -eq 3 ]]; then
                local names
                names=$(adk repo list --names-only 2>/dev/null)
                COMPREPLY=( $(compgen -W "$names --all" -- "$cur") )
                return
            fi
            # Dynamic: `adk pr-queue {{show,update,release}} <TAB>` → URLs from the queue.
            if [[ "$subcmd" == "pr-queue" && $cword -eq 3 ]]; then
                local nested="${{words[2]}}"
                case "$nested" in
                    show|update|release)
                        local urls
                        urls=$(adk pr-queue list --urls-only 2>/dev/null)
                        local extra=""
                        [[ "$nested" == "update" ]] && extra="--all"
                        COMPREPLY=( $(compgen -W "$urls $extra" -- "$cur") )
                        return
                        ;;
                esac
            fi
            # Dynamic: `adk pr-task {{prepare,info}} <TAB>` → URLs from the queue.
            if [[ "$subcmd" == "pr-task" && $cword -eq 3 ]]; then
                local nested="${{words[2]}}"
                case "$nested" in
                    prepare)
                        local urls
                        urls=$(adk pr-queue list --urls-only 2>/dev/null)
                        COMPREPLY=( $(compgen -W "$urls --all --rebuild --detailed --deep" -- "$cur") )
                        return
                        ;;
                    info|validate)
                        local urls
                        urls=$(adk pr-queue list --urls-only 2>/dev/null)
                        COMPREPLY=( $(compgen -W "$urls" -- "$cur") )
                        return
                        ;;
                esac
            fi
            COMPREPLY=( $(compgen -W "{" ".join(COMMON_FLAGS)}" -- "$cur") )
        }}
        complete -F _adk_complete adk
        """)


def emit_zsh() -> str:
    nested = []
    for cmd, subs in SUBCMDS.items():
        if not subs:
            continue
        items = " ".join(f"{s}:'{s}'" for s in subs)
        nested.append(f"        {cmd}) _values '{cmd} subcommand' {items} ;;")
    nested_block = "\n".join(nested) if nested else "        *) ;;"
    top_items = " ".join(f"{c}:'{c}'" for c in SUBCMDS)
    return textwrap.dedent(f"""\
        #compdef adk
        # adk completion (zsh). Source: `adk completion zsh > $fpath[1]/_adk` then `compinit`.
        _adk() {{
            local context state line
            if (( CURRENT == 2 )); then
                _values 'adk subcommand' {top_items}
                return
            fi
            local subcmd="${{words[2]}}"
            if (( CURRENT == 3 )); then
                case "$subcmd" in
        {nested_block}
                esac
                return
            fi
            # Dynamic: `adk repo update <TAB>` → completes from `adk repo list --names-only`.
            if [[ "$subcmd" == "repo" && "${{words[3]}}" == "update" && $CURRENT -eq 4 ]]; then
                local -a names
                names=("${{(@f)$(adk repo list --names-only 2>/dev/null)}}")
                _values 'repo' '--all[update every indexed repo]' $names
                return
            fi
            # Dynamic: `adk pr-queue {{show,update,release}} <TAB>` → URLs from the queue.
            if [[ "$subcmd" == "pr-queue" && $CURRENT -eq 4 ]]; then
                local nested="${{words[3]}}"
                case "$nested" in
                    show|update|release)
                        local -a urls
                        urls=("${{(@f)$(adk pr-queue list --urls-only 2>/dev/null)}}")
                        if [[ "$nested" == "update" ]]; then
                            _values 'pr-queue update' \\
                                '--all[refresh every non-terminal row]' $urls
                        else
                            _values "pr-queue $nested" $urls
                        fi
                        return
                        ;;
                esac
            fi
            # Dynamic: `adk pr-task {{prepare,info}} <TAB>` → URLs from the queue.
            if [[ "$subcmd" == "pr-task" && $CURRENT -eq 4 ]]; then
                local nested="${{words[3]}}"
                case "$nested" in
                    prepare)
                        local -a urls
                        urls=("${{(@f)$(adk pr-queue list --urls-only 2>/dev/null)}}")
                        _values 'pr-task prepare' \\
                            '--all[prepare every non-merged queue row]' \\
                            '--rebuild[force full re-index]' \\
                            '--detailed[use bge-m3 embeddings]' \\
                            '--deep[record deep model intent]' $urls
                        return
                        ;;
                    info|validate)
                        local -a urls
                        urls=("${{(@f)$(adk pr-queue list --urls-only 2>/dev/null)}}")
                        _values "pr-task $nested" $urls
                        return
                        ;;
                esac
            fi
            _values 'flags' {" ".join(f"'{f}'" for f in COMMON_FLAGS)}
        }}
        compdef _adk adk
        """)


def emit_fish() -> str:
    lines = ["# adk completion (fish). Source: `adk completion fish > ~/.config/fish/completions/adk.fish`."]
    # Top-level subcommands.
    for cmd in SUBCMDS:
        lines.append(f"complete -c adk -n '__fish_use_subcommand' -a {cmd}")
    # Nested.
    for cmd, subs in SUBCMDS.items():
        if not subs:
            continue
        for s in subs:
            lines.append(f"complete -c adk -n \"__fish_seen_subcommand_from {cmd}\" -a {s}")
    # Dynamic: `adk repo update <TAB>` → repo names + `--all`.
    lines.append(
        "complete -c adk -n \"__fish_seen_subcommand_from repo; "
        "and __fish_seen_subcommand_from update\" "
        "-a \"(adk repo list --names-only 2>/dev/null) --all\""
    )
    # Dynamic: `adk pr-queue {show,update,release} <TAB>` → PR URLs from the queue.
    for nested, extra in (("show", ""), ("update", " --all"), ("release", "")):
        lines.append(
            f"complete -c adk -n \"__fish_seen_subcommand_from pr-queue; "
            f"and __fish_seen_subcommand_from {nested}\" "
            f"-a \"(adk pr-queue list --urls-only 2>/dev/null){extra}\""
        )
    # Dynamic: `adk pr-task {prepare,info} <TAB>` → PR URLs from the queue.
    lines.append(
        "complete -c adk -n \"__fish_seen_subcommand_from pr-task; "
        "and __fish_seen_subcommand_from prepare\" "
        "-a \"(adk pr-queue list --urls-only 2>/dev/null) --all --rebuild --detailed --deep\""
    )
    for nested in ("info", "validate"):
        lines.append(
            f"complete -c adk -n \"__fish_seen_subcommand_from pr-task; "
            f"and __fish_seen_subcommand_from {nested}\" "
            f"-a \"(adk pr-queue list --urls-only 2>/dev/null)\""
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk completion",
                                 description="Emit a shell completion script.")
    ap.add_argument("shell", choices=("bash", "zsh", "fish"))
    ap.add_argument("-y", "--yes", action="store_true")
    args = ap.parse_args(argv)

    if args.shell == "bash":
        print(emit_bash())
    elif args.shell == "zsh":
        print(emit_zsh())
    else:
        print(emit_fish())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
