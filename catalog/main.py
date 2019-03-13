from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Found_Data import Base, FoundationCName, FName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine(
    'sqlite:///found.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open(
    'client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "FOUNDATIONS STORE"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
most = session.query(FoundationCName).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    most = session.query(FoundationCName).all()
    tot = session.query(FName).all()
    return render_template('login.html', STATE=state, most=most, tot=tot)
    # return render_template('myhome.html', STATE=state
    # most=most,tot=tot)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    U1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(U1)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#####
# Home


@app.route('/')
@app.route('/home')
def home():
    most = session.query(FoundationCName).all()
    return render_template('myhome.html', most=most)


@app.route('/Fstore')
def Fstore():
    try:
        if login_session['username']:
            name = login_session['username']
            most = session.query(FoundationCName).all()
            lan = session.query(FoundationCName).all()
            tot = session.query(FName).all()
            return render_template('myhome.html', most=most,
                                   lan=lan, tot=tot, uname=name)
    except:
        return redirect(url_for('showLogin'))


@app.route('/Fstore/<int:fid>/AllCompanys')
def showFound(fid):
    most = session.query(FoundationCName).all()
    lan = session.query(FoundationCName).filter_by(id=fid).one()
    tot = session.query(FName).filter_by(foundationcnameid=fid).all()
    try:
        if login_session['username']:
            return render_template('showFounds.html', most=most,
                                   lan=lan, tot=tot,
                                   uname=login_session['username'])
    except:
        return render_template('showFounds.html',
                               most=most, lan=lan, tot=tot)


@app.route('/Fstore/addFoundCompany', methods=['POST', 'GET'])
def addFoundCompany():
    if request.method == 'POST':
        company = FoundationCName(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(company)
        session.commit()
        return redirect(url_for('Fstore'))
    else:
        return render_template('addFoundCompany.html', most=most)


@app.route('/Fstore/<int:fid>/edit', methods=['POST', 'GET'])
def editFoundCategory(fid):
    editedFound = session.query(FoundationCName).filter_by(id=fid).one()
    creator = getUserInfo(editedFound.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Foundation Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('Fstore'))
    if request.method == "POST":
        if request.form['name']:
            editedFound.name = request.form['name']
        session.add(editedFound)
        session.commit()
        flash("Foundation Category Edited Successfully")
        return redirect(url_for('Fstore'))
    else:
        # most is global variable we can them in entire application
        return render_template('editFoundCategory.html',
                               tb=editedFound, most=most)


@app.route('/Fstore/<int:fid>/delete', methods=['POST', 'GET'])
def deleteFoundCategory(fid):
    tb = session.query(FoundationCName).filter_by(id=fid).one()
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Foundation Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('Fstore'))
    if request.method == "POST":
        session.delete(tb)
        session.commit()
        flash("Foundation Category Deleted Successfully")
        return redirect(url_for('Fstore'))
    else:
        return render_template('deleteFoundCategory.html', tb=tb, most=most)


@app.route('/Fstore/addCompany/addFoundDetails/<string:tbname>/add',
           methods=['GET', 'POST'])
def addFoundDetails(tbname):
    lan = session.query(FoundationCName).filter_by(name=tbname).one()
    # To See whether the user is not the owner of foundation store
    creator = getUserInfo(lan.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showFound', fid=lan.id))
    if request.method == 'POST':
        name = request.form['name']
        shade = request.form['shade']
        quantity = request.form['quantity']
        skintype = request.form['skintype']
        price = request.form['price']
        Foundationdetails = FName(name=name, shade=shade,
                                  quantity=quantity, skintype=skintype,
                                  price=price,
                                  date=datetime.datetime.now(),
                                  foundationcnameid=lan.id,
                                  user_id=login_session['user_id'])
        session.add(Foundationdetails)
        session.commit()
        return redirect(url_for('showFound', fid=lan.id))
    else:
        return render_template('addFoundDetails.html',
                               tbname=lan.name, most=most)


@app.route('/Fstore/<int:fid>/<string:ftbname>/edit',
           methods=['GET', 'POST'])
def editFound(fid, ftbname):
    tb = session.query(FoundationCName).filter_by(id=fid).one()
    Foundationdetails = session.query(FName).filter_by(name=ftbname).one()
    # To See whether the user is not the owner of foundation store
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showFound', fid=tb.id))
    # POST methods
    if request.method == 'POST':
        Foundationdetails.name = request.form['name']
        Foundationdetails.shade = request.form['shade']
        Foundationdetails.quantity = request.form['quantity']
        Foundationdetails.skintype = request.form['skintype']
        Foundationdetails.price = request.form['price']
        Foundationdetails.date = datetime.datetime.now()
        session.add(Foundationdetails)
        session.commit()
        flash("Foundation Edited Successfully")
        return redirect(url_for('showFound', fid=fid))
    else:
        return render_template('editFound.html',
                               fid=fid,
                               Foundationdetails=Foundationdetails, most=most)


@app.route('/Fstore/<int:fid>/<string:ftbname>/delete',
           methods=['GET', 'POST'])
def deleteFound(fid, ftbname):
    tb = session.query(FoundationCName).filter_by(id=fid).one()
    Foundationdetails = session.query(FName).filter_by(name=ftbname).one()
    # See if the logged in user is not the owner of foundation
    creator = getUserInfo(tb.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showFound', fid=tb.id))
    if request.method == "POST":
        session.delete(Foundationdetails)
        session.commit()
        flash("Deleted Foundation Successfully")
        return redirect(url_for('showFound', fid=fid))
    else:
        return render_template('deleteFound.html',
                               fid=fid,
                               Foundationdetails=Foundationdetails,
                               most=most)


@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None, headers={
            'content-type': 'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####
# Json


@app.route('/Fstore/JSON')
def allFoundJSON():
    foundationcategories = session.query(FoundationCName).all()
    category_dict = [c.serialize for c in foundationcategories]
    for c in range(len(category_dict)):
        Foundation = [i.serialize for i in session.query(FName).filter_by(
                     foundationcnameid=category_dict[c]["id"]).all()]
        if Foundation:
            category_dict[c]["foundation"] = Foundation
    return jsonify(FoundationCName=category_dict)

####


@app.route('/Fstore/FoundationCategories/JSON')
def categoriesJSON():
    foundations = session.query(FoundationCName).all()
    return jsonify(FoundationCategories=[c.serialize for c in foundations])

####


@app.route('/Fstore/foundations/JSON')
def fJSON():
    founds = session.query(FName).all()
    return jsonify(foundations=[i.serialize for i in founds])


#####
@app.route(
    '/Fstore/<path:foundation_name>/foundations/JSON')
def categoryfJSON(foundation_name):
    FoundationCategory = session.query(
        FoundationCName).filter_by(name=foundation_name).one()
    Foundations = session.query(
        FName).filter_by(foundationcname=FoundationCategory).all()
    return jsonify(foundationEdtion=[i.serialize for i in Foundations])


#####
@app.route(
    '/Fstore/<path:foundation_name>/<path:edition_name>/JSON')
def ItemJSON(foundation_name, edition_name):
    foundationCategory = session.query(
        FoundationCName).filter_by(name=foundation_name).one()
    foundationEdition = session.query(FName).filter_by(
           name=edition_name, foundationcname=foundationCategory).one()
    return jsonify(foundationEdition=[foundationEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=1429)
