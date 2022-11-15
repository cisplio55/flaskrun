import yaml
import re
import traceback

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


def generate_swagger_yaml(app):
    try:
        for rule in app.url_map.iter_rules():
            # print(rule)
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

            # Do not include static urls. So just skip if the there is static rule.
            if rule.endpoint == "static":
                continue
            
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
            parameter_names = list(rule.arguments)
            # Do not want to keep the schema parameter in swagger.
            if "schema" in parameter_names:
                parameter_names.remove("schema")
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
                    # Prepare the body with schema.
                    # ----------------------------------------------
                    if method != "get":
                        default_schema = {}
                        
                        try:
                            default_schema = rule.defaults.get("schema")
                        except:
                            message = "Default schema not available in : " + str(rule)
                            print("***", message)
                            # add_warning(message)

                        body_parameters = [
                            {
                                "in": "body",
                                "name": ep_as_desc,
                                "description": description,
                                # rule.defaults.get("schema") if rule.defaults is not None else {} #rule.defaults#rv.get_json() if "properties" in rv.get_json() else {},
                                "schema": default_schema
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
            data = data.replace(route_path+":", '"'+route_path+'":')
        with open(output_yaml_file, 'w') as file:
            file.write(data)
        # -------------------------------------------------
        return True
    except Exception as e:
        traceback.print_exc()
        return None
