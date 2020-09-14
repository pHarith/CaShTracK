from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField as str_field, SubmitField as smt_field, RadioField, TextAreaField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, optional, ValidationError, NumberRange
from packages.database import Transactions, Budget
from packages.cashtrack.helpers import hardcoded_rates, getfilter
from datetime import date
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms.widgets.html5 import NumberInput
from flask_login import current_user

symbol = hardcoded_rates[getfilter()]['symbol']

# Choices for Radio buttons
transactions_choices = [('Shopping', 'Shopping'), ('Food & Beverages', 'Food & Beverages'),
                        ('Travel','Travel'),('Entertainment', 'Entertainment'),
                        ('Bills', 'Bills'), ('Gifts & Donations', 'Gifts & Donations'),
                        ('Healthcare', 'Healthcare'), ('Investment', 'Investment'), 
                        ('Others', 'Others')]

income_choices = [('Salary', 'Salary'), ('Gifts', 'Gifts'), 
                    ('Awards', 'Awards'), ('Interest', 'Interest'),
                    ('Selling', 'Selling'), ('Others', 'Others')]

currency_choices=[('USD', 'USD (US Dollars)'), ('CAD', 'CAD (Canadian Dollars)'), 
                    ('EUR', 'EUR (European Euros)'), ('KHR', 'KHR (Khmer Riels)')]

class CurrencyForm(FlaskForm):
    rate = SelectField('Currency Rate', 
        choices=currency_choices)
    submit = smt_field('Change Currency')

class TransactionsForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(message="Amount entered is not valid."), NumberRange(min=0, message="Amount cannot be negative.")], widget=NumberInput(min=0, step=1), places=2)
    category = RadioField('Categories', validators=[DataRequired()],
                choices=transactions_choices)
    notes = TextAreaField('Notes', validators=[optional(), Length(max=60)], filters=[lambda v: 'None' if v == '' else v], render_kw={"rows":5, "cols":6})
    date = DateField('Date', validators=[DataRequired()])
    submit = smt_field('Save Transaction')

class IncomeForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(message="Amount entered is not valid."), NumberRange(min=0, message="Amount cannot be negative.")], widget=NumberInput(min=0, step=1), places=2)
    category = RadioField('Categories', validators=[DataRequired()],
                choices=income_choices)
    notes = TextAreaField('Notes', validators=[optional(), Length(max=60)], filters=[lambda v: 'None' if v == '' else v], render_kw={"rows":5, "cols":6})
    date = DateField('Date', validators=[DataRequired()])
    submit = smt_field('Save Income')

class BudgetForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(message="Amount entered is not valid."), NumberRange(min=0, message="Amount cannot be negative.")], widget=NumberInput(min=0, step=1), places=2)
    category = RadioField('Categories', validators=[DataRequired()],
                choices=transactions_choices)
    notes = TextAreaField('Notes', validators=[optional(), Length(max=60)], filters=[lambda v: 'None' if v == '' else v], render_kw={"rows":5, "cols":6})
    startdate = DateField('Start Date', validators=[DataRequired()])
    enddate = DateField('End Date', validators=[DataRequired()])
    submit = smt_field('Add Budget Plans')

    def validate_enddate(self, enddate):
        if self.enddate.data < self.startdate.data:
            self.enddate.errors.append('Please Input a Valid Budget Range.')
            return False
        else: 
            return True
            
    def validate_startdate(self, startdate):
        if self.startdate.data < date.today():
            self.startdate.errors.append('You must set a budget from the present time.')
            return False
        else: 
            return True
    
    def validate_category(self, category):
        category_exists = Budget.query.filter_by(user_id=current_user.id, category=category.data).filter(Budget.status != 'EXPIRED').first()
        if category_exists:
            self.category.errors.append('A budget for this category already exists. Please Check Your Existing Budgets.')
            for error in category.errors:
                flash(error, 'danger')
            return False
        else: 
            return True

class InterestForm(FlaskForm):
    name = str_field('Bank Name', validators=[optional()], filters=[lambda v: None if v == '' else v])
    capital = DecimalField('Account Capital', validators=[DataRequired(message="Amount entered is not valid."), NumberRange(min=0, message="Amount cannot be negative.")], widget=NumberInput(min=0))
    interest_rate = DecimalField('Interest Rate', validators=[DataRequired(message="Interest Rate is not valid."), NumberRange(min=0, message="Interest Rate cannot be negative or zero.")], widget=NumberInput(min=0, step=0.1))
    type = SelectField('Interest Type', choices=[('Simple','Simple'), ('Compound', 'Compound')])
    period = DecimalField('Deposit Duration', validators=[DataRequired(message="Please enter a valid time period. Must be at least half a year."), NumberRange(min=0.5, message="Time Period must at least half a year")], widget=NumberInput(min=0.5, step=0.5))
    submit = smt_field('Calculate Interest')

class ClearHistoryForm(FlaskForm):
    submit = smt_field('Clear Interest History')