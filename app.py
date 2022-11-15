from json import dumps
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import io
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import bcrypt
from util import *
from yml_handler.swagger_yaml_to_excell import *
from flask import Response
from yml_handler.flask_route_to_swagger import generate_swagger_yaml
from schema_definations import *
from flask import g, request, redirect, url_for


app = Flask(
    __name__,
    template_folder='frontend',
    static_url_path='/static',
    static_folder='frontend',
)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "this-is-secret-key"

@app.route('/accounts/authentication/app_registrations/register',  defaults={'schema': register_schema},methods=['POST'])
def register(schema):
    try:
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
            return dataresponse("register", {"message": "Thanks for register."})
        else:
            return dataresponse("register", {"message": "User already exists. Please login or try with another user name."})
    except Exception as e:
        return errorresponse("register", e)



@app.route('/accounts/authentication/app_registrations/login', defaults={'schema': login_schema}, methods=['POST'])
def login(schema):
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


@app.route('/accounts/authentication/app_registrations/getUsers', methods=['GET'])
def getUsers():
    try:
        users = get_database()['userCredential'].find(
            {}, {'password': 0, '_id': 0})
        return dataresponse("getUsers", list(users))
    except Exception as e:
        return errorresponse("getUsers", e)


@app.route('/accounts/test_url/test/<user_id>/<org_id>', defaults={'schema': test_api_schema}, methods=["GET", "POST"])
def test(user_id, org_id, schema):
    try:
        return dataresponse("TestCAll", {"message": user_id, "org_id" : org_id})
    except Exception as e:
        return errorresponse("login", e)


@app.route('/accounts/test_url/test/underTest/<employee_id>', defaults={'schema': test_api_schema}, methods=["GET", "POST", "PATCH"])
# @validate_input(test_api_schema)
def underTest(employee_id, schema):
    try:
        return dataresponse("TestCAll", {
            "message": "Under test message", 
            # "org_id" : org_id, 
            "employee_id" : employee_id
            })
    except Exception as e:
        return errorresponse("login", e)


# ----------------------------------------------------------------------------
# Swagger utility functions
# ----------------------------------------------------------------------------
@app.route('/')
def upload_File_page(name=None):  # To return the file upload UI.
    return render_template('uploadFile.html', name=name)


@app.route('/utility/swagger/UI/generate_csv_data', methods=['POST'])
def generate_csv_data():
    try:
        rettype = request.form.to_dict(flat=False).get("rettype", ["CSV"])[0].upper()
        raw_data = request.files['file'].read()
        data = yaml.load(raw_data, Loader=SafeLoader)
        df = yml_to_df(app, data)
        fileName = "OutputTable"

        if rettype == "CSV":
            """This block Returns CSV file"""
            s   = io.StringIO()
            df.to_csv(s, index=False)
            csv = s.getvalue()
            response = make_response(csv)
            cd = 'attachment; filename={}.csv'.format(fileName)
            response.headers['Content-Disposition'] = cd
            response.mimetype='text/csv'
            return response
        elif rettype == "EXCEL":
            """This block returns Excel file"""
            buffer = io.BytesIO()
            total_style = pd.Series("font-weight: bold;", index=["Response Code"])
            df.style.apply(lambda s: total_style)
            df.to_excel(fileName+".xlsx", index=False)
            df.to_excel(buffer, index=False)
            headers = {
                'Content-Disposition': 'attachment; filename={}.xlsx'.format(fileName),
                'Content-type': 'application/vnd.ms-excel'
            }
            return Response(buffer.getvalue(), mimetype='application/vnd.ms-excel', headers=headers)

    except Exception as e:
        return errorresponse("get_csv_data", e)


@app.route("/utility/swagger/UI/generate_yaml")
def generate_yaml():
    try:
        generate_swagger_yaml(app)
        return dataresponse("generate_yaml", {"mesage" : "Swagger YAML file generated successfully"})
    except Exception as e:
        errorresponse("generate_yaml", e)
# generate_swagger_yaml(app) # Create swagger file automatically on flask run.
# ----------------------------------------------------------------------------


# with app.test_request_context():
#     print(url_for('generate_yaml'))
#     print(url_for('underTest'))
    

# with app.app_context():
    # within this block, current_app points to app.
    
    # print (current_app.name)


# for rule in app.url_map.iter_rules():
#     # for rule in app.url_map.iter_rules():
#     options = {}
#     for arg in rule.arguments:
#         options[arg] = "[{0}]".format(arg)
#         methods = ','.join(rule.methods)
        
#         # if options != {}:
#         print(rule.endpoint, options)
#         print(url_for(rule.endpoint, **options))




    # url = url_for(rule.endpoint)
    # print(url)
    # line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
    # print(line, "@@@@@@@@@@@@@@")
    # output.append(line)
    # for line in sorted(output):
    #     print line




        