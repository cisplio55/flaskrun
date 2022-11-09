
import yaml
import re
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

def swagger_yaml_generator(app):
    for rule in app.url_map.iter_rules():
        # -----------------------------------
        # Get the router Path and param name and make the swagger specific formet.
        # -----------------------------------
        route_format = {}
        verb_details = {}

        route_path = str(rule)

        # /multi/level/url/test/{user_id}/{org_id}
        route_path = route_path.replace("<", "{")
        route_path = route_path.replace(">", "}")

        parameter_names = [s.replace(">", "")
                           for s in re.findall(r'[^<]+>', str(rule))]
        # -----------------------------------

        description = re.sub('[^a-zA-Z0-9 \n\.]', ' ', route_path).title()  # Make a description
  
        parameter_details = {  # Do this block when parameter is availabe.
            'description': description,
            # 'operationId': uuid.uuid4().hex,#'authentication-post-permissions-delete',
            'produces': ['application/json'],
            'responses': {
                200: {
                    'description': description
                }
            },
            'security': [
                {
                    'api_key': [],
                    'pypa_auth': []
                }
            ]
        }

        http_verbs = ["get", "post", "patch", "put", "update", "delete"]
        for method in http_verbs:
            if method.upper() in rule.methods:
                # Change the "http verb" dinamically from http verbs.
                verb_details.update({method: parameter_details})

        if parameter_names != []:
            param_array = [{
                'name': param_name,  # Get the first parameter from url
                'in': 'path',
                'description': "Input for " + param_name,
                'required': True,
                'type': 'string'
            } for param_name in parameter_names]
            parameter_details.update({'parameters': param_array})

        route_format.update(verb_details)
        route_format["options"] = parameter_details

        # {"/accounts/.../view/{doc_id}" : {...}}
        base_format["paths"].update({route_path: route_format})

        with open('swagger.yaml', 'w') as f:
            data = yaml.dump(base_format, f)
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
        # print("****************************")
    return True
