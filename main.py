import PySimpleGUI as sg
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import os

# SETUP
############################################################################################################
sg.theme('Dark')

# Get the current month and year
current_month = datetime.datetime.now().strftime('%Y_%m')
current_month_text = datetime.datetime.now().strftime('%B %Y')

# Function to construct the filename of the database for a specific month
def get_database_filename(month):
    return f'expenses_{month}.db'

# Function to check if the database file for a specific month exists
def does_database_exist(month):
    database_filename = get_database_filename(month)
    return os.path.exists(database_filename)

# Create a database connection
database_filename = get_database_filename(current_month)
conn = sqlite3.connect(database_filename)
cursor = conn.cursor()

# Create the database table if it doesn't exist for current month
cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                    id INTEGER PRIMARY KEY,
                    Item TEXT,
                    NumberOfItems INTEGER,
                    Details TEXT,
                    Cost REAL
                )''')

font = ('Arial', 14)

# Define layout of GUI
layout_gui = [
    [sg.Text(f'Current Month: {current_month_text}', key='-MONTH_LABEL-', font=font)],
    [sg.Button('<', key='-PREV-', font=font), sg.Button('>', key='-NEXT-', font=font)],
    [sg.Text('Item:', size=(15, 1), font=font), sg.Input(key='-ITEM-', size=(30, 1))],
    [sg.Text('Number of Items:', size=(15, 1), font=font), sg.Input(key='-NOITEMS-', size=(30, 1))],
    [sg.Text('Note:', size=(15, 1), font=font), sg.Input(key='-NOTE-', size=(30, 1))],
    [sg.Text('Cost:', size=(15, 1), font=font), sg.Input(key='-COST-', size=(30, 1))],
    [sg.Button('Add Expense'), sg.Button('Delete Expense'), sg.Button('Exit')],
    [sg.Text('Expenses', font=font)],
    [sg.Table(values=[], headings=['ID', 'Item', 'No. Items', 'Note', 'Cost'],
              key='-EXPENSES-', justification='center', num_rows = 10, font=font,
              auto_size_columns=False, def_col_width = 20, max_col_width = 100)]
]

window = sg.Window('Expense Tracker', layout_gui, finalize=True)
window.maximize()
############################################################################################################

# FUNCTIONALITY
############################################################################################################
# Display new expenses table for the specified month
def display_expenses(month):
    database_filename = get_database_filename(month)
    conn = sqlite3.connect(database_filename)
    cursor = conn.cursor()
    
    # Create the Expenses table if it doesn't exist for that month
    cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                        id INTEGER PRIMARY KEY,
                        Item TEXT,
                        NumberOfItems INTEGER,
                        Details TEXT,
                        Cost REAL
                    )''')

    # Query database and display in GUI
    cursor.execute('SELECT id, Item, NumberOfItems, Details, Cost FROM Expenses ORDER BY id ASC')
    expenses = cursor.fetchall()
    window['-EXPENSES-'].update(values=expenses)
    conn.close()

    # Extract id for each row
    return [row[0] for row in expenses]

# Query database to delete selected row in GUI
def delete_expense(selected_rows):
    for row_id in selected_rows:
        cursor.execute('DELETE FROM Expenses WHERE id=?', (row_id,))
        conn.commit()

# Update GUI label for current month and year
def update_month_label(month):
    month_text = datetime.datetime.strptime(month, '%Y_%m').strftime('%B %Y')
    window['-MONTH_LABEL-'].update(value=f'Current Month: {month_text}')

# Calculates previous month
def get_previous_month(current_month):
    current_date = datetime.datetime.strptime(current_month, '%Y_%m')
    previous_month = current_date - relativedelta(months=1)
    return previous_month.strftime('%Y_%m')

# Calculates next month
def get_next_month(current_month):
    current_date = datetime.datetime.strptime(current_month, '%Y_%m')
    next_month = current_date + relativedelta(months=1)
    return next_month.strftime('%Y_%m')

# Validate input values before inserting into the database
def validate_input(item, no_items, note, cost):
    if not item or not isinstance(item, str):
        sg.popup('Please enter a valid item.')
        return False

    if not no_items.isdigit():
        sg.popup('Please enter a valid number of items.')
        return False

    if not isinstance(note, str):
        sg.popup('Please enter a valid note.')
        return False

    try:
        float_cost = float(cost)
        if float_cost <= 0:
            sg.popup('Please enter a valid cost.')
            return False
    except ValueError:
        sg.popup('Please enter a valid cost.')
        return False

    return True
############################################################################################################

# EVENT LOOP
############################################################################################################
while True:
    display_expenses(current_month)
    event, values = window.read()

    # Monitor for Exit button activation or closed window
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    # Monitor for Add Expense button activation
    if event == 'Add Expense':

        # Get user input 
        item = values['-ITEM-']
        no_items = values['-NOITEMS-']
        note = values['-NOTE-']
        cost = values['-COST-']

        # Validate input
        if not validate_input(item, no_items, note, cost):
            continue

        # Query database and add inputs
        cursor.execute('INSERT INTO Expenses (Item, NumberOfItems, Details, Cost) VALUES (?, ?, ?, ?)',
                       (item, no_items, note, cost))
        conn.commit()

        # Update the display
        display_expenses(current_month)

    # Monitor for Delete Expense button activation
    elif event == 'Delete Expense':

        # Get index of selected row
        selected_rows = window['-EXPENSES-'].SelectedRows
        if selected_rows:

            #Get row ids and delete
            row_ids = display_expenses(current_month)
            selected_row_ids = [row_ids[index] for index in selected_rows]
            delete_expense(selected_row_ids)


    # Monitor for previous month button activation
    elif event == '-PREV-':

        # Update current month and the label
        current_month = get_previous_month(current_month)
        update_month_label(current_month)

        database_filename = get_database_filename(current_month)
        conn = sqlite3.connect(database_filename)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                                id INTEGER PRIMARY KEY,
                                Item TEXT,
                                NumberOfItems INTEGER,
                                Details TEXT,
                                Cost REAL
                            )''')

    # Monitor for next month button activation
    elif event == '-NEXT-':

        # Update current month and the label
        current_month = get_next_month(current_month)
        update_month_label(current_month)

        database_filename = get_database_filename(current_month)
        conn = sqlite3.connect(database_filename)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                                id INTEGER PRIMARY KEY,
                                Item TEXT,
                                NumberOfItems INTEGER,
                                Details TEXT,
                                Cost REAL
                            )''')

############################################################################################################

window.close()
conn.close()