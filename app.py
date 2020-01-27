from twilio.rest import Client
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from apscheduler.schedulers.background import BackgroundScheduler

import config
import random
import os

# Init App + Scheduler
app = Flask(__name__)
schedule = BackgroundScheduler(daemon=True)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init Marshmallow
ma = Marshmallow(app)


class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quote = db.Column(db.String())

    def __init__(self, quote):
        self.quote = quote

   


class QuoteSchema(ma.Schema):
    class Meta:
        fields = ('id', 'quote')


# Init Schema
quote_schema = QuoteSchema()
quotes_schema = QuoteSchema(many=True)


# Routes
@app.route('/quote', methods=['GET'])
def get_all_quotes():
    all_quotes = Quote.query.all()
    result = quotes_schema.dump(all_quotes)
    return jsonify(result)

@app.route('/quote', methods=['POST'])
def add_quote():
    quote = request.json['quote']
    new_quote = Quote(quote)
    db.session.add(new_quote)
    db.session.commit()
    return quote_schema.jsonify(new_quote)


@app.route('/quote/<id>/', methods=['GET'])
def get_quote(id):
    quote = Quote.query.get(id)
    result = quote_schema.dump(quote)
    return jsonify(result)


@app.route('/quote/<id>/', methods=['DELETE'])
def delete_quote(id):
    quote = Quote.query.get(id)
    db.session.delete(quote)
    db.session.commit()

    return quote_schema.jsonify(quote)


# Create client for twilio
client = Client(config.acct, config.key)

def send_message():
    quote = get_daily_quote()
    client.messages.create(to=config.mynum, from_=config.twilnum, body=quote)


def get_daily_quote():
    totalQuotes = Quote.query.count()
    number = random.randrange(totalQuotes)
    quote = Quote.query.get(number)
    result = quote_schema.dump(quote)
    return result["quote"]


#  Add Job to Scheduler
schedule.add_job(send_message, trigger='cron', hour='8')
schedule.start()



# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)



