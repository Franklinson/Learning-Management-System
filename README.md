# 📘 Simple Learning Management System (LMS)

A robust and intuitive web application designed to facilitate online learning. This LMS enables students to enroll in courses, access lessons, complete quizzes, and track their progress seamlessly. Instructors and administrators gain powerful tools to create, manage, and deliver educational content efficiently.

## Table of Contents

1.  [Introduction](#1-introduction)
    *   [Project Overview](#project-overview)
    *   [Core Features](#core-features)
    *   [Future Roadmap](#future-roadmap)
2.  [Tech Stack](#2-tech-stack)
3.  [Database Schema](#3-database-schema)
4.  [Development Strategy](#4-development-strategy)
5.  [Testing Strategy](#5-testing-strategy)
6.  [Documentation & Maintenance](#6-documentation--maintenance)
7.  [Example AI Prompts Library](#7-example-ai-prompts-library)
8.  [Getting Started](#8-getting-started)

## 1. Introduction

### Project Overview

The Simple LMS is envisioned as a comprehensive web application for managing learning content and student interactions. It will serve two primary user types:

*   **Students**: Can enroll in courses, access lesson materials (text, video, attachments), take interactive quizzes, and monitor their academic progress.
*   **Instructors/Admins**: Have the capability to create new courses, add lessons, design quizzes, and manage existing educational content.
*   **System**: Designed to securely store and manage all essential data, including enrollment records, quiz scores, and student completion progress.

### Core Features

*   **User Authentication**: Secure login and role management (student/instructor).
*   **Course Management**: Create, view, update, and delete courses (title, description, associated instructor).
*   **Lesson Management**: Manage lessons within courses (text content, video links, attachments, display order).
*   **Quiz System**: Develop quizzes with multiple-choice questions, define correct answers, and automate scoring.
*   **Student Enrollment**: Allow students to enroll in available courses.
*   **Progress Tracking**: Monitor completed lessons and quiz scores for each student.
*   **Basic Reporting Dashboard**: Overview of student progress per course.

### Future Roadmap (Nice-to-Have Features)

*   Discussion forums for each course.
*   Automated certificates of completion.
*   Advanced search and filtering functionalities for courses.
*   REST API endpoints to support mobile clients.

## 2. Tech Stack

The project leverages a modern and robust set of technologies to ensure scalability, maintainability, and a smooth development experience.

*   **Backend**: Django (Python 3.10+)
*   **Database**: PostgreSQL
*   **Frontend**: Django Templating with HTML5 + CSS3 (Bootstrap/Tailwind optional for styling)
*   **Hosting**: Render/Heroku/Railway/Vercel (for simplified deployment)
*   **Version Control**: Git + GitHub

### AI Tools Utilized

*   **Zed, Cursor, Trae**: For AI-assisted coding, refactoring, and general development support.
*   **ChatGPT**: Brainstorming, database schema design, documentation generation, and test planning.
*   **Coderabbit**: Automated code review suggestions to enhance code quality.

## 3. Database Schema (Initial Draft)

The following outlines the initial database schema design, leveraging Django's ORM capabilities for robust data management.

### Users

*   **User** (extends Django’s `AbstractUser`)
    *   `role` → `["student", "instructor"]`

### Courses & Lessons

*   **Course**
    *   `title` (string)
    *   `description` (text)
    *   `instructor` (FK to User)

*   **Lesson**
    *   `course` (FK to Course)
    *   `title` (string)
    *   `content` (text/HTML)
    *   `order` (integer)

### Quizzes

*   **Quiz**
    *   `lesson` (FK to Lesson)
    *   `title` (string)

*   **Question**
    *   `quiz` (FK to Quiz)
    *   `text` (text)

*   **Answer**
    *   `question` (FK to Question)
    *   `text` (text)
    *   `is_correct` (boolean)

### Student Progress

*   **Enrollment**
    *   `student` (FK to User)
    *   `course` (FK to Course)
    *   `date_enrolled` (datetime)

*   **LessonProgress**
    *   `enrollment` (FK to Enrollment)
    *   `lesson` (FK to Lesson)
    *   `completed` (boolean)

*   **QuizAttempt**
    *   `student` (FK to User)
    *   `quiz` (FK to Quiz)
    *   `score` (integer)

## 4. Development Strategy

The project will be developed in an agile, phased approach to ensure steady progress and deliver core functionalities early.

*   **Phase 1**: Project setup, basic user roles, Course and Lesson CRUD (Create, Read, Update, Delete) operations.
*   **Phase 2**: Implementation of the Quiz system (questions, answers, scoring logic).
*   **Phase 3**: Student Enrollment and progress tracking functionalities.
*   **Phase 4**: Development of the basic reporting dashboard.
*   **Phase 5**: Frontend styling, polishing, and overall user experience enhancements.

## 5. Testing Strategy

A comprehensive testing strategy is crucial to ensure the reliability and stability of the LMS.

*   **Unit Tests**: Django’s `TestCase` will be used for thorough testing of models, views, and forms.
*   **Integration Tests**: Simulate real-world user flows, such as a student enrolling in a course, completing lessons, and taking quizzes.
*   **AI-Assisted Tests**: AI IDEs will be utilized to generate boilerplate test cases, which will then be manually refined and expanded.

**Example AI Prompt for Testing**:
```/dev/null/example.md#L1-2
Generate Django unit tests for the QuizAttempt model ensuring score calculation works and multiple attempts are tracked per user.
```

## 6. Documentation & Maintenance

Maintaining high-quality documentation is a priority to ensure project longevity and ease of collaboration.

*   **`README.md`**: This document will be kept as a living document, regularly updated after each feature phase using AI-assisted summaries.

    **Example AI Prompt for README updates**:
    ```/dev/null/example.md#L1-2
    Summarize the new quiz feature implementation into a changelog format for README.md. Keep it concise.
    ```

*   **Docstrings**: Google-style docstrings will be mandatory for all models, views, and utility functions. AI IDEs (Zed/Cursor) will assist in auto-generating these, followed by manual refinement.

    **Example AI Prompt for Docstrings**:
    ```/dev/null/example.md#L1-2
    Generate Google-style docstrings for the Lesson model in Django. Include fields and relationships.
    ```

*   **Inline Comments**: Short, targeted explanations will be used sparingly for complex logic only, avoiding unnecessary clutter.

    **Example AI Prompt for Inline Comments**:
    ```/dev/null/example.md#L1-2
    Suggest inline comments for this Django view that calculates student progress, focusing on where the logic might confuse a new developer.
    ```

*   **Coderabbit (AI PR Reviewer)**: Will be configured to review pull requests, suggest refactoring improvements, and enforce coding standards (PEP8, docstring requirements, code readability, and flagging duplicate code).

    **Example Coderabbit setup prompt**:
    ```/dev/null/example.md#L1-2
    Configure Coderabbit to enforce PEP8, require docstrings for all new functions, and flag duplicate code in views.py.
    ```

## 7. Example AI Prompts Library

A collection of reusable prompts to guide AI tools throughout the project lifecycle.

*   **Schema Design**:
    ```/dev/null/example.md#L1-2
    Propose a Django model schema for courses, lessons, and quizzes with proper relationships and foreign keys.
    ```
*   **Boilerplate Code**:
    ```/dev/null/example.md#L1-2
    Generate a Django view for students to enroll in a course, ensuring duplicate enrollments are prevented.
    ```
*   **UI Enhancements**:
    ```/dev/null/example.md#L1-2
    Suggest simple Bootstrap classes to make the course list view responsive.
    ```
*   **Testing**:
    ```/dev/null/example.md#L1-2
    Write unit tests for Enrollment model ensuring that a user cannot enroll twice in the same course.
    ```
*   **Refactoring**:
    ```/dev/null/example.md#L1-2
    Refactor this Django view into class-based views while keeping existing functionality intact.
    ```

## 8. Getting Started

This section will contain instructions on how to set up and run the project locally.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Franklinson/Learning-Management-System.git
    cd Learning-Management-System
    ```
2.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt # (assuming a requirements.txt will be created)
    ```
4.  **Database Setup**:
    *   Run migrations: `python manage.py migrate`
5.  **Create a superuser**:
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server**:
    ```bash
    python manage.py runserver
    ```
    Access the application at `http://127.0.0.1:8000/`.
