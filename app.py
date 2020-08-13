from flask import Flask, request
import newrelic.agent

newrelic.agent.initialize('newrelic.ini')

app = Flask(__name__)


@app.route('/')
def hello():
    return f'Hello, Heroku!'

if __name__ == 'main':
    app.run()