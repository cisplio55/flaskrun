# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import re
import traceback

def yml_to_df(app, data=None):
    try:
        sl_no = 0
        if data == None:
            with open(app.root_path + '/yml_handler/openapi_modified.yml') as f:
                data = yaml.load(f, Loader=SafeLoader)
        route = None
        httpVar = None
        resp_code = None
        routs = data['paths']
        groped_route = {}
        df = pd.DataFrame()
        for route_path, route_data in routs.items():
            splitted_path = route_path.split('/')
            if len(splitted_path) < 5: # If length of the URL level less then 5, maintain atlist 5 levels.
                for i in range(5-len(splitted_path)): # Azuming URL mength is 4 alyays the format is > /accounts/Group_category/Groupname/generate_yaml
                    splitted_path.insert(0, '')
            route = route_path
            for item, item_data in route_data.items():
                if item in ['get', 'post', 'put', 'patch', 'update', 'delete']:
                    httpVar = item.upper()
                    
                    path_params = ""
                    body_params = ""

                    for resp_code in item_data.get("responses"):
                        resp_code = resp_code if isinstance(resp_code, (int)) else None
                    if item_data.get("parameters"):     # if parameter value is not none
                        for param_array in item_data.get("parameters"):
                            if str(param_array.get('in')).lower() == "path": # Process the URL parameters.
                                path_params += param_array.get("name")+", " if param_array.get("name") not in path_params else ""
                            
                            if str(param_array.get('in')).lower() == "body": # Process the body parameters.
                                try:
                                    for param in param_array["schema"]["properties"].keys():
                                        body_params += param+", "
                                except:
                                    """
                                    If param_array["schema"]["properties"] is not available
                                    then the excepton block will execute. And there is nothing to do
                                    if schema is not available so simply pass from.
                                    """
                                    pass
                    data = {
                        "Route"     :   route,
                        "HTTP Verbs"   :   httpVar, 
                        "Response Code" :   resp_code, 
                        "Parameter Name" :   "Path Parameters : {}\nBody Parameters : {}".format(path_params, body_params),
                    }
                    group_cat_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ',  splitted_path[2]).title()
                    group_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', splitted_path[3]).title()#+"("+httpVar+")"
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
        df = pd.concat([df, pd.DataFrame.from_records([{"Group Name" : ""}])]) # Insert a empty row at the top.
        for group, item_array in groped_route.items():
            group_name = group
            for item in item_array:
                group_cat_name = item.get("group_cat_name")
                if group_cat_name not in written:
                    written.append(group_cat_name)
                    df = pd.concat([df, pd.DataFrame.from_records([{"Group Name" : "Service: "+group_cat_name}])])
                path_name = group_cat_name+group_name
                if path_name not in written:
                    written.append(path_name)
                    df = pd.concat([df, pd.DataFrame.from_records([{"Group Name" : group_name}])])
                sl_no +=1
                item.get("data").update({"Serial Number" : sl_no, "API Type" : "Internal"})
                df = pd.concat([df, pd.DataFrame.from_records([item.get("data")])])
        slno = df.pop("Serial Number")
        df.insert(0, slno.name, slno)
        apitype = df.pop("API Type")
        df.insert(2, apitype.name, apitype)
        # df.to_csv('./yml_handler/output.csv', sl_no=False)     # Prevent to save the data.
        return df
    except Exception as e:
        traceback.print_exc()

