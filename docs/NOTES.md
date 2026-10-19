# Working notes

Facts about the workflow and the machines that are not in the spec, the decisions or the code.
Nothing about this project lives only in a session's memory: what a later session needs is here,
in `docs/DECISIONS.md` or in `docs/plans/`.

## Machines

- **Laptop (Windows 11 + WSL2 Ubuntu 24.04).** The Linux clone is `~/projects/VA-Rag` inside WSL;
  it is the working copy for everything that touches the environments. The Windows checkout at
  `C:\Users\notma\Desktop\VA-Rag` holds Windows-built `envs/*/.venv` that no longer match the
  committed Linux locks; it is used for editing and for the unit tests only (`uv run pytest -m
  "not envs"`). No GPU: `nvidia-smi` in WSL fails with "Failed to initialize NVML", so no model is
  served here. The isolation check passes (`isolation_status()` reports both limits).
- **PC (Windows + WSL2 Ubuntu with CUDA, RTX 5070 Ti, 16 GB).** Does all GPU work in a fresh
  session that has only this repository. See `docs/GPU_HANDOFF.md` once it exists.
- Clone inside the WSL filesystem (`~/`), never under `/mnt/c`: `/mnt/c` is slow and breaks
  file-mode assumptions.

## Tooling

- `uv` is installed per user at `~/.local/bin/uv` and is not on PATH in non-login shells; call it
  by that path or export PATH first. WSL here has uv 0.11.6 and installs CPython 3.11.15; the
  Windows side has uv 0.12 and CPython 3.11.17. `env verify` accepts any 3.11.x.
- From the Windows host, drive WSL with `wsl.exe -d Ubuntu-24.04 -e bash <script>` from
  PowerShell. Git Bash rewrites `/mnt/...` arguments as Windows paths, so it cannot pass WSL paths.
- Long Bash heredocs intermittently fail to parse ("unexpected EOF while looking for matching
  quote") and strings with `\n` escapes get unescaped in transit. Write anything longer than a few
  lines to a file and run the file; use the Edit tool for exact edits.
- Git line endings: `.gitattributes` forces LF; every writer of a hashed data file passes
  `newline="\n"`.

## cpu_tiny model server

`bash scripts/serve_cpu_tiny.sh` installs llama.cpp build b11723 under `~/.local/llama.cpp` and
starts `llama-server` on `:8080` with the pinned Q8_0 GGUF of Qwen2.5-Coder-0.5B-Instruct
(downloaded by the server into `~/.cache/llama.cpp`). `bash scripts/serve_cpu_tiny.sh stop` stops
it. `varag smoke --offline` runs ten dev instances through every method on it when it is up;
`configs/models.yaml` marks the backend `report: false`, so its runs never appear in results. On
this laptop (8 threads) the ten-instance smoke run took about four minutes.

## Data flow between the two checkouts

Code is edited on Windows and committed there; environment-dependent rebuilds run in WSL and are
committed there, then handed back with `git push win HEAD:refs/heads/linux-build` (the WSL clone
has a `win` remote pointing at the Windows checkout) and fast-forwarded on Windows. Both push to
`origin` (GitHub, branch `main`). The WSL clone has no GitHub credentials; pushes go from Windows.

## Rebuild order after a change

Locks or pins → `env build --relock`, then every lock-hashed artifact: `inventory build`,
`inventory audit`, `corpus build`, `bench probe`, `bench validate`. Diff rule or extractor change →
`inventory build` onward. The corpus example cache is keyed by lock hash and example hash, so a
rebuild re-runs only what changed.
