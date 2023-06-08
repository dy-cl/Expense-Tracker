import PySimpleGUI as sg
import sqlite3

#SETUP
############################################################################################################
sg.theme('Dark')

#Create database
conn = sqlite3.connect('expenses.db')

cursor = conn.cursor()

#Create database if not already existing
cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses (
                                            id INTEGER PRIMARY KEY,
                                            Item TEXT,
                                            NumberOfItems INTEGER,
                                            Details TEXT,
                                            Cost REAL
                                        )''')

font = ('Arial', 12)

#Define layout of GUI
layout_gui = [
    [sg.Text('Item:', size=(10, 1), font=font), sg.Input(key='-ITEM-', size=(20, 1))],
    [sg.Text('Number of Items:', size=(10, 1), font=font), sg.Input(key='-NOITEMS-', size=(20, 1))],
    [sg.Text('Note:', size=(10, 1), font=font), sg.Input(key='-NOTE-', size=(20, 1))],
    [sg.Text('Cost:', size=(10, 1), font=font), sg.Input(key='-COST-', size=(20, 1))],
    [sg.Button('Add Expense'), sg.Button('Delete Expense'), sg.Button('Exit')],
    [sg.Text('Expenses', font=font)],
    [sg.Table(values=[], headings=['ID', 'Item', 'No. Items', 'Note', 'Cost'],
              key='-EXPENSES-', justification='left', num_rows=10, font=font,
              auto_size_columns=True, col_widths=[15, 10, 25, 10])]
]

window = sg.Window('Expense Tracker', layout_gui, finalize = True)
############################################################################################################

#FUNCTIONALITY 
############################################################################################################
#Display new expenses table
def update_expenses_table():
    cursor.execute('SELECT id, Item, NumberOfItems, Details, Cost FROM Expenses ORDER BY id ASC')
    expenses = cursor.fetchall()
    window['-EXPENSES-'].update(values = expenses)
    return [row[0] for row in expenses]

def delete_expense(selected_rows):
    for row_id in selected_rows:
        cursor.execute('DELETE FROM Expenses WHERE id=?', (row_id,))
        conn.commit()
############################################################################################################

#EVENT LOOP
############################################################################################################
while True:
    update_expenses_table()
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'Add Expense':
        item = values['-ITEM-']
        no_items = values['-NOITEMS-']
        note = values['-NOTE-']
        cost = values['-COST-']

        cursor.execute('INSERT INTO Expenses (Item, NumberOfItems, Details, Cost) VALUES (?, ?, ?, ?)', (item, no_items, note, cost))
        conn.commit()

        update_expenses_table()

    elif event == 'Delete Expense':
        selected_rows = window['-EXPENSES-'].SelectedRows
        if selected_rows:
            row_ids = update_expenses_table()
            selected_row_ids = [row_ids[index] for index in selected_rows]
            delete_expense(selected_row_ids)
############################################################################################################
 
window.close()
conn.close()