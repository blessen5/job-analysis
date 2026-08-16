# Contributing Guidelines

Thank you for contributing to the **Job Market Analytics & Skill Demand Analysis** project. Please follow these guidelines for local setup, development workflows, and pull request submissions.

---

## 1. Local Environment Setup

### Prerequisites
* Python 3.11+
* Git

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/blessen-shaju/job-market-analytics.git
cd job-market-analytics

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r backend/requirements.txt
```

---

## 2. Running Tests

Run the test suite using `pytest`:

```bash
pytest
```

Ensure all tests pass before committing code.

---

## 3. Development Workflow

### Branch Naming Conventions
Use descriptive branch names with short prefixes:
* `feature/skill-extraction`
* `fix/health-check-endpoint`
* `docs/methodology-update`
* `chore/ci-pipeline`

### Commit Message Conventions
Follow standard Conventional Commits formatting:
* `feat: add raw data cleaning module`
* `fix: correct database session connection leak`
* `docs: add data dictionary definitions`
* `test: add unit tests for salary normalization`
* `chore: update dependencies`

---

## 4. Pull Request Process

1. Create a feature branch off `main`.
2. Commit your changes following commit guidelines.
3. Ensure all pytest tests pass locally.
4. Push your branch to GitHub and submit a Pull Request using the repository [Pull Request Template](file:///c:/Users/bless/OneDrive/Desktop/job%20analysis/job-market-analytics/.github/pull_request_template.md).
5. Complete all items in the PR checklist before requesting code review.
