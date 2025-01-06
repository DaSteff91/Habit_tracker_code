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

(It is assumed you already have git functionality available - otherwise [get git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for your operating system before continuing)

1. Clone the repository using git

```Bash
git clone [https://github.com/DaSteff91/Habit_tracker_code]
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

## Requirements

- Python 3.12+
- SQLite3
- Dependencies in requirements.txt:
    - pytest
    - rich
    - questionary

## Code Structure

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

- habit table: habit definitions
- task table: task tracking

## Testing

Run test suite:
```Bash
python -m pytest tests/
```
## License

MIT License - See LICENSE for details