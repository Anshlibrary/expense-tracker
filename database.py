import pyodbc

conn = pyodbc.connect(

    'DRIVER={SQL Server};'
    'SERVER=DL-AVL-35;'
    'DATABASE=ExpenseTrackerDB;'
    'UID=sa;'
    'PWD=Avaal2009'

)

cursor = conn.cursor()

print("Database Connected Successfully")