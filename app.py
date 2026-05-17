from flask import Flask, render_template, request, redirect, send_file
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt

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


# ================= HOME PAGE =================

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

# ================= ADD EXPENSE =================

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


# ================= REPORTS =================
@app.route('/reports')
def reports():

    date = request.args.get('date')
    month = request.args.get('month')
    year = request.args.get('year')
    category = request.args.get('category')

    query = "SELECT category, amount FROM Expenses WHERE 1=1"

    params = []

    if date:
        query += " AND expense_date = ?"
        params.append(date)

    if month:
        query += " AND MONTH(expense_date) = ?"
        params.append(int(month))

    if year:
        query += " AND YEAR(expense_date) = ?"
        params.append(int(year))

    if category:
        query += " AND category LIKE ?"
        params.append(f'%{category}%')

    cursor.execute(query, params)

    expenses = cursor.fetchall()

    categories = {}

    for expense in expenses:

        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount

    labels = list(categories.keys())
    amounts = list(categories.values())

    plt.figure(figsize=(6,6))

    if amounts:
        plt.pie(amounts, labels=labels, autopct='%1.1f%%')

    plt.title("Expense Report")

    plt.savefig('static/chart.png')

    return render_template(
        'reports.html',
        filters={
            'date': date,
            'month': month,
            'year': year,
            'category': category
        }
    )

# ================= SEARCH =================

@app.route('/search', methods=['GET'])
def search():

    keyword = request.args.get('keyword')

    query = """
    SELECT * FROM Expenses
    WHERE category LIKE ?
    OR description LIKE ?
    """

    search_value = 'f'
# ================= EXPORT CSV =================

@app.route('/export')
def export_csv():

    query = "SELECT * FROM Expenses"

    df = pd.read_sql(query, conn)

    path = "exports/expenses.csv"

    df.to_csv(path, index=False)

    return send_file(path, as_attachment=True)

# ================= FILTER =================

@app.route('/filter')
def filter_expenses():

    date = request.args.get('date')
    month = request.args.get('month')
    year = request.args.get('year')
    category = request.args.get('category')

    query = "SELECT * FROM Expenses WHERE 1=1"

    params = []

    if date:
        query += " AND expense_date = ?"
        params.append(date)

    if month:
        query += " AND MONTH(expense_date) = ?"
        params.append(int(month))

    if year:
        query += " AND YEAR(expense_date) = ?"
        params.append(int(year))

    if category:
        query += " AND category LIKE ?"
        params.append(f'%{category}%')

    cursor.execute(query, params)

    expenses = cursor.fetchall()

    total = 0

    for expense in expenses:
        total += expense.amount

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total
    )

# ================= RUN APP =================

if __name__ == '__main__':

    app.run(debug=True)
