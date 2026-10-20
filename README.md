# GitLab Time Analytics

A Django REST Framework backend for **collecting time-tracking data from GitLab** and turning it into **insights**: who spent how much time, on which projects, issues and merge requests, and how that changes over time.

![Python](https://img.shields.io/badge/python-3.14-blue)
![Django](https://img.shields.io/badge/django-6.1-green)
![DRF](https://img.shields.io/badge/DRF-3.18-red)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-brightgreen)
![Status](https://img.shields.io/badge/status-early%20development-orange)

> **Project status:** early development. The project foundation (DRF, Swagger, health check, app structure) is in place. GitLab integration and analytics are on the [roadmap](#roadmap). The `authors` and `books` apps are **temporary sample apps** and will be replaced by the domain apps described below.

---

## Table of Contents

- [Overview](#overview)
- [Goals](#goals)
- [Architecture](#architecture)
- [Planned Data Model](#planned-data-model)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Current Endpoints](#current-endpoints)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Overview

GitLab lets team members log time on issues and merge requests, using `/spend` quick actions or the time tracking UI. That data is spread across many projects and is hard to analyze inside GitLab.

This service will:

1. **Ingest** time logs from one or more GitLab groups and projects through the GitLab API.
2. **Store** them in a normalized, query-friendly schema.
3. **Expose** a clean REST API for raw data and aggregated analytics.
4. **Power** dashboards and reports such as time per user, per project, per label, per milestone and per period.

---

## Goals

- **Reliable sync:** incremental, idempotent imports that are safe to re-run.
- **Accurate data:** time logs keep their original author, date, target (issue or MR) and summary.
- **Analytics-ready:** a schema designed for aggregation by user, project, label, milestone and time range.
- **API-first:** every capability is available over a documented REST API (OpenAPI / Swagger).
- **Extensible:** clear app boundaries so new data sources and reports can be added easily.

---

## Architecture

```
┌──────────────┐     sync jobs      ┌──────────────────────┐      REST API      ┌──────────────┐
│    GitLab    │ ─────────────────▶ │   Ingestion layer    │                    │  Dashboards  │
│  (REST and   │  timelogs, issues, │  (GitLab client,     │                    │  / Reports / │
│   GraphQL)   │  MRs, users, ...   │   sync services)     │                    │  BI tools    │
└──────────────┘                    └──────────┬───────────┘                    └──────▲───────┘
                                               │ normalized data                       │
                                               ▼                                       │
                                    ┌──────────────────────┐   aggregations   ┌───────┴───────┐
                                    │      Database        │ ───────────────▶ │ Analytics API │
                                    │ (users, projects,    │                  │  (DRF views)  │
                                    │  issues, timelogs)   │                  └───────────────┘
                                    └──────────────────────┘
```

**Planned apps:**

| App          | Responsibility                                                         |
| ------------ | ---------------------------------------------------------------------- |
| `health`     | Liveness and readiness checks *(implemented)*                          |
| `gitlab`     | GitLab API client, credentials and sync jobs                           |
| `tracking`   | Core domain models: users, projects, issues, MRs, time logs            |
| `analytics`  | Aggregation endpoints: totals, breakdowns, trends                      |

Each app shows up as its own section in Swagger automatically (see [`config/schema.py`](config/schema.py)).

---

## Planned Data Model

> Subject to change as the integration is built.

| Model           | Key fields                                                                   |
| --------------- | ---------------------------------------------------------------------------- |
| `GitLabUser`    | `gitlab_id`, `username`, `name`, `email`, `state`                            |
| `Project`       | `gitlab_id`, `path_with_namespace`, `name`, `web_url`                        |
| `Issue`         | `gitlab_id`, `iid`, `project`, `title`, `state`, `labels`, `milestone`       |
| `MergeRequest`  | `gitlab_id`, `iid`, `project`, `title`, `state`, `labels`, `milestone`       |
| `TimeLog`       | `gitlab_id`, `user`, `issue` or `merge_request`, `time_spent` (seconds), `spent_at`, `summary` |
| `SyncRun`       | `started_at`, `finished_at`, `status`, `scope`, `records_created`, `errors`  |

**Example analytics questions the API will answer:**

- How many hours did each team member log this week or month?
- How is time split across projects, labels or milestones?
- What is the estimated time compared with the time actually spent per issue?
- Which issues take the most time?
- How does logged time trend over the last N weeks?

---

## Tech Stack

| Component        | Choice                    | Notes                                  |
| ---------------- | ------------------------- | -------------------------------------- |
| Language         | Python 3.14               |                                        |
| Framework        | Django 6.1, DRF 3.18      |                                        |
| API docs         | drf-spectacular 0.30      | Swagger UI and ReDoc                   |
| Database         | SQLite (dev)              | PostgreSQL planned for production      |
| Background jobs  | *planned*                 | For example Celery or django-q         |

---

## Getting Started

### Prerequisites

- Python 3.14+
- Git

### 1. Clone the repository

```bash
git clone <repository-url> gitlab-time-analytics
cd gitlab-time-analytics
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API is now available at **http://127.0.0.1:8000/**.

---

## API Documentation

| Interface      | URL                                  |
| -------------- | ------------------------------------ |
| Swagger UI     | http://127.0.0.1:8000/api/docs/      |
| ReDoc          | http://127.0.0.1:8000/api/redoc/     |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/    |
| Django admin   | http://127.0.0.1:8000/admin/         |

Endpoints are grouped by app in Swagger. New apps get their own section automatically, based on the `verbose_name` in their `apps.py`.

---

## Current Endpoints

### Health

| Method | Endpoint        | Description                               |
| ------ | --------------- | ----------------------------------------- |
| GET    | `/api/health/`  | Service status and database connectivity  |

Returns `200 OK` when healthy and `503 Service Unavailable` if the database is unreachable.

```json
{
  "status": "ok",
  "database": "ok"
}
```

### Sample apps (temporary)

`/api/authors/` and `/api/books/` provide full CRUD (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). They exist only as reference implementations of the app pattern and **will be removed** when the domain apps land.

---

## Configuration

Settings are read from environment variables:

| Variable               | Default                   | Description                             |
| ---------------------- | ------------------------- | --------------------------------------- |
| `DJANGO_SECRET_KEY`    | `dev-insecure-change-me`  | Secret key (**change in production**)   |
| `DJANGO_DEBUG`         | `1`                       | Set to `0` to disable debug mode        |
| `DJANGO_ALLOWED_HOSTS` | `*`                       | Comma-separated list of allowed hosts   |

**Planned** for the GitLab integration:

| Variable             | Description                                              |
| -------------------- | -------------------------------------------------------- |
| `GITLAB_URL`         | Base URL of the GitLab instance, e.g. `https://gitlab.com` |
| `GITLAB_TOKEN`       | Access token with `read_api` scope                       |
| `GITLAB_GROUP_IDS`   | Comma-separated group IDs to sync                        |

> Never commit tokens. Keep secrets in environment variables or a secrets manager.

---

## Project Structure

```
.
├── config/                 # Project configuration
│   ├── settings.py         # Django, DRF and Swagger settings
│   ├── urls.py             # Root URL routing and API docs
│   ├── schema.py           # Groups Swagger endpoints by app
│   └── wsgi.py
├── health/                 # Health check endpoint
├── authors/                # Sample app (temporary)
├── books/                  # Sample app (temporary)
├── manage.py
└── requirements.txt
```

Each domain app follows the same layout:

```
<app>/
├── models.py         # Database models
├── serializers.py    # Validation and representation
├── views.py          # API views and viewsets
├── urls.py           # Routes
├── admin.py          # Admin configuration
└── apps.py           # verbose_name = Swagger section
```

---

## Roadmap

- [x] Project foundation: Django, DRF, Swagger/ReDoc, app-based API grouping
- [x] Health check endpoint
- [ ] Replace sample apps with `tracking` domain models
- [ ] GitLab API client with token authentication and pagination
- [ ] Sync users, projects, issues and merge requests
- [ ] Incremental time log import (idempotent, resumable)
- [ ] `sync_gitlab` management command
- [ ] Scheduled background sync
- [ ] Read-only API for synced data, with filters (user, project, date range)
- [ ] Analytics endpoints: totals, breakdowns and weekly or monthly trends
- [ ] Authentication and permissions
- [ ] PostgreSQL, Docker and CI pipeline
- [ ] Test suite and coverage reporting

---

## Contributing

1. Create a branch from `main`: `git checkout -b feature/<short-name>`
2. Keep changes focused and follow the existing app structure.
3. Make sure `python manage.py check` passes and the schema builds:
   ```bash
   python manage.py spectacular --validate --file schema.yml
   ```
4. Open a merge request with a clear description of the change.
