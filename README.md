<a name="top"></a>

<div align="center" id="top">
  <p>
    <img src="docs/images/Logo.png" alt="PhotoShow logo" width="450">
  </p>

  <p>
    <em>Every Pixel Tells a Tale</em>
  </p>

  <p>
    <a href="https://github.com/pedromst2000/PhotoShow/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/pedromst2000/PhotoShow/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<br>

## :bookmark_tabs: Table of Contents

- [:bulb: About](#bulb-about)
- [:clapper: Demo Video](#clapper-demo-video)
- [:computer: Tech Stack](#computer-tech-stack)
- [:triangular_ruler: Architecture & Data Model](#triangular_ruler-architecture--data-model)
  - [:classical_building: Architecture](#classical_building-architecture)
  - [:card_file_box: Data Model](#card_file_box-data-model)
- [:rocket: Getting Started](#rocket-getting-started)
  - [:clipboard: Prerequisites](#clipboard-prerequisites)
  - [:inbox_tray: Quick Start](#inbox_tray-quick-start)
  - [:floppy_disk: Database Setup](#floppy_disk-database-setup)
- [:test_tube: Linting & Formatting](#test_tube-linting--formatting)
- [:hammer_and_wrench: Standalone Executable](#hammer_and_wrench-standalone-executable)
- [:handshake: Contributing](#handshake-contributing)
  - [:memo: Naming Conventions](#memo-naming-conventions)
  - [:arrows_counterclockwise: Contribution Workflow](#arrows_counterclockwise-contribution-workflow)
- [:page_facing_up: License](#page_facing_up-license)

<br>

## :bulb: About

PhotoShow is a local desktop application for browsing, organizing, and sharing photo collections. Sign in for a personalized, role-based experience.

**:sparkles: Key Features**

- Create and manage albums; upload and view photos.
- Explore and navigate community content.
- Like, comment on, and rate photos.
- Add other users' albums to your favorites.
- Follow other users and receive in-app notifications.
- Personalize your profile and avatar; admin tools to manage users and categories.

## :clapper: Demo Video

A demo video for PhotoShow will be added soon.

<br>

## :computer: Tech Stack

**Core Technologies**

- [Python 3.14+](https://www.python.org/) — Main programming language.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — GUI framework.
- [Pillow](https://pillow.readthedocs.io/en/stable/) — Image processing library.
- [pip](https://pip.pypa.io/en/stable/) — Package manager.

**Data & Security**

- [SQLite](https://www.sqlite.org/) — Embedded relational database.
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM and database toolkit.
- [bcrypt](https://github.com/pyca/bcrypt) — Password hashing.

**Code Quality & Linting**

- [Black](https://black.readthedocs.io/en/stable/) — Code formatter.
- [flake8](https://flake8.pycqa.org/en/latest/) — Code linter.
- [isort](https://pycqa.github.io/isort/) — Import sorter.
- [yamllint](https://yamllint.readthedocs.io/en/stable/) — YAML linter.
- [mypy](https://mypy.readthedocs.io/en/stable/) — Static type checker.

**Testing**

- [pytest](https://docs.pytest.org/en/stable/) — Testing framework.
- [pytest-mock](https://github.com/pytest-dev/pytest-mock) — Mocking in tests.
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) — Coverage reporting.
- [codecov](https://about.codecov.io/) — Code coverage reporting service.

**Packaging**

- [PyInstaller](https://www.pyinstaller.org/) — Build standalone executables.

<br>

## :triangular_ruler: Architecture & Data Model

### :classical_building: Architecture

> :warning: The preview below may be slightly outdated and will be refreshed in a later update.

[![Application Architecture](https://img.shields.io/badge/Application_Architecture-111827?style=for-the-badge&logo=visualstudiocode&logoColor=007ACC)](./docs/images/MVC_PHOTOSHOW.jpg)

![Application Architecture](./docs/images/MVC_PHOTOSHOW.jpg)

### :card_file_box: Data Model

> :warning: The preview below may be slightly outdated and will be refreshed in a later update.

The database model is shown as a `DER (Diagram Entity-Relationship)` preview so the main entities and relationships stay readable at a glance.

<div align="center">
  <p>
    <br>
    <a href="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=DER_PHOTOSHOW.drawio&dark=auto#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1mwGO-kwEJU-898KxfPnKxffRPsdYXHc4%26export%3Ddownload" target="_blank" rel="noopener noreferrer">
      <img src="./docs/images/DER_Preview.png" alt="PhotoShow database model preview" width="800" />
    </a>
  </p>
  <p>
    <a href="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=DER_PHOTOSHOW.drawio&dark=auto#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1mwGO-kwEJU-898KxfPnKxffRPsdYXHc4%26export%3Ddownload" target="_blank" rel="noopener noreferrer">
      <img src="https://img.shields.io/badge/View_Full_Model-Draw.io-FF6F00?style=for-the-badge&logo=diagramsdotnet&logoColor=white" alt="View full data model on Draw.io" />
    </a>
  </p>
</div>

ORM models live in `app/core/db/models/` and are implemented with `SQLAlchemy`. Key models:

- **User** — Account: username, email, password hash, profile, role.
- **Role** — Named user roles (e.g., admin, user).
- **Avatar** — User avatar image metadata.
- **Album** — Photo collection: title, description, owner, category.
- **Photo** — Photo record: filename, title, description, upload date; links to album and owner.
- **PhotoImage** — Stored image variants/paths linked to a `Photo`.
- **Comment** — Photo comment: author, content, timestamp.
- **Like** — Like relationship between a user and a photo.
- **Favorite** — User-saved album reference.
- **Follow** — Follow relationship between users.
- **Contact** — User-submitted contact or feedback message.
- **NotificationType** — Notification kind identifiers.
- **Notification** — In-app notification: recipient, content, read status.
- **Rating** — Numeric rating by a user for a photo.
- **Category** — Photo category: name and description.

<br>

## :rocket: Getting Started

### :clipboard: Prerequisites

- **Python 3.14.3** — Main programming language ([download](https://www.python.org/downloads/))
- **pip** — comes with Python
- **Git** — for cloning ([download](https://git-scm.com/downloads))
- (Recommended) Virtual environment support: `python -m venv`

> Verify your tools are available in the PATH:
>
> ```bash
> python --version
> pip --version
> git --version
> ```

### :inbox_tray: Quick Start

#### Clone the repository

```bash
git clone https://github.com/pedromst2000/PhotoShow.git
```

#### Navigate to the project directory

```bash
cd PhotoShow
```

> :bulb: **Tip:** Can't find the project directory? Open the folder in your code editor and use the integrated terminal.

#### Create and activate a virtual environment

Create the virtual environment:

```bash
python -m venv .venv
```

Activate it on **Windows PowerShell**:

```powershell
.venv\Scripts\Activate
```

Activate it on **macOS/Linux**:

```bash
source .venv/bin/activate
```

> **To deactivate the virtual environment:**
>
> - On any OS, simply run:

```bash
deactivate
```

This will return you to your system's default Python environment.

> **Note:** Some dependencies may only work correctly inside the `.venv` virtual environment. It is highly recommended to use the virtual environment for all development and testing.

#### Install dependencies

```bash
python -m pip install --upgrade pip
pip install --upgrade -r dev-requirements.txt
```

#### Run the app

```bash
python main.py
```

### :floppy_disk: Database Setup

`photoshow.db` is created automatically at the project root on first run. It is empty by default — use the commands below to create, seed, or restore data.

**Start (create schema if missing)**

```bash
python main.py
```

**Reset (backup current DB, wipe and reseed from CSV files)**

```bash
python main.py --resetDB
```

**Restore the latest backup**

```bash
python main.py --restoreDB
```

**Restore a specific backup**

```bash
python main.py --restoreDB backups/<folder>
```

> :warning: Backups may contain sensitive data (e.g., emails, password hashes). Keep backups local and do not commit them to version control — add backup folders or a matching pattern to your `.gitignore`.

<br>

## :test_tube: Linting & Formatting

Run these checks locally before committing to keep the codebase consistent and avoid CI failures.

#### Lint CSV data files

Checks CSV seed data files for structural and formatting issues.

```bash
python app/scripts/lint_csv.py
```

#### Format CSV data files

Auto-formats CSV seed data files to conform to project standards.

```bash
python app/scripts/format_csv.py
```

#### Check Python imports

Checks that Python imports are correctly ordered according to `isort` conventions.

```bash
python app/scripts/check_imports.py
```

#### Format Python imports

Auto-formats Python imports to match `isort` ordering conventions.

```bash
python app/scripts/format_imports.py
```

#### Lint Python files

Checks Python files for style violations and errors (`PEP 8` compliance).

```bash
python -m flake8 .
```

#### Format Python files

Auto-formats all Python files using the `Black` code formatter.

```bash
python -m black .
```

#### Check Python types

Runs static type checks on `app/` and `main.py` using `mypy`.

```bash
python -m mypy app main.py
```

> Configuration is managed via [`mypy.ini`](mypy.ini) at the project root.

#### Lint YAML files

Checks YAML configuration files for syntax and formatting issues.

```bash
python -m yamllint .
```

#### Check staged files

Runs all relevant checks (formatting, imports, CSV structure) on staged files only.

```bash
python app/scripts/check_changed_files.py
```

#### Auto-fix staged files

Automatically fixes all fixable issues in staged files — formatting, import ordering, and CSV structure. Only modifies currently staged files.

```bash
python app/scripts/check_changed_files.py --fix
```

---

> :warning: **Before every commit**, run the staged-file check to catch issues early and prevent CI failures:
>
> ```bash
> python app/scripts/check_changed_files.py
> ```
>
> Use `--fix` to apply automatic fixes, then review with `git diff --staged` before committing.
> If CI still fails, open the **Actions** tab on GitHub for detailed logs and fix any reported issues promptly.

<br>

## :hammer_and_wrench: Standalone Executable

Standalone executable instructions will be added soon.

<br>

## :handshake: Contributing

Your contributions help improve PhotoShow! Whether you're fixing a bug, improving the UI, or adding a new feature — every contribution matters.

- Found a bug? [Report it](https://github.com/pedromst2000/PhotoShow/issues/new?labels=bug)
- Have an enhancement idea? [Suggest it](https://github.com/pedromst2000/PhotoShow/issues/new?labels=enhancement)
- Ready to code? Follow the workflow below

### :memo: Naming Conventions

Follow these conventions for branches and commit messages:

| Type       | Purpose            | Branch Example           | Commit Example                    |
| ---------- | ------------------ | ------------------------ | --------------------------------- |
| `feat`     | New feature        | `feat/photo-grid`        | `feat: add photo grid view`       |
| `fix`      | Bug fix            | `fix/login-validation`   | `fix: resolve login error`        |
| `docs`     | Documentation      | `docs/update-readme`     | `docs: update installation steps` |
| `refactor` | Code restructuring | `refactor/album-service` | `refactor: simplify album logic`  |
| `test`     | Testing            | `test/auth-tests`        | `test: add auth unit tests`       |
| `ci`       | CI/CD pipelines    | `ci/add-lint-workflow`   | `ci: add lint workflow`           |
| `chore`    | Maintenance        | `chore/update-deps`      | `chore: update dependencies`      |

### :arrows_counterclockwise: Contribution Workflow

1. **Fork** the repository and clone your fork
2. **Create a branch:**
   ```bash
   git checkout -b <type>/<short-description>
   ```
3. **Make your changes**
4. **Commit:**
   ```bash
   git commit -m "<type>: <short description>"
   ```
5. **Push:**
   ```bash
   git push origin <type>/<short-description>
   ```
6. **Open a Pull Request**

**PR checklist:**

- :white_check_mark: Title follows naming conventions
- :white_check_mark: Description explains changes clearly
- :white_check_mark: Passes all linting and formatting checks
- :white_check_mark: No merge conflicts

Thanks for contributing! :tada:

## :page_facing_up: License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

<p align="center">
  <a href="#top">Back to top</a>
</p>
