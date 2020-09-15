from flask import (render_template as rnd_tmp, url_for, redirect, 
                    flash, send_file, g, Blueprint, current_app)
from packages import db
from packages.cashtrack.helpers import (find_weekrange, find_month_complete, find_month_weekrange, 
                                        getfilter, make_exrate_dict, make_records_dict, 
                                        make_today_transactions, write_to_csv, write_to_zip,
                                        label_icons, label_colors, hardcoded_rates, 
                                        convert_currency_float, convert_usd)
from packages.cashtrack.forms import (TransactionsForm, IncomeForm, BudgetForm, 
                                        InterestForm, CurrencyForm, ClearHistoryForm)
from packages.database import User, Transactions, Budget, DailyRecords, InterestHistory
from flask_login import login_required, current_user
from datetime import date, timedelta
from sqlalchemy import extract, or_
from apscheduler.schedulers.background import BackgroundScheduler
import calendar
import jinja2

cashtrack = Blueprint('cashtrack', __name__)

rates = {}

# Make exchange rate dict, then update it every hour
make_exrate_dict(rates)
sched = BackgroundScheduler(daemon=True)
sched.add_job(make_exrate_dict, 'interval', args=[rates], minutes=180)
sched.start()

# Add the currency symbol and code in used for layout
@cashtrack.before_app_request
def define_currency():
    code = getfilter()
    currency = rates[code]['symbol']
    g.currency = currency
    g.code = code

@jinja2.contextfilter
@cashtrack.app_template_filter()
def convert_currency(self, value, code):
    """Converts value into one of the currencies in exchange rate dict"""
    ex_rate = float(rates[code]['rates'])
    value_inNew = ex_rate * value
    return str(rates[code]['symbol'] + '{:,.2f}'.format(value_inNew))

@cashtrack.route("/transactions", methods=['GET', 'POST'])
@login_required
def transactions():
    form = TransactionsForm()
    rows = Transactions.query.filter_by(user_id=current_user.id, type='Expense', date=date.today()).order_by(Transactions.date.desc())
    today = make_today_transactions(rows)
    if form.validate_on_submit():
        # Checking if Transaction can be made
        if current_user.balance == 0:
            flash('Your Balance is empty. Please add income to record expenses.', 'danger')
            return redirect(url_for('cashtrack.income'))
        if current_user.balance < form.amount.data:
            flash('You cannot afford the transaction. Please add income.', 'danger')
            return redirect(url_for('cashtrack.income'))
        amount = convert_usd(float(form.amount.data), g.code, rates)
        # Record transaction to database
        transactions = Transactions(user_id=current_user.id, amount=amount, type='Expense', category=form.category.data, date=form.date.data, notes=form.notes.data)
        db.session.add(transactions)
        db.session.commit()

        # Update users Total Balance and Expenses
        User.query.get(current_user.id).expenses += amount
        User.query.get(current_user.id).balance -= amount
        db.session.commit()
        
        # Update daily expense
        record = DailyRecords.query.filter_by(user_id=current_user.id, date=form.date.data, type='Expense').first()
        if record:
            record.amount += amount 
            db.session.commit()
        else:
            new = DailyRecords(user_id=current_user.id, amount=amount, type='Expense', date=form.date.data)
            db.session.add(new)
            db.session.commit() 

        # Update if budget for transaction type exists
        budget = Budget.query.filter_by(user_id=current_user.id, category=form.category.data).filter(Budget.status != 'EXPIRED').first()
        if budget:
            if form.date.data >= budget.start_date:
                budget.amount_used += amount
                db.session.commit()

        # Redirect user to dashboard
        flash('Transaction Recorded', 'success')
        return redirect(url_for('cashtrack.overview'))
    return rnd_tmp("add.html", form=form, title="Transactions", icons=label_icons, colors=label_colors, rows=today, length=rows.count(), date=date.today())

@cashtrack.route("/income", methods=['GET', 'POST'])
@login_required
def income():
    form = IncomeForm()
    rows = Transactions.query.filter_by(user_id=current_user.id, type='Income', date=date.today()).order_by(Transactions.id.desc())
    today = make_today_transactions(rows)
    if form.validate_on_submit():
        # Record transactions to database
        amount = convert_usd(float(form.amount.data), g.code, rates)
        transactions = Transactions(user_id=current_user.id, amount=amount, type='Income', category=form.category.data, date=form.date.data, notes=form.notes.data)
        db.session.add(transactions)
        db.session.commit()
        # Update users Balance
        User.query.get(current_user.id).balance += amount
        db.session.commit()
        # Update daily income
        record = DailyRecords.query.filter_by(user_id=current_user.id, date=form.date.data, type='Income').first()
        if record:
            record.amount += amount
            db.session.commit()
        else:
            new = DailyRecords(user_id=current_user.id, amount=amount, type='Income', date=form.date.data)
            db.session.add(new)
            db.session.commit()
        # Redirect user to dashboard
        flash('Income Recorded', 'success')
        return redirect(url_for('cashtrack.overview'))
    return rnd_tmp("add.html", form=form, title="Income", icons=label_icons, colors=label_colors, rows=today, length=rows.count(), date=date.today())

@cashtrack.route("/budget", methods=['GET', 'POST'])
@login_required
def budget():
    Budget.delete_expired()
    rows = Budget.query.filter_by(user_id=current_user.id).filter(Budget.status != 'EXPIRED')
    expired = Budget.query.filter_by(user_id=current_user.id).filter(Budget.status == 'EXPIRED')
    form = BudgetForm()
    if form.validate_on_submit():
        amount = convert_usd(float(form.amount.data), g.code, rates)
        budget = Budget(user_id=current_user.id, amount=amount, category=form.category.data, notes=form.notes.data, start_date=form.startdate.data, end_date=form.enddate.data)
        db.session.add(budget)
        db.session.commit()
        flash('Budget Added!', 'success')
        return redirect(url_for('cashtrack.overview'))
    return rnd_tmp("budget.html", form=form, rows=rows, expires=expired, length=rows.count(), length_ex=expired.count(), icons=label_icons, colors=label_colors)

@cashtrack.route("/interest", methods=['GET', 'POST'])
@login_required
def interest():
    """Calculate and Return Interest Value to User"""
    form = InterestForm()
    placeholder = 'Capital ({})'.format(rates[getfilter()]['symbol'])
    P = I = A = 0
    if form.validate_on_submit():
        P = float(form.capital.data)
        i = float(form.interest_rate.data)
        t = float(form.period.data)
        print(f'{P}, {i}, {t}')
        if str(form.type.data) == 'Simple':
            I = P * (i/100) * t 
            A = I + P
        elif str(form.type.data) == 'Compound':
            A = P * ((1 + i/100)**t)
            I = A - P
        new = InterestHistory(user_id=current_user.id, bank_name=form.name.data, initial_capital=P, interest_rate=i, final_capital=A, period=t, type=form.type.data)
        db.session.add(new)
        db.session.commit()
    return rnd_tmp('interest.html', form=form, P=P, I=I, A=A, placeholder=placeholder)

@cashtrack.route("/records")
@login_required
def records():
    """Shows graphs of user's transactions"""
    income = {}
    expense = {}
    weeklyrecord = {} 
    # Extracting all transactions for the month
    dataMonth = DailyRecords.query.filter(DailyRecords.date.in_(find_month_complete(date.today()))).filter_by(user_id=current_user.id)
    
    # Convert transactions into weekly dictionary
    weekList = find_month_weekrange(date.today())
    print(weekList)
    for week in weekList:
        weeklyrecord.update({ week : {
            'Income': 0,
            'Expense': 0
        }})
    
    for data in dataMonth:
        week = find_weekrange(data.date)
        if week in weekList:
            weeklyrecord[week][data.type] += convert_currency_float(data.amount, g.code, rates)
    
    transactions = Transactions.query.filter_by(user_id=current_user.id)
    for transaction in transactions:
        trans_amount = convert_currency_float(transaction.amount, g.code, rates)
        if transaction.type == 'Income':
            if transaction.category in income:
                income[transaction.category] += trans_amount
            else:
                income.update({transaction.category : trans_amount})
        else:
            if transaction.category in expense:
                expense[transaction.category] += trans_amount
            else:
                expense.update({transaction.category : trans_amount})          
    return rnd_tmp("records.html", income=income, expense=expense, month_data=weeklyrecord, month=calendar.month_name[date.today().month], colors=label_colors)
    
@cashtrack.route("/overview")
@login_required
def overview():
    """" Renders dashboard """
    print(g.code)
    daily = DailyRecords.query.filter(extract('day', DailyRecords.date).between(date.today().day-1, date.today().day+1)).filter_by(user_id=current_user.id)
    recentRecord = {}
    for i in range(-1, 2):
        newDate = date.today()+timedelta(days=i)
        recentRecord.update({newDate.strftime('%d/%m/%Y') : {
            'Income' : 0,
            'Expense': 0
        }})
    for day in daily:
        dateOf = day.date.strftime('%d/%m/%Y')
        recentRecord[dateOf][day.type] += day.amount
    records = make_records_dict(recentRecord, rates)

    monthIncome = monthExpenses = 0
    record_month = DailyRecords.query.filter_by(user_id=current_user.id).filter(extract('month', DailyRecords.date)==date.today().month)
    for record in record_month:
        if record.type == 'Income':
            monthIncome += float(record.amount)
        else:
            monthExpenses += float(record.amount)
    row = Transactions.query.filter_by(user_id=current_user.id).order_by(Transactions.date.desc(),Transactions.id.desc()).limit(5)
    return rnd_tmp('overview.html', record=records, rows=row, icons=label_icons, colors=label_colors, length=row.count(), monthIncome=monthIncome, monthExpenses=monthExpenses, month=calendar.month_name[date.today().month])


@cashtrack.route("/transactions_history", methods=['GET'])
@login_required
def transactions_history():
    # Getting all transactions linked to user id
    row = Transactions.query.filter_by(user_id=current_user.id).order_by(Transactions.date.desc(), Transactions.id.desc())     
    return rnd_tmp("history.html", title='Transactions', rows=row, length=row.count(), icons=label_icons, colors=label_colors)

@cashtrack.route("/interest_history", methods=['GET', 'POST'])
@login_required
def interest_history():
    # Getting all transactions linked to user id
    form = ClearHistoryForm()
    row = InterestHistory.query.filter_by(user_id=current_user.id).order_by(InterestHistory.id.desc())
    if form.validate_on_submit():
        delete_row = InterestHistory.query.filter_by(user_id=current_user.id)
        delete_row.delete()
        db.session.commit()
        flash('Interest History Cleared', 'success')
        return redirect(url_for('cashtrack.interest'))
    return rnd_tmp("history.html", title='Interest', form=form, rows=row, length=row.count(), filter=g.code)

@cashtrack.route("/download")
@login_required
def download():
    """Export a csv file of user's data"""
    transactions = Transactions.query.filter_by(user_id=current_user.id).order_by(Transactions.date)
    budgets = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.id)
    transactions_headers = [
        'date',
        'type',
        'category',
        'amount',
        'notes'
    ]
    budget_headers = [
        'category',
        'amount',
        'amount_used',
        'startdate',
        'enddate',
        'status'
    ]
    trans_data = []
    budget_data = []

    for transaction in transactions:
        trans_data.append({
            'date':transaction.date,
            'type':transaction.type,
            'category':transaction.category,
            'amount': f'{g.currency}{str(convert_currency_float(transaction.amount, g.code,rates))}',
            'notes': transaction.notes
        })
    for budget in budgets:
        budget_data.append({
            'category': budget.category,
            'amount': f'{g.currency}{str(convert_currency(budget.amount, g.code,rates))}',
            'amount_used': f'{g.currency}{str(convert_currency(budget.amount_used, g.code,rates))}',
            'startdate': budget.start_date,
            'enddate': budget.end_date,
            'status': budget.status
        })
    write_to_csv(trans_data, transactions_headers, 'transactions.csv')
    write_to_csv(budget_data, budget_headers, 'budgets.csv')
    write_to_zip('report.zip', ['transactions.csv', 'budgets.csv'])
    file = "../report.zip"
    return send_file(file, as_attachment=True)

@cashtrack.route("/currency", methods=['GET', 'POST'])
@login_required
def change_currency():
    """ Change user's currency """
    form = CurrencyForm()
    if form.validate_on_submit():
        currency = form.rate.data
        redirected = redirect(url_for('cashtrack.overview'))
        redirected.set_cookie('filter', currency)
        symbol = rates[currency]['symbol']
        flash(f'Currency has been changed to {currency} ({symbol})', 'success')
        return redirected
    return rnd_tmp('currency.html', form=form, rates=rates)