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
  - Create habits with multiple tasks
  - Set importance levels and repeat intervals
  - Update habit details
  - Delete habits and associated tasks

- **Task Tracking**
  - Mark tasks as done/ignored
  - Handle related tasks together
  - Pause habits temporarily
  - Track streaks automatically

- **Analytics**
  - View success rates
  - Track longest streaks
  - Filter and sort habits
  - Monitor progress over time

## Preparation and Installation

1. Clone the repository using git

2. Create a virtual environment (recommended) 

3. Install dependencies from the requirement.txt

## Usage

1. Start the application using
```Bash
python main.py
```

2. Navigation
- Arrow keys (↑↓) for menu selection
- Enter to confirm
- Space for multiple selection

3. Workflow for Tracking
- Create habits in Habit Management
- Track tasks in Task Overview
- Check progress in Analytics

## Requirements
- Python 3.12+
- SQLite3
- Dependencies in requirements.txt:
    - pytest
    - rich
    - questionary

## Projet Structure

```Bash
habit-tracker/
├── controllers/
│   ├── habit.py
│   └── task.py
├── models/
│   ├── habit.py
│   └── task.py
├── utils/
│   ├── validators.py
│   └── date_utils.py
├── tests/
├── main.py
└── README.md
```

## Project and Code Structure

Following the model-view-controll pattern and a seperation of concern approach using
- models: Database operations and business logic
- views: Taking care of the user interface
- controllers: Maintaining interactions between models and views
- database: Ensuring data is stored in a defined manner
- utils: Helper functions and validator
- tests: Test suite for key functionalities

## Database
SQLite database (main.db):

- habit table: habit definitions
- task table: task tracking

## Testing

Run test suite:
```Bash
python -m pytest tests/
```
## License
