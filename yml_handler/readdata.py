# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import re

def yml_to_df(app, data=None):
    data_array = []
    index = 0

    if data == None:
        with open(app.root_path + '/yml_handler/openapi_modified.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)

    route = None
    httpVar = None
    resp_code = None
    paramName = None
    routs = data['paths']
    
    groped_route = {}
    grouped_cat = {}
    
    df = pd.DataFrame()
    for route_path, route_data in routs.items():
        splitted_path = route_path.split('/')
        # print(splitted_path[3])
        route       =   route_path
        for item, item_data in route_data.items():
            if item in ['get', 'post', 'put', 'patch', 'update', 'delete']:
                httpVar = item.upper()

                for resp_code in item_data.get("responses"):
                    resp_code = resp_code if isinstance(resp_code, (int)) else None
                
                if item_data.get("parameters"):     # if parameter value is not none
                    paramName = item_data.get("parameters")[0].get('name')

        data = {
            "Route"     :   route,
            "HTTP Verbs"   :   httpVar, 
            "Response Code" :   resp_code, 
            "Parameter Name" :   paramName
        }

        group_cat_name  = splitted_path[2]
        group_cat_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', group_cat_name).title()

        group_name  = splitted_path[3]
        group_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', group_name).title()

        if group_name in groped_route:
            groped_route.get(group_name).append(
                {
                    "data":data,
                    "group_cat_name" : group_cat_name
                }
            )
        else:
            groped_route[group_name] = [{
                    "data":data,
                    "group_cat_name" : group_cat_name
                }]

    written = []

    for group, item_array in groped_route.items():
        # df = df.append({"Group Name" : group}, ignore_index=True)
        group_name = group

        for item in item_array:
            group_cat_name = item.get("group_cat_name")

            if group_cat_name not in written:
                written.append(group_cat_name)
                df = df.append({"Group Name" : "Service: "+group_cat_name}, ignore_index=True)

            path_name = group_cat_name+group_name
            if path_name not in written:
                written.append(path_name)
                df = df.append({"Group Name" : group_name}, ignore_index=True)
            
            index +=1
            item.get("data").update({"Serial Number" : index})
            item.get("data").update({"API Type" : "Internal"})
            df = df.append(item.get("data"), ignore_index=True)


    col = df.pop("Serial Number")
    df.insert(0, col.name, col)
    
    apitype = df.pop("API Type")
    df.insert(2, apitype.name, apitype)

    # print(df)

    return df
