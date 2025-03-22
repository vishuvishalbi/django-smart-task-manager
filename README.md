# Smart Task Manager

A Django-based task management application with AI-powered insights.

## Features

- Task Management: Create, update, and delete tasks with priority levels and due dates
- Notes: Keep track of important information alongside your tasks
- AI Summary: Get AI-powered insights about your productivity and task completion patterns
- User Authentication: Register, login, and manage your profile

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```
   python manage.py migrate
   ```
4. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. Register a new account or login with existing credentials
2. Create tasks with titles, descriptions, due dates, and priority levels
3. Organize and filter tasks by status, due date, or priority
4. Create notes to keep track of important information
5. View AI-generated insights about your productivity

## Technologies Used

- Django 5.1+
- Django REST Framework
- Bootstrap 5
- Font Awesome
- SQLite (development)