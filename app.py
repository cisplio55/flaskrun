from json import dumps
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import io
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import bcrypt
from util import *
from yml_handler.readdata import *
from flask import Response
from flask import url_for
from urllib.parse import urlparse, parse_qs
from yml_handler.FlaskRouteToSwagger import swagger_yaml_generator

app = Flask(
    __name__,
    template_folder='frontend',
    static_url_path='',
    static_folder='frontend',
)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"


@app.route('/register', methods=['POST'])
def register():
    enteredInfo = getenteredInfo(request)
    username = enteredInfo.get("username")
    password = enteredInfo.get("password")
    dbname = get_database()
    collection_name = dbname["userCredential"]
    user = collection_name.find_one({"username": username})
    if user == None:
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        collection_name.insert_one(
            {"username": username, "password": hashed_password})
        return {"message": "Thanks for register."}
    else:
        return {"message": "User already exists. Please login or try with another user name."}

@app.route('/login', methods=['POST'])
def login():
    try:
        enteredInfo = getenteredInfo(request)
        username = enteredInfo.get("username")
        password = enteredInfo.get("password")
        dbname = get_database()
        collection_name = dbname["userCredential"]
        user_found = collection_name.find_one({"username": username})

        if bcrypt.checkpw(password.encode('utf-8'), user_found.get("password")):
            # request.seassion({"username":username})
            access_token = create_access_token(identity=username)
            return dataresponse("login", {"message": "Login Successful", "access_token": access_token})
        return dataresponse("login", {"message": "Invalid credential"})
    except Exception as e:
        return errorresponse("login", e)

@app.route('/getUsers', methods=['GET'])
# @jwt_required
def getUsers():
    try:
        users = get_database()['userCredential'].find(
            {}, {'password': 0, '_id': 0})
        return dataresponse("getUsers", list(users))
    except Exception as e:
        return errorresponse("getUsers", e)

@app.route('/get_csv_data', methods=['POST'])
def get_csv_data():
    try:
        # In form data, I used "myfile" as key.
        raw_data = request.files['file'].read()
        data = yaml.load(raw_data, Loader=SafeLoader)

        df = yml_to_df(app, data)
        fileName = "OutputTable"
        """This block Returns CSV file"""
        # s   = io.StringIO()
        # df.to_csv(s, index=False)
        # csv = s.getvalue()
        # response = make_response(csv)
        # cd = 'attachment; filename={}.csv'.format(fileName)
        # response.headers['Content-Disposition'] = cd
        # response.mimetype='text/csv'
        # return response

        """This block returns Excel file"""
        buffer = io.BytesIO()
        total_style = pd.Series("font-weight: bold;", index=["Response Code"])
        df.style.apply(lambda s: total_style)
        df.to_excel("./yml_handler/output.xlsx", index=False)
        df.to_excel(buffer, index=False)
        headers = {
            'Content-Disposition': 'attachment; filename={}.xlsx'.format(fileName),
            'Content-type': 'application/vnd.ms-excel'
        }
        return Response(buffer.getvalue(), mimetype='application/vnd.ms-excel', headers=headers)

    except Exception as e:
        return errorresponse("get_csv_data", e)


@app.route('/multi/level/url/test/<user_id>/<org_id>', defaults={'username': "Subhankar"}, methods=["GET", "POST"])
def test(user_id, org_id, username):
    try:
        return dataresponse("TestCAll", {"message": user_id, "org_id" : org_id, "username": username})
    except Exception as e:
        return errorresponse("login", e)


# ------------------------------------------
# URL Building
# ------------------------------------------
# with app.test_request_context():
#     print(url_for('register'))             # /
#     print(url_for('login'))             # /
#     print(url_for('getUsers'))             # /login
#     print(url_for('get_csv_data', next='/'))   # /login?next=/
# ------------------------------------------



@app.route("/generate_yaml")
def generate_yaml():
    try:
        swagger_yaml_generator(app)
        return dataresponse("generate_yaml", {"mesage" : "Swagger YAML file generated successfully"})
    except Exception as e:
        errorresponse("generate_yaml", e)