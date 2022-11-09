# import pyyaml module
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import re

def yml_to_df(app, data=None):
    index = 0

    if data == None:
        with open(app.root_path + '/yml_handler/openapi_modified.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
    
    print(data)

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

        group_cat_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ',  splitted_path[2]).title()
        group_name = re.sub('[^a-zA-Z0-9 \n\.]', ' ', splitted_path[3]).title()

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

            index +=1
            item.get("data").update({"Serial Number" : index, "API Type" : "Internal"})
            df = pd.concat([df, pd.DataFrame.from_records([item.get("data")])])



    slno = df.pop("Serial Number")
    df.insert(0, slno.name, slno)
    
    apitype = df.pop("API Type")
    df.insert(2, apitype.name, apitype)
    
    # df = df.style.applymap_index(
    #     lambda v: "font-weight: bold;", axis="columns"
    # ).to_latex(convert_css=True)
    


    # def highlight_max(x):
    #     return ['font-weight: bold' if "Service" in v else '' for v in x]

    # # df = pd.DataFrame(np.random.randn(5, 2))
    # df.style.apply(highlight_max)

    # print(df)

    # df.to_csv('./yml_handler/output.csv', index=False)     # Prevent to save the data.
    return df
