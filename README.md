📘 Simple Learning Management System (LMS)
1. Project Scope

The Simple LMS will be a web application that enables:

Students to enroll in courses, access lessons, take quizzes, and track progress.

Instructors/Admins to create and manage courses, lessons, and quizzes.

System to store enrollment data, quiz scores, and completion progress.

Core Features

User authentication (student/instructor roles)

Course management (title, description, instructor)

Lesson management (text, video, attachments)

Quiz system (questions, multiple choice answers, scoring)

Student enrollment

Progress tracking (completed lessons, quiz scores)

Basic reporting dashboard (student progress per course)

Nice-to-Have Features (Future Roadmap)

Discussion forums for each course

Certificates of completion

Search and filtering for courses

REST API endpoints for mobile clients

2. Tech Stack

Backend: Django (Python 3.10+)

Database: PostgreSQL

Frontend: Django Templating with HTML5 + CSS3 (Bootstrap/Tailwind optional for styling)

Hosting: Render/Heroku (for simplicity in deployment)

Version Control: Git + GitHub

AI Tools:

Zed, Cursor, Trae → AI-assisted coding & refactoring

ChatGPT → brainstorming, schema design, documentation, testing plans

Coderabbit → automated code review suggestions

3. Database Schema (Initial Draft)
Users

User (extends Django’s AbstractUser)

role → ["student", "instructor"]

Courses & Lessons

Course

title

description

instructor (FK to User)

Lesson

course (FK to Course)

title

content (text/HTML)

order

Quizzes

Quiz

lesson (FK to Lesson)

title

Question

quiz (FK to Quiz)

text

Answer

question (FK to Question)

text

is_correct (boolean)

Student Progress

Enrollment

student (FK to User)

course (FK to Course)

date_enrolled

LessonProgress

enrollment (FK to Enrollment)

lesson (FK to Lesson)

completed (boolean)

QuizAttempt

student (FK to User)

quiz (FK to Quiz)

score

4. Feature Development Strategy

Phase 1: Setup project, user roles, course/lesson CRUD

Phase 2: Quizzes (questions, answers, scoring)

Phase 3: Enrollment & tracking

Phase 4: Basic reporting/dashboard

Phase 5: Styling & polishing

5. Testing

Unit Tests → Django’s TestCase for models, views, and forms

Integration Tests → simulate student enrolling, completing lessons, taking quizzes

AI-Assisted Tests → Use AI IDEs to generate boilerplate tests, then refine manually

Example prompt to AI:

Generate Django unit tests for the QuizAttempt model ensuring score calculation works and multiple attempts are tracked per user.

6. Documentation & Maintenance
README.md

Maintained as a living document

Updated after each feature phase using AI-assisted summaries

Example prompt to AI:

Summarize the new quiz feature implementation into a changelog format for README.md. Keep it concise.

Docstrings

Google-style docstrings for all models, views, and utils

AI IDEs (Zed/Cursor) will be used to auto-generate docstrings, then refined manually

Example prompt:

Generate Google-style docstrings for the Lesson model in Django. Include fields and relationships.

Inline Comments

Short, targeted explanations for complex logic only

Avoid clutter by not commenting obvious code

Example prompt:

Suggest inline comments for this Django view that calculates student progress, focusing on where the logic might confuse a new developer.

Coderabbit (AI PR Reviewer)

Will be used to review pull requests and suggest refactoring

Enforce docstring, testing, and readability standards

Example Coderabbit setup prompt:

Configure Coderabbit to enforce PEP8, require docstrings for all new functions, and flag duplicate code in views.py.

7. Example Prompts Library

Here are reusable prompts for AI tools throughout the project:

Schema Design:
"Propose a Django model schema for courses, lessons, and quizzes with proper relationships and foreign keys."

Boilerplate Code:
"Generate a Django view for students to enroll in a course, ensuring duplicate enrollments are prevented."

UI Enhancements:
"Suggest simple Bootstrap classes to make the course list view responsive."

Testing:
"Write unit tests for Enrollment model ensuring that a user cannot enroll twice in the same course."

Refactoring:
"Refactor this Django view into class-based views while keeping existing functionality intact."
