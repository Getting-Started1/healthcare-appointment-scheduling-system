from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


app = FastAPI()

@app.get('/')

def index():
    return {"Msg": "Hello World"}

#Tortoise ORM setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,   
)

