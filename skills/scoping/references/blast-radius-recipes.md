# `scoping` — blast-radius recipes (per stack)

## TypeScript / React

```sh
rg -l 'DataGrid' --type=ts --type=tsx
rg -l 'csvExport|exportCsv' --type=ts
fd -e tsx --search 'DataGrid'
```

## Python

```sh
rg -l 'def export_csv|class DataGrid' --type=py
```

## Go

```sh
rg -l 'func ExportCSV|type DataGrid' --type=go
```

## Node API endpoint

```sh
rg -l "router\\.(get|post)\\(.*'/api/export" --type=ts
```

## CSS / styles

```sh
rg -l '\\.data-grid' --type=css --type=scss
```

## Always-also-include (rule of thumb)

When a file is in blast radius, also pull:
- Its test file (`<name>.test.ts`, `<name>.spec.ts`, `tests/<name>_test.py`).
- Its type file (`<name>.d.ts`, `types/<name>.ts`).
- Its story / preview (`<name>.stories.tsx`).
- Its CSS / styles file if a component.
