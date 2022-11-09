
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
import re
import yaml

def swagger_yaml_generator(app):
    for rule in app.url_map.iter_rules():
        # -----------------------------------
        # Get the router Path and param name and make the swagger specific formet.
        # -----------------------------------
        route_path = str(rule)

        print(route_path, "################")

        param_name = re.findall(r'<(.+)>', str(rule))
        param_name = param_name[0] if param_name!=[] else ""
        if ":" in param_name:
            param_name = param_name.split(":")[1] # if 'path:filename' then take the param name

        to_replace = re.findall(r'<.+>', str(rule))
        if to_replace != []:
            route_path = route_path.replace(to_replace[0], "{"+param_name+"}")
        # -----------------------------------

        description = re.sub('[^a-zA-Z0-9 \n\.]', ' ',  route_path).title() # Make the description

        route_format = {}
        verb_details = {}

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
                verb_details.update({method: parameter_details})  # Change the "http verb" dinamically from http verbs.
        
        if param_name != "":            
            parameter_details.update({
                'parameters': [
                    {
                        'name': param_name, # Get the first parameter from url
                        'in': 'path',
                        'description': description,
                        'required': True,
                        'type': 'string'
                    }
                ]
            })

        route_format.update(verb_details)
        route_format["options"] = parameter_details
        
        base_format["paths"].update({route_path: route_format}) # {"/accounts/.../view/{doc_id}" : {...}}

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