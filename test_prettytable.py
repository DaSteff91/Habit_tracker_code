from prettytable import PrettyTable
from database.operations import DatabaseController

db_controller = DatabaseController()

habit_headers = db_controller.get_table_headers('habit')

habits_raw = db_controller.read_data('habit')
habits_as_lists = [list(habit) for habit in habits_raw]
table = PrettyTable()
table.field_names = habit_headers
table.add_rows(habits_as_lists)

print(table)

table = PrettyTable()

task_headers = db_controller.get_table_headers('task')
tasks_raw = db_controller.read_data('task')
tasks_as_lists = [list(task) for task in tasks_raw]

table.field_names = task_headers
table.add_rows(tasks_as_lists)

print(table)

task_headers_short = [habit_headers[1] ,task_headers[2], task_headers[3], task_headers[5], task_headers[6]]
print(len(task_headers_short))

tasks_as_lists_short = [habits_as_lists[0][1], tasks_as_lists[3][1], tasks_as_lists[3][3], tasks_as_lists[3][5], tasks_as_lists[3][6]]
print(len(tasks_as_lists_short))

table = PrettyTable()
table.field_names = task_headers_short
table.add_row(tasks_as_lists_short)
print(table)