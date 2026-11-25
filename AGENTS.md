# Project notes — J.A.R.V.I.S. (Termux edition)

Pure-stdlib Python, no dependencies. The whole app lives in `jarvis/` (package)
with the entry point `jarvis.py` at the repo root.

`/workspace/jarvis` is itself the git repo root, and it is what gets pushed to
GitHub (`serenitynightmarebiz-coder/J.A.R.V.I.S-TERMUX`, branch `main`). So all
paths in the README and CI are root-relative: `tests/`, `scripts/`, `jarvis.py`.
CI lives in `.github/workflows/tests.yml` here — GitHub only runs workflows from
the repo root, so it must stay at this level.

## Run & verify (no phone needed)

```bash
python3 -m unittest discover -s tests      # full suite, offline
JARVIS_MOCK=1 python3 jarvis.py --selftest # tools against the fake device
JARVIS_MOCK=1 python3 jarvis.py --diag     # health report (JSON)
python3 -m compileall -q jarvis jarvis.py tests
```

`JARVIS_MOCK=1` is required for `--selftest`/`--diag` off-device, otherwise the
Termux:API probes fail.

## Pitfalls

- Pushing: `origin` has no stored credentials, so a bare `git push origin main`
  hangs forever. The user supplies a fresh GitHub PAT in chat (they expire in
  about an hour); push with
  `GIT_TERMINAL_PROMPT=0 git push https://serenitynightmarebiz-coder:<TOKEN>@github.com/serenitynightmarebiz-coder/J.A.R.V.I.S-TERMUX.git main:main`.
  Never commit or record the token itself.
- On 2025-11-25 the remote history was force-replaced (`--force-with-lease`)
  with this clean root layout: the old remote had every file duplicated under
  `jarvis/` (`jarvis/jarvis/`, `jarvis/tests/`, `jarvis/scripts/`). If remote
  and local ever diverge again, diff first — the local tree is the tested one.
- `config.json` is gitignored and not committed; the code falls back to built-in
  defaults, and `install.sh` copies `config.example.json`. Never commit it — it
  can hold an API key.
- `data/` and `logs/` are gitignored runtime state, auto-created via `mkdir(parents=True)`
  at runtime. `--selftest` recreates `data/backups` and `data/selftest`; delete
  them before committing if they show up.
- `.revyl/` is PolyDev session data — gitignored, never commit it.
- The sandbox shell is busybox `ash`: no heredocs, no `grep --include`/`--exclude-dir`.
  Use `search_grep` for searching and `write_file` for multi-line files.
- README numbers are asserted by hand: 83 tools, 102 tests, 13 providers. Update
  them together if the registry or suite grows.

## Layout

`jarvis/tools/` holds the 83 registered capabilities (registry decorator →
JSON schema). `agent.py` is the model→tool→model loop; `llm.py` the provider
abstraction; `gate.py` the wake-word rules; `service.py` the background daemon.
