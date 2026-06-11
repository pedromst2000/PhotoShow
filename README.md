<a name="top"></a>

 <p align="center">
    <a href="https://github.com/pedromst2000/PhotoShow/actions/workflows/code-quality.yml">
      <img src="https://github.com/pedromst2000/PhotoShow/actions/workflows/code-quality.yml/badge.svg" alt="Code Quality" />
    </a>
  </p>

<div align="center" id="top">
  <p>
    <img src="docs/images/Logo.png" alt="PhotoShow logo" width="450">
  </p>

<em>Every Pixel Tells a Tale</em>

  <p>
    <a href="https://github.com/pedromst2000/PhotoShow/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/pedromst2000/PhotoShow/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

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
  - [:cloud: Cloudinary Setup (Developers/Production)](#cloud-cloudinary-setup-developersproduction)
    - [Step 1: Create a Cloudinary Account](#step-1-create-a-cloudinary-account)
    - [Step 2: Configure Environment Variables](#step-2-configure-environment-variables)
    - [Step 3: Create Folder Structure](#step-3-create-folder-structure-in-cloudinary)
    - [Step 4: Populate Dev Folder](#step-4-populate-your-dev-folder)
    - [Step 5: Folder Separation](#step-5-folder-separation)
    - [Troubleshooting](#troubleshooting)
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

- 📁 Create and manage albums
- 📸 Upload and view photos
- 🔍 Browse community content
- ❤️ Like and rate photos
- 💬 Comment on photos
- ⭐ Add albums to favorites
- 👥 Follow other users
- 🔔 Receive in-app notifications
- 👤 Customize your profile
- 🎨 Set a custom avatar
- 🚩 Report inappropriate content
- 👨‍💼 Admin tools for user management
- 📋 Admin tools for category management
- ✅ Admin review system for reports

## :clapper: Demo Video

A demo video for PhotoShow will be added soon.

<br>

## :computer: Tech Stack

**Core Technologies**

- [Python 3.14+](https://www.python.org/) - Main programming language.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework.
- [Pillow](https://pillow.readthedocs.io/en/stable/) - Image processing library.
- [pip](https://pip.pypa.io/en/stable/) - Package manager.

**Data & Security**

- [SQLite](https://www.sqlite.org/) - Embedded relational database.
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM and database toolkit.
- [bcrypt](https://github.com/pyca/bcrypt) - Password hashing.

**Code Quality & Linting**

- [Black](https://black.readthedocs.io/en/stable/) - Code formatter.
- [flake8](https://flake8.pycqa.org/en/latest/) - Code linter.
- [isort](https://pycqa.github.io/isort/) - Import sorter.
- [yamllint](https://yamllint.readthedocs.io/en/stable/) - YAML linter.
- [mypy](https://mypy.readthedocs.io/en/stable/) - Static type checker.

**Testing**

- [pytest](https://docs.pytest.org/en/stable/) - Testing framework.
- [pytest-mock](https://github.com/pytest-dev/pytest-mock) - Mocking in tests.
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) - Coverage reporting.
- [codecov](https://about.codecov.io/) - Code coverage reporting service.

**Packaging**

- [PyInstaller](https://www.pyinstaller.org/) - Build standalone executables.

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

ORM models live in `app/core/db/models/` and are implemented with `SQLAlchemy`. You can check also in `app\core\db\models\__init__.py` for a quick overview of all the main entities and their relationships.

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

`photoshow.db` is created automatically at the project root on first run. Use the commands below to manage the database state.

| Command | Description |
|---|---|
| `python main.py --backupDB` | Snapshot the current live DB to `backups/<timestamp>/` |
| `python main.py --resetDB` | Auto-backup, then wipe and reseed from seed CSV files |
| `python main.py --restoreDB` | Restore DB from the latest backup |
| `python main.py --restoreDB backups/<folder>` | Restore DB from a specific backup snapshot |

**When to use each:**

- **`--backupDB`** - before making risky changes or testing destructive operations; saves the current live state
- **`--resetDB`** - returns the app to the initial dummy-data state (useful for local feature testing); always auto-backups first
- **`--restoreDB`** - brings back a previous state after a reset or data loss; defaults to the newest backup

> :warning: Backups may contain sensitive data (e.g., emails, password hashes). Keep the `backups/` folder local and out of version control - it is already listed in `.gitignore`.

### :cloud: Cloudinary Setup (Developers/Production)

**PhotoShow** uses [Cloudinary](https://cloudinary.com/) to store and manage media assets. The **Project Owner** maintains the main cloud account with production assets, while each **developer/contributor** creates their own Cloudinary account as a local development copy.

**Cloud Architecture:**
- **Owner's Cloud:** Main account for the project owner/maintainer with all production assets
- **Developer's Cloud:** Individual copy for each contributor, mirroring the owner's structure for isolated development

#### Step 1: Create a Cloudinary Account

1. Sign up for a free account at [cloudinary.com](https://cloudinary.com/)
2. From your **Dashboard**, note your credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

#### Step 2: Configure Environment Variables

Copy [`.env.example`](.env.example) to `.env` and fill in your Cloudinary credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your values from the Cloudinary dashboard.

> :warning: **Never commit `.env` to git.** It is listed in `.gitignore` for security.

#### Step 3: Create Folder Structure and Populate with Seed Data

In your Cloudinary **Media Library**, create the same folder structure and populate it with seed assets from the Owner's Cloud.

**GUI Path:** `Media Library > Folders > Home` → Create folder `photo-show`

**Reference Image (Owner's Cloud structure):**

<div align="center">
  <img src="./docs/images/Cloudinary_GUI_Layout_Assets.png" alt="Cloudinary folder structure" width="600" />
</div>

**Folder structure to create:**

```
photo-show/
├── dev/                         # [CRITICAL: Mirror from Owner's Cloud]
│   ├── profile_avatars/         # Seed avatars (download from owner's CSV)
│   └── photos_gallery/          # Seed photos (download from owner's CSV)
└── prod/                        # [Your uploads only]
    ├── profile_avatars/         # Your avatar uploads (empty initially)
    └── photos_gallery/          # Your photo uploads (empty initially)
```

**Populate your `dev/` folders:**

1. Open `app/files/avatars.csv` or `app/files/photo_image.csv`
2. These CSV files reference the **Owner's Cloud** seed images
3. For each image URL in the `provider_url_image` column:
   - Open the URL in your browser
   - **Right-click** → **"Guardar imagem como..."** (Save image as...)
   - Save locally
   - Upload to your Cloudinary `photo-show/dev/profile_avatars/` or `photo-show/dev/photos_gallery/`

**Folder Behavior:**

| Folder | Purpose | Reset Behavior | Modified By |
|--------|---------|---|---|
| `dev/profile_avatars` | Seed avatars (mirrored from owner) | **Preserved** ✓ | App reads from CSV |
| `dev/photos_gallery` | Seed photos (mirrored from owner) | **Preserved** ✓ | App reads from CSV |
| `prod/profile_avatars` | Your avatar uploads | **Cleared** 🗑️ | App auto-manages |
| `prod/photos_gallery` | Your photo uploads | **Cleared** 🗑️ | App auto-manages |

> :bulb: **Key Point:** `dev/` folders are your local copy of the owner's seed data and survive `--resetDB`. `prod/` folders are cleared during reset to return to initial development state.

#### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ValueError: Must supply api_key` | Add missing variables to `.env` from `.env.example` |
| Images show as broken links | Verify images are in your Cloudinary `dev/` folders and `.env` has correct credentials |
| Database reset deletes my uploads | Expected behavior—`prod/` folders are cleared. Run `python main.py --backupDB` first if you want to preserve data |

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

#### Validate staged files before committing

Before committing, run the check on your staged changes and (if needed) auto-fix style issues:

Run the check:

```bash
python app/scripts/check_changed_files.py
```

To auto-fix style-only problems (formatting, imports, CSV structure):

```bash
python app/scripts/check_changed_files.py --fix
```

Note: `--fix` only addresses style issues. Re-run the first command after fixes to confirm everything is clean before committing.

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
  <a href="#top">⬆️ Back to top</a>
</p>
