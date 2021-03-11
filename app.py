import os
import json
import requests
from flask import Flask, session, redirect, request, url_for
from requests_oauthlib import OAuth2Session
import pandas as pd

app = Flask(__name__)


OURA_CLIENT_ID     = os.getenv('OURA_CLIENT_ID')#
OURA_CLIENT_SECRET = os.getenv('OURA_CLIENT_SECRET')#

START_DATE = '2021-03-09'
END_DATE = '2021-03-10'

OURA_AUTH_URL = 'https://cloud.ouraring.com/oauth/authorize'
OURA_TOKEN_URL = 'https://api.ouraring.com/oauth/token'


@app.route('/login')
def oura_login():
    """Login to the Oura cloud.
    This will redirect to the login page 
    of the OAuth provider in our case the 
    Oura cloud's login page
    """
    oura_session = OAuth2Session(OURA_CLIENT_ID)

    # URL for Oura's authorization page for specific client
    authorization_url, state = oura_session.authorization_url(OURA_AUTH_URL)

    session['oauth_state'] = state

    return redirect(authorization_url)


@app.route('/callback')
def callback():
    """Callback page
    Get the access_token from response url from Oura. 
    Redirect to the sleep data page.
    """
    oura_session = OAuth2Session(OURA_CLIENT_ID, state=session['oauth_state'])
    session['oauth'] = oura_session.fetch_token(
                        OURA_TOKEN_URL,
                        client_secret=OURA_CLIENT_SECRET,
                        authorization_response=request.url)
    return redirect(url_for('.home'))

@app.route('/sleep') #This is bad? Its OK!
def sleep():
    """Sleep data page
    Get sleep data from the OURA API
    transform sleep data to a pandas DataFrame
    store sleep data as a csv
    return description of the DataFrame
    """
    oauth_token = session['oauth']['access_token']

    sleep_data = requests.get('https://api.ouraring.com/v1/sleep?'
                              'start={}&end={}&access_token={}'
                              .format(START_DATE, END_DATE, oauth_token))
    json_sleep = sleep_data.json()
    pretty_print = json.dumps(json_sleep, indent=4)
    df = pd.DataFrame(json_sleep['sleep'])
    local_path = 'sleep_data_from{}_to{}.csv'.format(START_DATE, END_DATE)
    df.to_csv(local_path)
    return '<title>Oura Ring Sleep Data</title>\n\n<a href="/">home</a>\n\n<h1>Successfully stored sleep data</h1>\n\n\t<p>{}</p>\n\n\tJSON sleep data:\n\n\t<pre>{}</pre>\n\n<a href="/">home</a>\n\n'\
        .format(df.describe(), pretty_print)


@app.route('/activity')
def activity():
    """Activity data page
    Get activity data from the OURA API
    transform activity data to a pandas DataFrame
    store activity data as a csv
    return description of the DataFrame
    """
    oauth_token = session['oauth']['access_token']

    activity_data = requests.get('https://api.ouraring.com/v1/activity?'
                              'start={}&end={}&access_token={}'
                              .format(START_DATE, END_DATE, oauth_token))
    json_activity = activity_data.json()
    pretty_print = json.dumps(json_activity, indent=4)
    df = pd.DataFrame(json_activity['activity'])
    local_path = 'activity_data_from{}_to{}.csv'.format(START_DATE, END_DATE)
    df.to_csv(local_path)
    return '<title>Oura Ring Activity Data</title>\n\n<a href="/">home</a>\n\n<h1>Successfully stored activity data</h1>\n\n\t<p>{}</p>\n\n\tJSON activity data:\n\n\t<pre>{}</pre>\n\n<a href="/">home</a>\n\n'\
        .format(df.describe(), pretty_print)
        
@app.route('/readiness')
def readiness():
    """Readiness data page
    Get readiness data from the OURA API
    transform readiness data to a pandas DataFrame
    store readiness data as a csv
    return description of the DataFrame
    """
    oauth_token = session['oauth']['access_token']

    readiness_data = requests.get('https://api.ouraring.com/v1/readiness?'
                              'start={}&end={}&access_token={}'
                              .format(START_DATE, END_DATE, oauth_token))
    json_readiness = readiness_data.json()
    pretty_print = json.dumps(json_readiness, indent=4)
    df = pd.DataFrame(json_readiness['readiness'])
    local_path = 'readiness_data_from{}_to{}.csv'.format(START_DATE, END_DATE)
    df.to_csv(local_path)
    return '<title>Oura Ring Readiness Data</title>\n\n<a href="/">home</a>\n\n<h1>Successfully stored readiness data</h1>\n\n\t<p>{}</p>\n\n\tJSON readiness data:\n\n\t<pre>{}</pre>\n\n<a href="/">home</a>\n\n'\
        .format(df.describe(), pretty_print)
        
@app.route('/userinfo')
def userinfo():
    """userinfo data page
    Get userinfo data from the OURA API
    transform userinfo data to a pandas DataFrame
    store userinfo data as a csv
    return description of the DataFrame
    """
    oauth_token = session['oauth']['access_token']

    userinfo_data = requests.get('https://api.ouraring.com/v1/userinfo?'
                              '&access_token={}'
                              .format(oauth_token))
    json_userinfo = userinfo_data.json()
    pretty_print = json.dumps(json_userinfo, indent=4)
    return '<title>Oura Ring User Info</title>\n\n<a href="/">home</a>\n\n<h1>Successfully stored userinfo data</h1>\n\n\t<p>{}</p>\n\n\tJSON userinfo data:\n\n\t<pre>{}</pre>\n\n<a href="/">home</a>\n\n'\
        .format(pretty_print)

@app.route('/')
def home():
    """Welcome page of the sleep data app.
    """
    return "<title>Oura Ring Latest Data</title><h1>Welcome to your Oura app</h1>\n\n\t<tr><li><a href='/login'>login</a></li><li><a href='/sleep'>sleep</a></li><li><a href='/activity'>activity</a></li><li><a href='/readiness'>readiness</a></li></tr>"

if __name__ == "__main__":

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=False, host='127.0.0.1', port=8080)