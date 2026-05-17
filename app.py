from flask import Flask, render_template, request, redirect, send_file
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# DATABASE CONNECTION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(100))

    description = db.Column(db.String(255))

    amount = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

# ================= HOME PAGE =================

@app.route('/')
def home():

    expenses = Expense.query.all()

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

    category = request.form['category']

    description = request.form['description']

    amount = request.form['amount']

    new_expense = Expense(

        category=category,

        description=description,

        amount=amount

    )

    db.session.add(new_expense)

    db.session.commit()

    return redirect('/')

# ================= DELETE =================

@app.route('/delete/<int:id>')
def delete_expense(id):

    expense = Expense.query.get(id)

    db.session.delete(expense)

    db.session.commit()

    return redirect('/')

# ================= UPDATE =================

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_expense(id):

    expense = Expense.query.get(id)

    if request.method == 'POST':

        expense.category = request.form['category']

        expense.description = request.form['description']

        expense.amount = request.form['amount']

        db.session.commit()

        return redirect('/')

    return render_template(
        'update_expense.html',
        expense=expense
    )


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

    plt.figure(figsize=(6,6))

    if amounts:
        plt.pie(amounts, labels=labels, autopct='%1.1f%%')

    plt.title("Expense Report")

    plt.savefig('static/chart.png')

    return render_template('reports.html')

# ================= SEARCH =================

@app.route('/search')
def search():

    keyword = request.args.get('keyword')

    expenses = Expense.query.filter(

        (Expense.category.like(f'%{keyword}%')) |

        (Expense.description.like(f'%{keyword}%'))

    ).all()

    total = 0

    for expense in expenses:
        total += expense.amount

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total
    )
# ================= EXPORT CSV =================

@app.route('/export')
def export_csv():

    expenses = Expense.query.all()

    data = []

    for expense in expenses:

        data.append({

            'ID': expense.id,

            'Category': expense.category,

            'Description': expense.description,

            'Amount': expense.amount,

            'Created At': expense.created_at

        })

    df = pd.DataFrame(data)

    path = 'exports/expenses.csv'

    df.to_csv(path, index=False)

    return send_file(path, as_attachment=True)

# ================= FILTER =================

@app.route('/filter')
def filter_expenses():

    date = request.args.get('date')

    month = request.args.get('month')

    year = request.args.get('year')

    category = request.args.get('category')

    query = Expense.query

    if date:

        query = query.filter(
            db.func.date(Expense.created_at) == date
        )

    if month:

        query = query.filter(
            db.extract('month', Expense.created_at) == int(month)
        )

    if year:

        query = query.filter(
            db.extract('year', Expense.created_at) == int(year)
        )

    if category:

        query = query.filter(
            Expense.category.like(f'%{category}%')
        )

    expenses = query.all()

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

    app.run(host='0.0.0.0', port=5000, debug=True)
