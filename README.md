# Habit Tracker Application

A command-line application to help users create, track, and analyze habits systematically.

## Purpose

This habit tracker helps users:
- Create and manage habits with customizable tasks
- Track daily/weekly progress
- Monitor habit streaks and success rates
- Analyze performance through detailed statistics

## Features

- **Habit Management**
  - Create habits with multiple tasks for tracking
  - Set importance levels and repeat intervals
  - Categorization for fine tuning
  - Updating and deleting always possible

- **Task Tracking**
  - Mark tasks as done/ignored
  - Multi-selection
  - Pause habits temporarily
  - Track streaks automatically

- **Analytics**
  - View success rates
  - Track longest streaks
  - Filter and sort habits
  - Monitor progress over time
  - Filter and sort as you please

## Preparation and Installation

1. Clone the repository using git into a folder of your choice

```Bash
git clone https://github.com/DaSteff91/Habit_tracker_code
```

2. Optional: Create a virtual environment in the folder you will use the app

```Bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies from the requirement.txt

```Bash
pip install -r requirements.txt
```
## Usage

1. Start the application using
```Bash
python main.py
```

2. Navigation in the menu
- Arrow keys (↑↓) for menu selection
- Enter to confirm
- Space for multiple selection

3. Workflow for Tracking
- Create habits in Habit Management
- Track tasks in Task Overview
- Check progress in Analytics
- Get details in the provided help.txt file

## Menu Overview

```Bash
Habit Tracker Main Menu
│
├── Task Overview
│   ├── Mark tasks as done
│   ├── Mark tasks as ignored
│   ├── Pause habit
│   ├── Previous/Next Page
│   └── Back to Main Menu
│
├── Habit Management
│   ├── Create New Habit
│   ├── Update Habit
│   ├── Delete Habit
│   ├── Previous/Next Page
│   └── Back to Main Menu
│
├── Analytics
│   ├── Filter Habits
│   ├── Reset View
│   ├── Previous/Next Page
│   └── Back to Main Menu
│
├── Help
└── Exit
```

## Requirements

- Python 3.12+
- SQLite3
- Dependencies in requirements.txt:
    - pytest
    - prettytables
    - questionary

## Code Structure

```Bash
habit-tracker/
├── controllers/
│   ├── habit.py
│   ├── analytics.py
│   └── task.py
│ 
├── models/
│   ├── habit.py
│   ├── analytics.py
│   └── task.py
│ 
├── views/
│   ├── habit_ui.py
│   ├── analytics_ui.py
│   ├── task_ui.py
│   ├── core.py
│   └── menui_ui.py
│ 
├── database/
│   ├── connector.py
│   └── operations.py
│ 
├── utils/
│   ├── help.txt
│   ├── validators.py
│   └── date_utils.py
│ 
├── tests/
│   ├── db.py
│   ├── tests.py
│   └── conftest.py
│ 
├── main.py
├── main.db
├── README.md
└── requirements.txt
```

## Project Structure

Following the model-view-controller pattern and a seperation of concern approach using
- models: Database access layer and business logic
- views: Taking care of the user interface
- controllers: Maintaining interactions between models and views
- database: Ensuring data is stored in a defined manner
- utils: Helper functions and validator
- tests: Test suite for key functionalities

## Database

SQLite database (main.db):

- If not existing: Gets created when launching the main.py
- habit table: habit definitions
- task table: task tracking
- Schema and dummy data in the SQlite file
- A dummy data creater is also provided in the project folder

## Testing

Tests are provided for the basic functionality:
- Creating, updating and deleting a habit
- Inceasing and resetting a streak
- Managing tasks

Run test suite:
```Bash
python -m pytest tests/
```
## License

MIT License - See LICENSE for details