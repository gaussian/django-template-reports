# django-template-reports — agent guide

Generates reports (PPTX/XLSX) from template files that are flexibly populated
using the Django ORM, without hard-coding. Published to PyPI. The actual
template-rendering engine lives in the sibling package `office-templates`
(https://github.com/gaussian/python-office-templates); this repo is the Django
integration layer (models, admin, signals) on top of it.

## Repo shape

- Source: `template_reports/`
- Tests: `tests/` (pytest-django) — `uv run --all-extras pytest`. **Note:** this
  repo currently has no test suite — the template-rendering tests moved to
  `office-templates` when its logic did (see commit `05453c3`). The `test` CI
  job tolerates zero collected tests (pytest exit code 5) so it doesn't block
  on this pre-existing gap; a real regression still fails the job.
- Lint + format: `uv run --all-extras ruff check template_reports/ tests/` and
  `ruff format --check template_reports/ tests/`
- Default working branch: `develop`. Releases flow `develop` → `main`.

## Opening PRs & versioning

`main` is protected: PRs only, and checks (`lint`, `test`) must pass to merge.
The version is a static string in `pyproject.toml`, `template_reports/__init__.py`,
and `uv.lock` and is **not** bumped automatically on merge — it must be bumped
deliberately, or no release is cut. Publishing to PyPI is automatic once a
`develop` → `main` PR merges.

**Follow the `create-merge-pr` skill** (`.agents/skills/create-merge-pr/`) for the
full PR workflow, including when and how to bump the version.
