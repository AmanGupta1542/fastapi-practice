description = """
Its a online shopping store. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users**
* **Read users**
"""

title="Gupta Light House"
description=description
version="1.0.0"
terms_of_service="http://example.com/terms/"
contact={
    "name": "Aman Gupta",
    "url": "http://x-force.example.com/contact/",
    "email": "amangupta1542@gmail.com",
}

license_info={
    "name": "GLH License",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
}

# alias for docs and redocs url

docs_url="/documentation"
redoc_url='/redoc'
openapi_url="/api/v1/openapi.json"

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:4200",
]

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]