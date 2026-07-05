<a name="top"></a>

<p align="center">
  <a href="https://github.com/pedromst2000/PhotoShow/actions/workflows/tests.yml">
      <img src="https://github.com/pedromst2000/PhotoShow/actions/workflows/tests.yml/badge.svg" alt="Tests" />    
   </a>
    <a href="https://github.com/pedromst2000/PhotoShow/actions/workflows/code-quality.yml">
      <img src="https://github.com/pedromst2000/PhotoShow/actions/workflows/code-quality.yml/badge.svg" alt="Code Quality" />
    </a>
      <a href="https://codecov.io/gh/pedromst2000/PhotoShow">
      <img src="https://codecov.io/gh/pedromst2000/PhotoShow/graph/badge.svg?branch=master" alt="Coverage" />
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
- [:art: UI Screenshots](#art-ui-screenshots)
- [:computer: Tech Stack](#computer-tech-stack)
- [:triangular_ruler: Architecture & Data Model](#triangular_ruler-architecture--data-model)
  - [:classical_building: Architecture](#classical_building-architecture)
  - [:card_file_box: Data Model](#card_file_box-data-model)
- [:rocket: Getting Started](#rocket-getting-started)
  - [:clipboard: Prerequisites](#clipboard-prerequisites)
  - [:inbox_tray: Quick Start](#inbox_tray-quick-start)
- [:floppy_disk: Database Setup](#floppy_disk-database-setup)
- [:cloud: Cloudinary Setup](#cloud-cloudinary-setup)
- [:test_tube: Linting & Formatting](#test_tube-linting--formatting)
- [:hammer_and_wrench: Standalone Executable](#hammer_and_wrench-standalone-executable)
  - [Using the Executable](#using-the-executable)
  - [Database Location](#database-location)
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
- 👥 Follow other users and manage your profile
- 🔔 Receive in-app notifications
- 🚩 Report inappropriate content
- 🛠️ Admin tools for user and category management
- ✅ Admin review system for reports
- 📧 Contact Admin for banned users to appeal their ban

## :clapper: Demo Video

A demo video for PhotoShow will be added soon.

<br>

## :art: UI Screenshots

<details>
<summary><strong>Click to expand and view application screenshots</strong></summary>

### Home View & Menu Navigation

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Home_Screen_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Home_Screen_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Admin_Menu_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### Authentication & User Registration

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Sign_In_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Sign_Up_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### 📁 Create and manage albums

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Albuns_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Albuns_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Albuns_03.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Albuns_04.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### 📸 Upload and view photos

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Add_Photo_01.png" alt="PhotoShow UI screenshots" width="500" height="400" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Add_Photo_02.png" alt="PhotoShow UI screenshots" width="500" height="400" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Add_Photo_03.png" alt="PhotoShow UI screenshots" width="500" height="400" />
  </p>

### 🔍❤️ Browse community content & Like and rate photo

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Explore_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Explore_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Explore_03.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Explore_04.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Explore_05.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Photo_Details_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Album_Details_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### 💬 Comment on photos

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Photo_Comments_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### ⭐ Add albums to favorites

<p align="center">
    <img src="./docs/images/UI_Screenshoots/Favorites_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

  <p align="center">
    <img src="./docs/images/UI_Screenshoots/Favorites_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### 👥 Follow other users and manage your profile

 <p align="center">
    <img src="./docs/images/UI_Screenshoots/Profile_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Profile_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Profile_03.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Change_Avatar_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Change_Avatar_02.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

   <p align="center">
    <img src="./docs/images/UI_Screenshoots/Change_Password_01.png" alt="PhotoShow UI screenshots" width="500" />
  </p>

### 🔔 Receive in-app notifications

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Notifications_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>
  
  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Notifications_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

### 🚩 Report inappropriate content

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Report_Photo_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Report_Photo_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

### 🛠️ Admin tools for user and category management

 <p align="center">
      <img src="./docs/images/UI_Screenshoots/Admin_Manage_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Admin_Manage_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Admin_Manage_03.png" alt="PhotoShow UI screenshots" width="500" />
    </p>
  
   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Admin_Manage_04.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

### ✅ Admin review system for reports

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Reports_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Reports_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Reports_03.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

### MessageBoxes & Alerts

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>
  
   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_03.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_04.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_05.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_06.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_07.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_08.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_09.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_10.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_11.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_12.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Messagebox_13.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Onboarding_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

### 📧 Contact Admin and Banned Notice

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Contact_Admin_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Contacts_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

  <p align="center">
      <img src="./docs/images/UI_Screenshoots/Contacts_02.png" alt="PhotoShow UI screenshots" width="500" />
    </p>
  
   <p align="center">
      <img src="./docs/images/UI_Screenshoots/Banned_Notice_01.png" alt="PhotoShow UI screenshots" width="500" />
    </p>

</details>

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

**Cloud Storage**

- [Cloudinary](https://cloudinary.com/) - Image hosting and management.
- [python-cloudinary](https://github.com/cloudinary/cloudinary_python) - Cloudinary SDK.

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

**Packaging**

- [PyInstaller](https://www.pyinstaller.org/) - Build standalone executables.

<br>

## :triangular_ruler: Architecture & Data Model

### :classical_building: Architecture

[![Application Architecture](https://img.shields.io/badge/Application_Architecture-111827?style=for-the-badge&logo=visualstudiocode&logoColor=007ACC)](./docs/images/MVC_PHOTOSHOW.jpg)

![Application Architecture](./docs/images/MVC_PHOTOSHOW.jpg)

### :card_file_box: Data Model

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

- **Python 3.14+** — Main programming language ([download](https://www.python.org/downloads/))
- **pip** — comes with Python
- **Git** — for cloning ([download](https://git-scm.com/downloads))
- (Recommended) Virtual environment support: `python -m venv`
- **DB Browser for SQLite** — For viewing and debugging the local database ([download](https://sqlitebrowser.org/))

> Verify your tools are available in the PATH:
>
> ```bash
> python --version
> pip --version
> git --version
> ```

### :inbox_tray: Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/pedromst2000/PhotoShow.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd PhotoShow
   ```

3. **Create and activate a virtual environment:**

   Create:

   ```bash
   python -m venv .venv
   ```

   Activate on **Windows (Command Prompt)**:

   ```cmd
   .venv\Scripts\Activate.bat
   ```

   Activate on **Windows PowerShell** (if you get an execution policy error, see note below):

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   > ⚠️ **PowerShell Execution Policy Error?** If you see "running scripts is disabled on this system", either:
   >
   > - Use **Command Prompt** (`.bat` command above) instead, OR
   > - Run this once to allow scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

   Activate on **macOS/Linux**:

   ```bash
   source .venv/bin/activate
   ```

   > **To deactivate the virtual environment:**
   >
   > - On any OS, simply run:
   >
   > ```
   > deactivate
   > ```
   >
   > This will return you to your system's default Python environment.
   >
   > **Note:** Some dependencies may only work correctly inside the `.venv` virtual environment. It is highly recommended to use the virtual environment for all development and testing.

4. **Install dependencies:**

   ```bash
   python -m pip install --upgrade pip
   pip install --upgrade -r dev-requirements.txt
   ```

5. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your Cloudinary credentials (see [Cloudinary Setup](#cloud-cloudinary-setup) below).

6. **Run the app:**
   ```bash
   python main.py
   ```

<br>

## :floppy_disk: Database Setup

PhotoShow uses **SQLite** for local data storage. The database file (`photoshow.db`) is created automatically at the project root on first run.

### Database Commands

| Command                                       | Description                                     |
| --------------------------------------------- | ----------------------------------------------- |
| `python main.py --backupDB`                   | Backup the database to `backups/<timestamp>/`   |
| `python main.py --resetDB`                    | Reset to initial seed data (auto-backups first) |
| `python main.py --restoreDB`                  | Restore from latest backup                      |
| `python main.py --restoreDB backups/<folder>` | Restore from specific backup                    |

**When to use:**

- **`--backupDB`** — Before making risky changes
- **`--resetDB`** — Return to initial state for testing
- **`--restoreDB`** — Recover from a previous backup

### Viewing Database Content

For detailed instructions on viewing the database in both development and distribution modes, see [Database Location](#database-location) in the [Standalone Executable](#hammer_and_wrench-standalone-executable) section.

> :warning: **Backups:** The `backups/` folder may contain sensitive data. Keep it local and out of version control (listed in `.gitignore`).

<br>

## :cloud: Cloudinary Setup

PhotoShow uses [Cloudinary](https://cloudinary.com/) to store photos and avatars. Each developer creates their own free Cloudinary account.

### Step 1: Create a Cloudinary Account

1. Sign up for a free account at [cloudinary.com](https://cloudinary.com/)
2. From your **Dashboard**, copy these credentials:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

### Step 2: Configure Environment Variables

1. If you haven't already, copy [`.env.example`](.env.example) to `.env` (see [Quick Start — Step 5](#inbox_tray-quick-start)):

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Cloudinary credentials from the dashboard

> :warning: **Never commit `.env` to git.** It's in `.gitignore` for security.

### Step 3: Create Folder Structure in Cloudinary

In your Cloudinary **Media Library**, create this folder structure:

```
photo-show/
├── dev/                    # Seed data (reference images)
│   ├── profile_avatars/
│   └── photos_gallery/
└── prod/                   # Your uploads
    ├── profile_avatars/
    └── photos_gallery/
```

**GUI Path:** Media Library → Folders → Home → Create `photo-show` folder

<div align="center">
  <img src="./docs/images/Cloudinary_GUI_Layout_Assets.png" alt="Cloudinary folder structure" width="600" />
</div>

### Step 4: Populate Seed Data (Optional)

To add reference images to your `dev/` folders:

1. Open [avatars.csv](app/files/avatars.csv) or [photo_image.csv](app/files/photo_image.csv)
2. For each image URL in the `provider_url_image` column:
   - Click the URL link to open it in your browser
   - Right-click → Save image locally
   - Upload to your Cloudinary `photo-show/dev/profile_avatars/` or `photo-show/dev/photos_gallery/`

> :bulb: **Tip:** The `dev/` folder preserves seed data during `--resetDB`. The `prod/` folder stores your uploads and is cleared on reset.

### Troubleshooting

| Problem                            | Fix                                                                          |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| `ValueError: Must supply api_key`  | Check `.env` has correct `CLOUDINARY_*` credentials                          |
| Images show broken links           | Verify folders exist in Cloudinary Media Library with correct names          |
| Images disappear after `--resetDB` | Expected — `prod/` folder is cleared. Use `--backupDB` to save uploads first |

<br>

## :test_tube: Linting & Formatting

Run these checks locally before committing to keep the codebase consistent and avoid CI failures.

#### Check all changed files

Runs all code quality checks (flake8, mypy, black, isort, yamllint, lint_csv) on files that have changed vs HEAD:

```bash
python app/scripts/check_changed_files.py
```

Auto-fix style issues (black, isort, format_csv) in changed files only:

```bash
python app/scripts/check_changed_files.py --fix
```

> :bulb: **Tip:** Use this before committing to catch style and type issues quickly on only the files you changed.

#### Format Python code

Auto-formats all Python files using Black:

```bash
python -m black app tests main.py
```

#### Lint Python files

Checks Python files for style violations and errors (PEP 8 compliance):

```bash
python -m flake8 .
```

#### Format import statements

Auto-sorts imports in Python files using isort:

```bash
python app/scripts/format_imports.py
```

#### Check import ordering

Validates that all Python files have properly sorted imports:

```bash
python app/scripts/check_imports.py
```

#### Check Python types

Runs static type checks on `app/`, `tests/`, and `main.py` using mypy:

```bash
python -m mypy app tests main.py
```

#### Lint YAML files

Checks YAML configuration files for syntax and formatting issues:

```bash
python -m yamllint .
```

#### Format CSV data files

Auto-formats CSV seed data files (removes empty rows, strips whitespace, consistent quoting):

```bash
python app/scripts/format_csv.py
```

#### Lint CSV data files

Checks CSV seed data files for structural and formatting issues:

```bash
python app/scripts/lint_csv.py
```

<br>

## :test_tube: Running Tests

Run tests using the dedicated test runner script for convenience, or use pytest directly for more control.

#### Run all tests

Executes the full test suite (smoke, unit, functional, integration, acceptance):

```bash
python run_tests.py
```

#### Run only unit and smoke tests

Runs quick unit tests plus smoke gate checks:

```bash
python run_tests.py --unit
```

#### Run only functional tests

Runs business logic verification tests:

```bash
python run_tests.py --functional
```

#### Run only integration tests

Runs service interaction tests with real database:

```bash
python run_tests.py --integration
```

#### Run only acceptance tests

Runs complete user workflow tests:

```bash
python run_tests.py --acceptance
```

#### Run tests with coverage report

Generates a coverage report showing which code lines are tested:

```bash
python run_tests.py --coverage
```

This generates:

- Terminal coverage report (shows percentage per module)
- `coverage.xml` file (for CI/CD tools like GitHub Actions, GitLab CI)

#### Run tests directly with pytest

If you prefer to use pytest directly instead of the test runner script:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml

# Run specific layer
python -m pytest tests/unit/ -v          # Unit tests only
python -m pytest tests/smoke/ -v         # Smoke tests only
python -m pytest tests/functional/ -v    # Functional tests only
python -m pytest tests/integration/ -v   # Integration tests only
python -m pytest tests/acceptance/ -v    # Acceptance tests only
```

#### Generate coverage for CI/tools

To produce machine-readable coverage data for CI/CD pipelines and tools:

```bash
python -m pytest tests/ --cov=app --cov-report=xml:coverage.xml
```

<br>

## :hammer_and_wrench: Standalone Executable

You can compile PhotoShow into a self-contained application folder using `PyInstaller`, which bundles everything needed to run it. However, please note:

> ⚠️ **Warning:** The generated executable is intended for use on your own machine. Running the executable on remote or other machines may trigger antivirus false positives or fail due to environment differences. Distribution is not recommended.

To compile locally, follow these steps:

1. **Set up your environment and dependencies** (see [Getting Started](#rocket-getting-started) above).
2. **Activate your virtual environment** (see [Getting Started](#rocket-getting-started) above).
3. **Install PyInstaller in your virtual environment**:
   ```bash
   pip install pyinstaller
   ```
4. **Compile the application** (in your activated virtual environment):

   > ⚠️ **Before rebuilding:** If `PhotoShow.exe` is already running, **close it first**. Windows locks DLLs of running processes and PyInstaller will fail with a `PermissionError` if the exe is open.

   **Using the build script (recommended - embeds credentials at compile time):**

   The `build.py` script handles everything automatically: it takes your Cloudinary credentials, creates `.env`, embeds it into the executable, runs PyInstaller, and verifies the output.

   **Choose one method:**

   **🟢 Interactive (you're prompted for credentials):**

   ```bash
   python scripts/build.py --interactive
   ```

   **🔵 Command-Line Arguments:**

   ```bash
   python scripts/build.py --cloud-name your_cloud_name --api-key your_api_key --api-secret your_secret --default-avatar-public-id your_avatar_public_id --default-avatar-url your_avatar_url
   ```

   **What the build script does for you:**
   - ✅ Takes your credentials (interactive or CLI args)
   - ✅ Creates `.env` with embedded credentials
   - ✅ Runs `pyinstaller PhotoShow.spec --clean --noconfirm` internally
   - ✅ Copies `.env` next to `PhotoShow.exe` in `dist/PhotoShow/`
   - ✅ Verifies the build succeeded
   - ✅ Shows you next steps

   > ⚠️ **Antivirus false positives — IMPORTANT:** PyInstaller bundles Python DLLs (e.g. `ucrtbase.dll`, `python313.dll`, `msvcrt.dll`) into the `_internal/` folder.
   >
   > **To resolve:**
   >
   > - Add `dist/PhotoShow/` folder and all its contents to your antivirus **exclusion list**
   > - Or **allow/verify** the exe when your antivirus prompts you (click "Run anyway" or "Allow")
   > - If antivirus blocks DLL access: `PermissionError: [Errno 13] Permission denied: '..._internal\ucrtbase.dll'` → exclude the entire `dist/PhotoShow/_internal/` folder from real-time scanning

   > After building, a `dist/PhotoShow` folder is created. Open it and run `PhotoShow.exe` — no Python required. Keep the entire folder together (do not remove `_internal` or other support files). The executable is platform-specific; rebuild separately on Windows, macOS, or Linux.

   > **Deploy anywhere:** Move the `PhotoShow` folder from `dist/` to your **Desktop** (or anywhere you want). Then double-click `PhotoShow.exe` inside it to run — no Python required! Keep the folder and all its contents together.

### Database Location

> ⚠️ **CRITICAL:** The database location is **DIFFERENT** depending on how you run PhotoShow. Opening the wrong database file in SQLite Browser will make data changes appear out of sync!

**The database location differs between development and distribution modes:**

| Mode                     | Database Location                                                           | When to use                            |
| ------------------------ | --------------------------------------------------------------------------- | -------------------------------------- |
| **Development (source)** | `C:\Users\User\Desktop\PhotoShow\photoshow.db` (root folder)                | Running `python main.py` from the repo |
| **Distribution (exe)**   | `C:\Users\User\Desktop\PhotoShow\dist\PhotoShow\photoshow.db` (dist folder) | Running `dist/PhotoShow/PhotoShow.exe` |

**Always verify which `photoshow.db` you're opening in SQLite Browser:**

- **Dev mode** → Open from **project root**
- **Distribution mode** → Open from **dist/PhotoShow/** folder

#### Viewing Database Content

1. Open **DB Browser for SQLite**
2. **File** → **Open Database**
3. Select the correct database file based on your mode:
   - **Dev mode:** `photoshow.db` at project root
   - **Distribution mode:** `dist/PhotoShow/photoshow.db`

**In development mode:** You'll see real-time changes from the app running via `python main.py`.

**In distribution mode:** You'll see data from the packaged executable. If changes aren't appearing, verify you opened the correct file in `dist/PhotoShow/` folder, not the project root.

> ⚠️ **Do NOT mix them up** — opening the wrong file makes it appear data isn't syncing.
> <br>

## :handshake: Contributing

Your contributions help improve PhotoShow! Whether you're fixing a bug, improving the UI, or adding a new feature — every contribution matters.

- Found a bug? [Report it](https://github.com/pedromst2000/PhotoShow/issues/new?labels=bug)
- Have an enhancement idea? [Suggest it](https://github.com/pedromst2000/PhotoShow/issues/new?labels=enhancement)
- Ready to code? Follow the workflow below

### :memo: Naming Conventions

| Type       | Purpose            | Branch Example                 | Commit Example                                              |
| ---------- | ------------------ | ------------------------------ | ----------------------------------------------------------- |
| `feat`     | New feature        | `feat/photo-grid`              | `feat: add photo grid view`                                 |
| `fix`      | Bug fix            | `fix/login-validation`         | `fix: resolve login error`                                  |
| `docs`     | Documentation      | `docs/update-readme`           | `docs: update installation steps`                           |
| `refactor` | Code restructuring | `refactor/album-service`       | `refactor: simplify album logic`                            |
| `test`     | Testing            | `test/auth-tests`              | `test: add auth unit tests`                                 |
| `build`    | Build system       | `build/pyinstaller-dist-fixes` | `build: automate PyInstaller with compile-time credentials` |
| `ci`       | CI/CD pipelines    | `ci/add-lint-workflow`         | `ci: add lint workflow`                                     |
| `chore`    | Maintenance        | `chore/update-deps`            | `chore: update dependencies`                                |

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

- ✅ Branch name follows naming conventions ( See [above](#memo-naming-conventions) )
- ✅ Description explains changes clearly
- ✅ Passes all CI checks. See [GitHub Actions](https://github.com/pedromst2000/PhotoShow/actions) tab for details
- ✅ No merge conflicts

Thanks for contributing! 🎉

## :page_facing_up: License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

<p align="center">
  <a href="#top">⬆️ Back to top</a>
</p>
