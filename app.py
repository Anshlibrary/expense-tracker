from flask import Flask, render_template, request, redirect
import pyodbc

app = Flask(__name__)

# DATABASE CONNECTION
conn = pyodbc.connect(

    'DRIVER={SQL Server};'
    'SERVER=DL-AVL-35;'
    'DATABASE=ExpenseTrackerDB;'
    'UID=sa;'
    'PWD=Avaal2009'

)

cursor = conn.cursor()

# ================= HOME =================

@app.route('/')

def home():

    cursor.execute("SELECT * FROM Expenses")

    expenses = cursor.fetchall()

    total = 0

    for expense in expenses:
        total += expense.amount

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total
    )

# ================= ADD =================

@app.route('/add', methods=['POST'])

def add_expense():

    date = request.form['date']

    category = request.form['category']

    description = request.form['description']

    amount = request.form['amount']

    query = """

    INSERT INTO Expenses
    (expense_date, category, description, amount)

    VALUES (?, ?, ?, ?)

    """

    cursor.execute(
        query,
        (date, category, description, amount)
    )

    conn.commit()

    return redirect('/')

# ================= DELETE =================

@app.route('/delete/<int:id>')

def delete_expense(id):

    cursor.execute(
        "DELETE FROM Expenses WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect('/')

# ================= UPDATE =================

@app.route('/update/<int:id>', methods=['GET', 'POST'])

def update_expense(id):

    if request.method == 'POST':

        date = request.form['date']

        category = request.form['category']

        description = request.form['description']

        amount = request.form['amount']

        query = """

        UPDATE Expenses

        SET
        expense_date=?,
        category=?,
        description=?,
        amount=?

        WHERE id=?

        """

        cursor.execute(
            query,
            (date, category, description, amount, id)
        )

        conn.commit()

        return redirect('/')

    cursor.execute(
        "SELECT * FROM Expenses WHERE id=?",
        (id,)
    )

    expense = cursor.fetchone()

    return render_template(
        'update_expense.html',
        expense=expense
    )

# ================= RUN =================

if __name__ == '__main__':

    app.run(debug=True)