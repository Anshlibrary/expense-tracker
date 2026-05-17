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

# ================= REPORTS =================

@app.route('/reports')

def reports():

    expenses = Expense.query.all()

    categories = {}

    for expense in expenses:

        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount

    labels = list(categories.keys())

    amounts = list(categories.values())

    plt.figure(figsize=(5,5))

    plt.pie(amounts, labels=labels, autopct='%1.1f%%')

    plt.savefig('static/chart.png')

    return render_template('reports.html')


# ================= EXPORTS =================

@app.route('/export')

def export_csv():

    expenses = Expense.query.all()

    data = []

    for expense in expenses:

        data.append({
            'Date': expense.date,
            'Category': expense.category,
            'Description': expense.description,
            'Amount': expense.amount
        })

    df = pd.DataFrame(data)

    path = 'exports/expenses.csv'

    df.to_csv(path, index=False)

    return send_file(path, as_attachment=True)


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