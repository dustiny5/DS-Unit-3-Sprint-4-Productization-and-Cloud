from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import openaq


"""OpenAQ Air Quality Dashboard with Flask."""

# Instantiate flask and DB
APP = Flask(__name__)
DB = SQLAlchemy(APP)

# Route to homepage
@APP.route('/')
def root():
    """Base view."""
    # Shows only above 10
    records = Record.query.filter(Record.value >= 10).all()
    return render_template('base.html', title='Home', records=records)


# Setup Database
APP.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')


# Refresh
@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'

# Record Object
class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return 'Datetime:{} and Value: {}'.format(self.datetime, self.value)

# Get the openaq api
api = openaq.OpenAQ()
status, body = api.measurements(city='Los Angeles', parameter='pm25')

# Put utc,value in a tuple then append to a list
my_list = []
for i in range(len(body['results'])):
    (utc, value) = body['results'][i]['date']['utc'], body['results'][i]['value']
    my_list.append((utc, value))

# Populate database
for i,j in my_list:
    db_record = Record(datetime=i, value=j)
    DB.session.add(db_record)
DB.session.commit()
