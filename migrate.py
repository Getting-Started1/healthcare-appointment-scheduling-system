from tortoise import Tortoise, run_async
 
 
async def migrate():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",
        modules={"models":["app.models.user"]}
    )
    await Tortoise.generate_schemas()

run_async(migrate())
 