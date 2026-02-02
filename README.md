# Service Day Dashboard - Developer Onboarding Guide

Welcome to the **Service Day Dashboard** project! This guide is designed to help you understand the project structure, our development patterns, and how to start contributing to new Use Cases.

## 1. Project Overview
This is a Django-based web application designed to manage CSR (Corporate Social Responsibility) activities. It allows administrators to manage NGO activities and employees to register for them.

### Key Technologies
- **Backend**: Python 3.11+, Django 5.x
- **Frontend**: Tailwind CSS (via CDN), HTML5
- **Database**: SQLite (default)

---

## 2. Getting Started

### Prerequisites
1. Install [Python](https://www.python.org/).
2. Clone the repository and navigate to the project root.

### Setup Instructions
1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **Install Dependencies**:
   (Standard Django is used; ensure it's installed or run `pip install django`).
3. **Database Setup**:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create Admin User** (to access `/admin`):
   ```powershell
   python manage.py createsuperuser
   ```
5. **Run Server**:
   ```powershell
   python manage.py runserver
   ```
   Access the app at: `http://127.0.0.1:8000/`

---

## 3. Architecture & File Structure

We follow the **"Fat Service, Skinny View"** pattern to keep code maintainable.

### Root Directory
- `manage.py`: Django's command-line utility.
- `service_day_system/`: Configuration folder (Settings, Main URLs).
- `dashboard/`: The main application folder where our logic lives.

### The `dashboard` App Breakdown
| File  | Purpose | What to do here? |
| :---            | :--- | :--- |
| **`models.py`** | Data Structure     | Define database tables (e.g., `NGOActivity`). Run migrations after changes. |

| **`services/`** | **Business Logic** | All database operations (CRUD) should be here. Views call these functions. |

| **`forms.py`**  | Data Validation    | Define forms for user input. It handles validation and HTML generation. |

| **`views.py`**  | Request Handling   | Receives requests, calls Services, and returns Templates (HTML). |

| **`urls.py`**   | Routing            | Maps URL paths (e.g., `/create/`) to functions in `views.py`. |

| **`templates/`** | UI (HTML)         | The visual part. We use Tailwind CSS for styling. |

---

## 4. How to Implement a New Use Case

Follow these 4 steps to add a new feature:

### Step 1: Update Models (if needed)
Add new fields or classes in `models.py`, then run `makemigrations` and `migrate`.

### Step 2: Add Service Logic
In `dashboard/services/activity_service.py`, add a static method for the new logic (e.g., `register_employee_to_activity`).

### Step 3: Create View & Form
- If you need input, add a form in `forms.py`.
- Create a function in `views.py` that handles the request and calls your service.

### Step 4: Add URL & Template
- Link the view in `dashboard/urls.py`.
- Create the HTML file in `dashboard/templates/dashboard/`.

## 5. Coding Standards
- **Service Layer**: Do NOT write complex SQL queries directly in `views.py`. Always use the Service layer.
- **Styling**: Use Tailwind CSS classes for all UI elements.

