


register_schema = {
    "type" : "object",
    "properties" : {
        "username" : {"type" : "string", "minLength": 5, "maxLength": 10},
        "password" : {"type" : "string", "minLength": 5, "maxLength": 10},
    },
    "required": ["username", "password"]
}

login_schema = {
    "type" : "object",
    "properties" : {
        "username" : {"type" : "string", "minLength": 5, "maxLength": 10},
        "password" : {"type" : "string", "minLength": 5, "maxLength": 10},
    },
    "required": ["username", "password"]
}



test_api_schema = {
    "type" : "object",
    "properties" : {
        "pin_code" : {"type" : "number", "minLength": 5, "maxLength": 10},
        "phone" : {"type" : "number", "minLength": 5, "maxLength": 10},
    },
    "required": ["user_id", "org_id"]
}