#! /usr/bin/env python

from time import strftime as timestamp

from flask import Flask, flash, request, session, redirect, url_for, render_template

app = Flask(__name__)
app.secret_key = 'CHANGE ME'

TIME_FORMAT = '%Y-%m-%d %H:%I:%S'
MESSAGE_LIMIT = 20 

with app.open_resource('badwords', mode='r') as badwords_file:
    badwords = [word.rstrip() for word in badwords_file.readlines()]

with app.open_resource('blockedips', mode='r') as blockedips_file:
    blockedips = [word.rstrip() for word in blockedips_file.readlines()]

messages = []


def is_blocked_user():
    if request.remote_addr in blockedips:
        return True
    else:
        return False

def clear_messages():
    flash('messages cleared')
    messages[:] = []


def get_time():
    return timestamp(TIME_FORMAT)


def insert_message(message):
    if message != None:
        messages.insert(0, {'time': get_time(),
                        'chatter': request.remote_addr,
                        'content': message })
        if len(messages) > MESSAGE_LIMIT:
            messages.pop()


def is_valid_message(message):
    if message == None:
        return True 
    else:
        return message not in badwords and len(message) > 0


@app.route('/', methods=['GET', 'POST'])
def say():
    if is_blocked_user(): 
        return render_template('go_away.html')

    chatter = request.remote_addr
    if 'message' in request.form:
        message = request.form['message']
    else:
        message = None

    if is_valid_message(message):
        insert_message(message)
        return render_template('kala.html', messages=messages)
    else:
        flash('you can\'t say that here')
        return render_template('kala.html', messages=messages)


@app.route('/clear/')
def no_password():
    flash('failed to clear messages. invalid password')
    return redirect('/')


@app.route('/clear/<password>')
def force_clear(password):
    if password == 'CHANGEME':
        clear_messages()
    else:
        flash('failed to clear messages. invalid password')
    return redirect('/')

