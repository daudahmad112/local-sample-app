from flask import Flask, request, jsonify
import datetime
import pytz
import logging
import math
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize variables
users = {}
lockout_time = 60  # seconds
max_requests = 5


# Define calculator functions
def add(x, y):
    return x + y


def subtract(x, y):
    return x - y


def multiply(x, y):
    return x * y


def divide(x, y):
    if y == 0:
        raise ValueError('Cannot divide by zero')
    return x / y


def power(x, y):
    return pow(x, y)


def sqrt(x):
    if x < 0:
        raise ValueError('Cannot take the square root of a negative number')
    return pow(x, 0.5)


def log(x, base):
    if x <= 0 or base <= 0 or base == 1:
        raise ValueError('Invalid input for log function')
    return math.log(x, base)


# Define routes
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Cloud-based Scientific Calculator API!"


@app.route('/calculate', methods=['POST'])
def calculate():
    # Get user's IP address
    ip_address = request.remote_addr

    # Check if user exists in the dictionary
    if ip_address not in users:
        users[ip_address] = {'requests': 0, 'locked': False, 'timestamp': None}

    # Check if user is locked out
    if users[ip_address]['locked']:
        return 'Your account is currently locked. Please try again in {} seconds.'.format(lockout_time)

    # Get user input
    data = request.get_json()
    operation = data['operation']
    x = data['x']
    y = data['y']

    # Determine the operation to perform
    if operation == 'add':
        result = add(x, y)
    elif operation == 'subtract':
        result = subtract(x, y)
    elif operation == 'multiply':
        result = multiply(x, y)
    elif operation == 'divide':
        result = divide(x, y)
    elif operation == 'power':
        result = power(x, y)
    elif operation == 'sqrt':
        result = sqrt(x)
    elif operation == 'log':
        result = log(x, y)
    else:
        return 'Invalid operation'

    # Increment user's request count
    users[ip_address]['requests'] += 1

    # Check if user has made max_requests number of requests
    if users[ip_address]['requests'] == max_requests:
        users[ip_address]['locked'] = True
        users[ip_address]['timestamp'] = datetime.datetime.now(pytz.utc)
        users[ip_address]['requests'] = 0
        return 'Your account has been locked. Please wait {} seconds.'.format(lockout_time)

    # Log user input and output
    timestamp = datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    log_msg = '{}: x = {}, y = {}, operation = {}, result = {}'.format(timestamp, x, y, operation, result)
    logging.info('{} - {}'.format(ip_address, log_msg))

    # Return result
    return jsonify({'result': result})


# Run the app
if __name__ == '__main__':
    app.run()
