#!/bin/env python3
from aperturedb import Utils, Connector


user = "admin"
password = "admin"

con = Connector.Connector(user=user, password=password, port=55557)
query = [{
    "FindImage": {
        "_ref": 1,
        "constraints": {
            "class": ["==", "celeb"]
        }
    }},
#    {
#    "DeleteDescriptor": {
#        "ref": 1,
#    }},
#    {
#    "DeleteBoundingBox": {
#        "ref": 1,
#    }},
#    {
#    "DeleteImage": {
#        "ref": 1,
#    }}
]

(res,blobs) = con.query(query)

query = [{
    "DeleteDescriptorSet" : {
        "constraints": {
            "name" : [ "==" , "celebs" ]
            }
        }
    }]
(res,blobs) = con.query(query)
print("{}".format(res))
