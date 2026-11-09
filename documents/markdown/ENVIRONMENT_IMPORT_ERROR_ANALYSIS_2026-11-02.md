# Analysis: `ModuleNotFoundError: No module named 'quantfin'`

Date: 2 November 2026 (Singapore)

Scope: analysis of the supplied terminal screenshot against this repository. Only this Markdown report has been created. No application, test, dependency, README, Git branch, or environment changes have been made; no installation, pull, or tests have been executed for this review.

## 1. Diagnosis

The visible error occurs while pytest imports test modules, before their test functions execute:

```text
python -m pytest tests/leakage -v -rx
...
from quantfin.cross_market.panel import _scheduled_features
ModuleNotFoundError: No module named 'quantfin'
...
Interrupted: 3 errors during collection
```

The most likely cause is that the local project has not been installed into the Python environment running pytest, or that an earlier editable installation points to another checkout. This repository uses a **`src/` package layout**, so running Python from the repository root does not by itself put `src/quantfin/` on the import path. The normal development setup includes installing the local project with `python -m pip install -e .`. This is consistent with the [Python Packaging User Guide's explanation of the src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).

The screenshot is from a MacBook using a pyenv Python 3.12.15 installation. It does **not** establish a Mac-versus-Windows or Apple-Silicon-versus-Intel incompatibility. It also does not establish that the friend is on an old branch. Both the installation and repository revision need checking before attributing the failure to either.

Collection errors are not failed leakage assertions. No conclusion about the model's leakage controls can be drawn from this output.

## 2. What is `quantfin`?

`quantfin` is the project's **custom local Python package**, defined in this repository. It is not a separate external finance library that the friend needs to find online.

| Name | Meaning in this project |
|---|---|
| `project2QuantFin` | The repository/project directory. Its directory name is not the Python import name. |
| `project2-quantfin` | The distribution name declared in `pyproject.toml`; use this name with `python -m pip show project2-quantfin`. |
| `quantfin` | The importable package under `src/quantfin/`; used by statements such as `from quantfin.cross_market.panel import ...`. |
| `quantfin` command | A command-line entry point declared as `quantfin = "quantfin.cli:main"`. It is created when the project is installed. |
| `python -m quantfin` | Runs the installed package's `__main__.py` using the chosen Python interpreter. |

The package contains the project's data loading, cleaning, feature engineering, cross-market timing, model training, backtesting, tracking, and evaluation modules.

Relevant layout:

```text
project2QuantFin/
├── pyproject.toml
├── requirements.txt
├── src/
│   └── quantfin/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── cross_market/
│           ├── panel.py
│           ├── timing.py
│           └── experiments.py
└── tests/
```

Relevant packaging declarations already exist:

```toml
[project]
name = "project2-quantfin"
requires-python = ">=3.10"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

**Do not run `pip install quantfin` as the solution.** That asks a package index for a distribution with that name, rather than installing this repository. The intended command is `python -m pip install -e .` from the directory containing this project's `pyproject.toml`.

## 3. Could an old branch or missing `git pull` cause this?

**Yes, potentially, but updating Git alone is not a reliable fix for this exact error.**

Git determines which source files are present. The Python environment determines which packages Python can import. These are separate pieces of the setup.

| Situation | Could it explain this error? | Appropriate response |
|---|---|---|
| Correct branch and files, but project never installed | Yes; this is the leading explanation. | Install this checkout into the interpreter used for pytest. |
| Only `pip install -r requirements.txt` was run | Yes. The current requirements file lists external dependencies and does not install the local project. | Also install the local project with `-e .`. |
| An older branch lacks the package or packaging declarations | Yes, if confirmed by inspecting that checkout. | Align the intended source revision, then install it. |
| Tests were copied from a newer revision into older application code | Possible. The first error may be package discovery; missing functions can appear after fixing imports. | Compare the application and test revisions together. |
| `git pull` updated the current branch, but it is not the agreed project branch | Possible. A pull does not automatically switch branches. | Compare branch, remote, and commit with the agreed source. |
| The repository was moved after an editable install | Yes, potentially. The environment may still refer to the earlier checkout. | Reinstall from the current directory using the same interpreter. |
| Files were updated but the active Python environment was not recreated/updated | Possible. Git does not install packages or dependencies. | Check the interpreter and reinstall the checkout as necessary. |

### A concrete revision discrepancy

In the checkout inspected for this report, branch `v5-ritik`, commit `2ab3007b`, the `tests/leakage/` directory and the screenshot's `test_scheduled_availability.py` and `test_updated_pipeline.py` files are absent. The local `panel.py` does define `_scheduled_features`.

This establishes a **difference in working-tree contents**, not which person's version is older or correct. The friend's tests may be new local additions, on another branch, or from another commit. Do not delete those tests or switch branches solely because they differ.

The README currently recommends `unittest` discovery for the tests shipped in this checkout; the friend is using pytest for an additional leakage suite. Pytest itself is not declared in this checkout's core dependencies. In the screenshot it is already installed and running, so its absence is not the immediate problem.

Compare the following outputs on both machines. These commands are read-only and do not update or switch branches:

```bash
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short
git log -1 --oneline
git ls-files pyproject.toml src/quantfin tests
```

The full commit hash is a better comparison than branch name alone. The same branch name can point to different commits on different computers. Untracked or modified tests also need accounting for, even if the commit hashes match. Do not share credential-bearing remote URLs in public logs.

No `git pull`, branch switch, reset, or deletion is prescribed before reviewing those differences. If synchronization is needed, preserve the friend's local work and align to the explicitly agreed branch/commit first.

## 4. Ranked probable causes and checks

| Priority | Probable cause | Evidence / limit | Check |
|---|---|---|---|
| 1 | Local project missing from the test interpreter's environment | `quantfin` cannot be found; the project uses `src/`. | Inspect `pip show project2-quantfin` and `find_spec('quantfin')`. |
| 2 | Installation and testing used different Python interpreters | A `.venv` prompt is useful but does not prove which executable runs. | Print `sys.executable`; use the explicit virtual-environment Python path. |
| 3 | Only third-party dependencies were installed | `requirements.txt` has no `-e .` or equivalent local-project entry. | Ask which setup commands completed successfully; inspect installation metadata. |
| 4 | Editable install refers to a moved or different checkout | Editable installations depend on the local source location. | Check the package file path and pip's editable-project location. |
| 5 | Wrong branch, mismatched test revision, incomplete copy, or wrong nested project directory | The screenshot's tests differ from this checkout; screenshot does not identify the exact commit. | Compare Git outputs and verify `pyproject.toml` and `src/quantfin/__init__.py` exist in the working directory. |
| 6 | Native architecture or compiled dependency problem | Not supported by this traceback. | Investigate only if a later error reports a binary load, DLL, ABI, or incompatible architecture failure. |

The pytest hint about valid Python module names is generic collection guidance. The specific exception underneath it—missing `quantfin`—is more diagnostic. Spaces in the displayed directory path are not, by themselves, evidence of a broken package name; quote such paths in shell commands.

A traceback under `~/.pyenv/versions/3.12.15/lib/python3.12/importlib/` is also not proof that the virtual environment was bypassed. Virtual environments can use the base interpreter's standard library. Check `sys.executable`, `sys.prefix` and `sys.base_prefix` instead.

## 5. Read-only diagnostics for the friend

Run from the actual project root: the directory containing `pyproject.toml` and `src/quantfin/`. These commands inspect the environment; they do not install anything or run the tests.

```bash
python -c "import sys,platform; print('executable:',sys.executable); print('prefix:',sys.prefix); print('base_prefix:',sys.base_prefix); print('version:',sys.version); print('platform:',platform.platform()); print('machine:',platform.machine())"
python -m pip --version
python -m pip show project2-quantfin
python -c "from pathlib import Path; print('cwd:',Path.cwd()); print('pyproject:',Path('pyproject.toml').is_file()); print('local package:',Path('src/quantfin/__init__.py').is_file())"
python -c "import importlib.util; print(importlib.util.find_spec('quantfin'))"
```

Interpretation:

- Missing distribution metadata plus `find_spec(...)` returning `None` strongly supports a missing installation in that environment.
- If the local package file is absent, first resolve the checkout/root-directory problem.
- If distribution metadata exists but no import spec is found, check for a stale editable installation or a different interpreter.
- If the import spec resolves elsewhere, inspect whether that is another clone or an unrelated installed package.

## 6. Recommended repair: same local install on either platform

These are **proposed commands for the friend to run after review**, not changes executed for this report. They install into an existing virtual environment. Run them from the project root and only continue after each command succeeds.

The [pip documentation](https://pip.pypa.io/en/stable/topics/local-project-installs/) describes editable installation of a local project. It makes the local source available to the Python interpreter associated with that pip invocation. It does not move or rename the source package.

### macOS: existing `.venv`

Using the explicit executable avoids ambiguity from activation, pyenv, or another shell environment:

```bash
./.venv/bin/python -m pip install -e .
./.venv/bin/python -m pip check
./.venv/bin/python -c "import quantfin; print(quantfin.__file__)"
./.venv/bin/python -c "from quantfin.cross_market.panel import _scheduled_features; print('panel import OK')"
./.venv/bin/python -m pytest --collect-only tests/leakage -q
./.venv/bin/python -m pytest tests/leakage -v -rx
```

Expected package path: this checkout's `src/quantfin/__init__.py`. Collection should proceed without the missing-package error; that does not guarantee every test assertion will pass.

If that explicit Python reports `No module named pytest`, install the test runner into the same environment before repeating collection:

```bash
./.venv/bin/python -m pip install pytest
```

### Windows PowerShell: existing `.venv`

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import quantfin; print(quantfin.__file__)"
.\.venv\Scripts\python.exe -c "from quantfin.cross_market.panel import _scheduled_features; print('panel import OK')"
.\.venv\Scripts\python.exe -m pytest --collect-only tests/leakage -q
.\.venv\Scripts\python.exe -m pytest tests/leakage -v -rx
```

If pytest is absent:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

These explicit paths do not require running PowerShell's activation script or changing its execution policy.

If the install fails because the packaging tools are too old, upgrade them in the same environment and retry the local installation. Do not assume the install succeeded if its output ended in an error:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

Use the explicit macOS or Windows virtual-environment executable in place of `python` here if interpreter selection is uncertain.

### If `tests/leakage/` does not exist

Do not create an empty directory to satisfy the command. First reconcile the intended test revision. For the tests actually shipped in the inspected checkout, the README's command is:

```bash
python -m unittest discover -s tests -v
```

That is not a substitute for the friend's additional leakage tests; it only runs the suite present in this checkout. Use the chosen environment's Python and confirm the number of tests discovered.

## 7. Platform and Python-version assessment

| Question | Finding |
|---|---|
| Does the screenshot show Windows? | No. It shows a MacBook shell and macOS paths. |
| Does it identify Apple Silicon versus Intel? | No reliable architecture identification is visible. Use `platform.machine()` to check. |
| Is Python 3.12 intrinsically outside this project's declared range? | No. Packaging declares Python >=3.10, and the README recommends 3.10–3.12. This does not certify every dependency combination. |
| Should the friend downgrade Python immediately? | No. Fix package discovery first. A version change is not justified by this error alone. |
| Is a copied `.venv` portable between machines? | Do not rely on it. Recreate environments locally; interpreter paths and compiled dependencies can differ. |
| Can macOS and Windows encounter the same missing-package error? | Yes. Both need the local project installed into the Python environment used for testing. |
| Could compiled dependency compatibility matter later? | Yes, but that would require a separate diagnosis based on the actual subsequent error. |

Matching code and supported Python versions is useful for replication. Exact numerical equivalence across machines also depends on resolved dependency versions and numerical libraries. The broad dependency ranges in this repository are not a fully locked cross-platform environment. That is a future reproducibility consideration, not evidence explaining this screenshot.

## 8. Possible repository improvements for discussion only

No changes in this section have been implemented.

| Proposed improvement | Benefit | Scope / caution |
|---|---|---|
| Add a visible local-package import check immediately after installation in the README | Catches missing or wrong-checkout installs before long runs. | Keep the existing `src/` layout. |
| Declare a test/development dependency extra for pytest if the added suite becomes part of the shared repository | Makes the extra runner an explicit setup requirement. | Current shipped tests use unittest; agree the intended suite first. |
| Document the difference between `project2-quantfin`, `quantfin` and the repository name | Prevents attempts to install an unrelated finance package. | Documentation only. |
| Add CI using agreed Python versions on macOS and Windows | Verifies installation and test collection on clean environments. | Requires implementation and actual CI results before claiming platform coverage. |
| Record the agreed commit and environment with replication outputs | Distinguishes revision drift from environment drift. | Include modified/untracked test files when relevant. |
| Consider a tested dependency lock or constraints strategy | Reduces version drift between machines. | Choose a cross-platform approach and validate it; do not copy a Mac virtual environment to Windows. |

Adding `sys.path` hacks to every test, moving the whole package to the repository root, or weakening leakage assertions is unnecessary as a first response. Pytest documents the supported relationship between installation, import paths and the src layout in its [good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html).

## 9. Resolution criteria

The immediate import issue is resolved when:

1. The chosen Python executable is the intended environment.
2. `import quantfin` resolves to this checkout.
3. The `panel` imports required by the friend's tests succeed.
4. Collection finds the intended leakage tests without `ModuleNotFoundError`.
5. Running those tests produces actual test outcomes rather than collection errors.

A later failing assertion or dependency exception needs its own analysis. A successful import is not a claim that the entire pipeline or model has passed validation.

## 10. Evidence and references

Repository evidence reviewed: `pyproject.toml`, `requirements.txt`, README environment/test instructions, `src/quantfin/`, `src/quantfin/cross_market/panel.py`, and the local test inventory. The friend's installed packages, exact Git revision, and setup command history are not available; probable causes therefore remain ranked diagnoses rather than confirmed facts about that computer.

Official references consulted on 2 November 2026:

- [Python Packaging User Guide: src layout versus flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
- [pip: local project installations](https://pip.pypa.io/en/stable/topics/local-project-installs/).
- [pytest: good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html).
