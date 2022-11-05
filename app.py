from json import dumps
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import io
# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import pandas as pd

app = Flask(
    __name__, 
    template_folder='frontend',
    static_url_path='', 
    static_folder='frontend',
    )
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"


# ------------------------------------------
# Pass variables as argument
# ------------------------------------------
from markupsafe import escape

@app.route('/user')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {escape(username)}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'
# ------------------------------------------

# ------------------------------------------
# HTTP Methods
# ------------------------------------------
# from flask import request

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return "do_the_login()"
#     else:
#         return "show_the_login_form()"

#             # OR

# @app.get('/login')
# def login_get():
#     return "show_the_login_form()"

# @app.post('/login')
# def login_post():
#     return "do_the_login()"
# ------------------------------------------

# ------------------------------------------
# Reading cookies
# ------------------------------------------

# @app.route('/')
# def reacCoocie():
#     username = request.cookies.get('username')
#     # use cookies.get(key) instead of cookies[key] to not get a
#     # KeyError if the cookie is missing.
# ------------------------------------------

# ------------------------------------------
# Storing cookies
# ------------------------------------------

# @app.route('/')
# def writeCoocie():
#     resp = "make_response(render_template(...))"
#     resp.set_cookie('username', 'the username')
#     return resp
# ------------------------------------------






# ------------------------------------------
# HTTP Methods
# ------------------------------------------
from flask import request
import bcrypt
from util import *
from yml_handler.readdata import *


@app.route("/")
def uploadFile():
    return render_template('uploadFile.html', name="uploadFile")

@app.route('/register', methods=['POST'])
def register():
    enteredInfo = getenteredInfo(request)
    username = enteredInfo.get("username")
    password = enteredInfo.get("password")
    dbname = get_database()
    collection_name = dbname["userCredential"]
    user = collection_name.find_one({"username" : username})
    if user == None:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    
        collection_name.insert_one({"username" : username, "password" : hashed_password})
        return {"message" : "Thanks for register."}
    else:
        return {"message" : "User already exists. Please login or try with another user name."}



@app.route('/login', methods=['POST'])
def login():
    try:
        enteredInfo = getenteredInfo(request)
        username = enteredInfo.get("username")
        password = enteredInfo.get("password")
        dbname = get_database()
        collection_name = dbname["userCredential"]
        user_found = collection_name.find_one({"username" : username})
        # print(str(user_found.get("password")))

        if bcrypt.checkpw(password.encode('utf-8'), user_found.get("password")):
            # request.seassion({"username":username})
            access_token = create_access_token(identity=username)
            return dataresponse("login", {"message" : "Login Successful", "access_token":access_token} )
        return dataresponse("login", {"message" : "Invalid credential"})
    except Exception as e:
        return errorresponse("login", e)


@app.route('/getUsers', methods=['GET'])
# @jwt_required
def getUsers():
    try:
        users = get_database()['userCredential'].find({},{'password':0, '_id':0})     
        return dataresponse("getUsers", list(users))
    except Exception as e:
        return errorresponse("getUsers", e)

@app.route('/get_csv_data', methods=['POST'])
def get_csv_data():
    try:
        raw_data = request.files['file'].read()  # In form data, I used "myfile" as key.    
        data = yaml.load(raw_data, Loader=SafeLoader)
        df  = yml_to_df(app, data)
        s   = io.StringIO()
        df.to_csv(s)
        csv = s.getvalue()# pd.read_csv(app.root_path+'/yml_handler/output.csv')
        response = make_response(csv)
        cd = 'attachment; filename=mycsv.csv'
        response.headers['Content-Disposition'] = cd 
        response.mimetype='text/csv'
        return response
    except Exception as e:
        return errorresponse("get_csv_data", e)
# ------------------------------------------



# ------------------------------------------
# URL Building
# ------------------------------------------
from flask import url_for

# @app.route('/')
# def index():
#     return 'index'

# @app.route('/login')
# def login():
#     return 'login'

# @app.route('/user/<username>')
# def profile(username):
#     return f'{username}\'s profile'

with app.test_request_context():
    print(url_for('uploadFile'))             # /
    # print(url_for('index'))             # /
    # print(url_for('login'))             # /login
    # print(url_for('login', next='/'))   # /login?next=/
    # print(url_for('profile', username='John Doe'))   # /user/John%20Doe
# ------------------------------------------

