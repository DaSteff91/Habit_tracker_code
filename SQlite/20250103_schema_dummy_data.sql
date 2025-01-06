-- habit definition

CREATE TABLE IF NOT EXISTS habit (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                created TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT,
                importance TEXT NOT NULL,
                repeat TEXT NOT NULL,
                tasks INT NOT NULL,
                tasks_description TEXT NOT NULL,
                streak INT NOT NULL DEFAULT 0,
                streak_reset_count INT NOT NULL DEFAULT 0,
                longest_streak INT NOT NULL DEFAULT 0 
            );

-- task definition

CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY,
                habit_id INTEGER NOT NULL,
                task_number INTEGER NOT NULL,
                task_description TEXT NOT NULL,
                created TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habit (id)
            );