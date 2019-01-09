#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created by: tomas@tomasjerabek.com
# Created on: Sept 3, 2018

import logging
import os
import smtplib
from email.mime.text import MIMEText
import configparser
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime


config = configparser.ConfigParser()
config.read('settings.ini')
login = config['login']
general = config['general']

DOCUMENT_ROOT = general['DOCUMENT_ROOT']
HOSTNAME = general['HOSTNAME']
WEBPORT = int(general['PORT'])
LOG_DIR = general['LOG_DIR']
APP_SECRET = general['SECRET']
USER = login['USER']
PASSWORD = login['PASSWORD']
HOST = login['HOST']
PORT = int(login['PORT'])


if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

#init logging:
logger = logging.getLogger('my_logger')
formatter = logging.Formatter("[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s: %(message)s")
handler = RotatingFileHandler(os.path.join(DOCUMENT_ROOT, LOG_DIR, 'server.log'), maxBytes=5000000, backupCount=5)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


app = Flask(__name__)
app.secret_key = APP_SECRET
csrf = CSRFProtect(app)


@app.context_processor
def inject_year():
    return dict(year=datetime.today().year)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        send_mail(name, email, message)
        flash(u'Thank you for your message. I will get back to you shortly.')
        return redirect(url_for('homepage'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def send_mail(name, email, message):
    try:
        text = u"{0} ({1}) sent following message: \n\n{2}".format(name, email, message)
        msg = MIMEText(text, 'plain')
        msg['Subject'] = u'Message from Contact Form @tomasjerabek.com'
        msg['From'] = USER
        msg['To'] = USER
        s = smtplib.SMTP_SSL(HOST, PORT)
        s.login(USER, PASSWORD)
        s.send_message(msg)
        s.quit()
        logger.info(u"Email from {0} ({1}) sent.".format(name, email))
        logger.info(u"Message: {}.".format(message))
    except Exception as e:
        logger.error(e)

