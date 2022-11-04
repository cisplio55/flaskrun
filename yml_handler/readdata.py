# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import pandas as pd

def yml_to_df(app, data=None):
    data_array = []
    index = 1

    if data == None:
        with open(app.root_path + '/yml_handler/openapi_modified.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        
    route = None
    httpVar = None
    resp_code = None
    paramName = None
    routs = data['paths']

    for route_path, route_data in routs.items():
        index+=1
        route       =   route_path
        for item, item_data in route_data.items():
            if item in ['get', 'post', 'put', 'patch', 'update', 'delete']:
                httpVar = item

                for resp_code in item_data.get("responses"):
                    resp_code = resp_code if isinstance(resp_code, (int)) else None
                    
                if item_data.get("parameters"):     # if parameter value is not none
                    paramName = item_data.get("parameters")[0].get('name')

        data = {
            "route"     :   route, 
            "httpVar"   :   httpVar, 
            "resp_code" :   resp_code, 
            "paramName" :   paramName
        }

        data_array.append(data)

    df = pd.DataFrame(data_array)
    # df.to_csv('./yml_handler/output.csv', index=False)     # Prevent to save the data.
    return df
