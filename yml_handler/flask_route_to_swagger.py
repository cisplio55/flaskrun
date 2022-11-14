import yaml
import re
from util import logger
from functools import wraps
from flask import g, request, redirect, url_for
from flask import abort, make_response, jsonify
from jsonschema import validate, Draft202012Validator

base_format = {
    'swagger': '2.0',
    'info': {
        'description': 'Pypa API specification, across all products.',
        'title': 'Pypa Endpoint for Development',
        'version': '1.0.0'
    },
    'host': 'pypa-api-development.endpoints.huko-312103.cloud.goog',
    'x-google-endpoints': [
        {
            'name': 'pypa-api-development.endpoints.huko-312103.cloud.goog',
            'target': '34.149.86.33'
        }
    ],
    'consumes': [
        'application/json'
    ],
    'produces': [
        'application/json'
    ],
    'schemes': [
        'https',
        'http'
    ],
    'security': [
        {
            'api_key': [],
            'pypa_auth': []
        }
    ],
    'paths': {},
    'securityDefinitions': {
        'api_key': {
            'type': 'apiKey',
            'name': 'x-api-key',
            'in': 'header'
        },
        'pypa_auth': {
            'authorizationUrl': '',
            'flow': 'implicit',
            'type': 'oauth2',
            'x-google-issuer': 'development-endpoint-service@huko-312103.iam.gserviceaccount.com',
            'x-google-jwks_uri': 'https: //www.googleapis.com/service_accounts/v1/metadata/x509/development-endpoint-service@huko-312103.iam.gserviceaccount.com',
            'x-google-audiences': 'pypa-api-development.endpoints.huko-312103.cloud.goog'
        }
    }
}


def rm_sc_make_title(str):
    return re.sub('[^a-zA-Z0-9 \n\.]', ' ', str).title()


def CreateSwaggerSpecificRoute(rule):
    route_path = str(rule)   # /multi/level/url/test/{user_id}/{org_id}
    route_path = route_path.replace("<", "{")
    route_path = route_path.replace(">", "}")
    return route_path


# Decorator function. @validate_input(input_schema)
def validate_input(input_schema=None):
    try:
        """
        # input schema looks like.
        schema = {
            "type" : "object",
            "properties" : {
                "username" : {"type" : "string"},
                "password" : {"type" : "number"},
            },
        }
        """
        def decoratorFunction(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):

                if input_schema == None:    # Simply return without doing anything.
                    return f(*args, **kwargs)

                # GET methd is ignoored because there is no body in get method.
                if request.method != "GET":
                    instance = request.get_json()   # {"get_schema" : true}
                    # If get_schema = True in the request query then return the schema else validate the user input.
                    if instance.get("get_schema"):
                        abort(make_response(jsonify(input_schema), 404))
                    else:
                        try:
                            # Check if chema is valid or not.
                            validate(instance=instance, schema=input_schema)
                        except:
                            validator = Draft202012Validator(input_schema)
                            # sorted(v.iter_errors(instance), key=lambda e: e.path)
                            output_schema = validator.schema
                            abort(make_response(jsonify(output_schema), 404))

                return f(*args, **kwargs)
            return decorated_function
        return decoratorFunction
    except Exception as e:
        print(e)


def generate_swagger_yaml(app):
    try:
        for rule in app.url_map.iter_rules():
            # print("rule : ", rule)
            # print("subdomain : ", rule.subdomain)
            # print("methods : ", rule.methods)
            # print("build_only : ", rule.build_only)
            # print("endpoint : ", rule.endpoint)
            # print("strict_slashes : ", rule.strict_slashes)
            # print("merge_slashes : ", rule.merge_slashes)
            # print("redirect_to : ", rule.redirect_to)
            # print("alias : ", rule.alias)
            # print("host : ", rule.host)
            # print("websocket : ", rule.websocket)
            # print(rule.arguments)
            # print("****************************")

            # -----------------------------------
            # Get the router Path and param name and make the swagger specific formet.
            # -----------------------------------
            route_format = {}
            verb_details = {}
            body_parameters = []
            output_yaml_file = "swagger.yaml"
            endpoint = rule.endpoint
            desc_200 = {"description": "Success"}
            route_path = CreateSwaggerSpecificRoute(rule)
            parameter_names = rule.arguments
            # -----------------------------------

            description = rm_sc_make_title(route_path)  # Make a description
            ep_as_desc = rm_sc_make_title(endpoint)
            option_details = {  # Do this block when parameter is availabe.
                'description': ep_as_desc,
                "summary": ep_as_desc,
                # 'operationId': uuid.uuid4().hex,#'authentication-post-permissions-delete',
                'produces': ['application/json'],
                'responses': {
                    200: desc_200
                },
                'security': [
                    {
                        'api_key': [],
                        'pypa_auth': []
                    }
                ]
            }

            param_array = [{
                'name': param_name,  # Get the first parameter from url
                'in': 'path',
                'description': "Input for " + param_name,
                'required': True,
                'type': 'string'
            } for param_name in parameter_names] if parameter_names != [] else []

            http_verbs = ["get", "post", "patch", "put", "delete"]
            for method in http_verbs:
                if method.upper() in rule.methods:

                    # ----------------------------------------------
                    # Featch schema and prepare the body.
                    # ----------------------------------------------
                    if method != "get":
                        with app.test_client() as c:
                            rv = None
                            fixed_input = {"get_schema": True}
                            if method == "post":
                                rv = c.post(route_path, json=fixed_input)
                            elif method == "put":
                                rv = c.put(route_path, json=fixed_input)
                            elif method == "patch":
                                rv = c.patch(route_path, json=fixed_input)
                            elif method == "delete":
                                rv = c.delete(route_path, json=fixed_input)

                            body_parameters = [
                                {
                                    "in": "body",
                                    "name": ep_as_desc,
                                    "description": description,
                                    "schema": rv.get_json() if "properties" in rv.get_json() else {},
                                }
                            ]
                    # ----------------------------------------------

                    verb_details.update({method: {
                        "summary": ep_as_desc,
                        "consumes": [
                            "application/json"
                        ],
                        # Add URL parameters.
                        "parameters": param_array+body_parameters,
                        "responses": {
                            200: desc_200
                            }
                    }
                    })

                    option_details.update(
                        {"parameters": param_array+body_parameters})

            route_format.update(verb_details)
            route_format["options"] = option_details       # Update parameters

            # {"/accounts/.../view/{doc_id}" : {...}}
            base_format["paths"].update({route_path: route_format})

            with open(output_yaml_file, 'w') as f:
                data = yaml.dump(base_format, f)

        # -------------------------------------------------
        # Modify the router path to keep inside quotation
        # -------------------------------------------------
        data = None
        with open(output_yaml_file, 'r') as file:
            data = file.read()
        for rule in app.url_map.iter_rules():
            route_path = CreateSwaggerSpecificRoute(rule)
            # print(route_path, "@@@@@@@@@@@@@@")
            data = data.replace(route_path+":", '"'+route_path+'":')
        with open(output_yaml_file, 'w') as file:
            file.write(data)
        # -------------------------------------------------

        return True
    except Exception as e:
        # logger("generate_swagger_yaml() : ", e, level="error")
        print(e)
        return None
