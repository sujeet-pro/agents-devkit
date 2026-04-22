# `setup` — output format

```
[adk:setup] platform=<darwin> mode=<auto|fix> auto=<on|off>

cli tools:
  brew     <present|installed-now> (<version>)
  gh       <present|installed-now> (<version>) authed=<ok|missing>
  jq       <present|installed-now> (<version>)
  fd       <present|installed-now> (<version>)
  ripgrep  <present|installed-now> (<version>)
  fzf      <present|installed-now> (<version>)
  claude   <present|installed-now> (<version>)
  node     <present|installed-now> (<version>)

env vars (~/.zshenv):
  <VAR>    <present|MISSING> [— add: export <VAR>="..."]
  ...

mcp servers (claude mcp ls):
  <name>   <installed|skipped (env missing)|present>
  ...

doctor: <N> warnings, <M> errors
  - <warning text>
  - <error text>

next:
  - <one-line action> (or "ready — run `/adk:auto <prompt>`")
```
