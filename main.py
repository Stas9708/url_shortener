
import uvicorn
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pymysql.cursors


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="./static/html")

connection = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="123456",
    db="test_db",
    cursorclass=pymysql.cursors.DictCursor
)
link_dict = {}


@app.get("/registration", response_class=HTMLResponse)
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/registration", response_class=HTMLResponse)
def registration(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    with connection.cursor() as cursor:
        sql = "INSERT INTO `users` (`username`, `password`) VALUES(%s, %s)"
        cursor.execute(sql, (username, password))
    connection.commit()
    return RedirectResponse(url="/login")


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: Annotated[str, Form()]):
    return templates.TemplateResponse("login.html", {"request": request, "username": username})


@app.get("/item/{item_id}", response_class=HTMLResponse)
def item_page(request: Request, item_id: str):
    return templates.TemplateResponse("index.html", {"request": request, "id": item_id})


@app.get("/get_link")
def get_user_link(long_link: str):
    with connection.cursor() as cursor:
        sql = "SELECT long_link, short_link FROM `links` WHERE `long_link` = %s"
        cursor.execute(sql, (long_link,))
        db_long_link = cursor.fetchone()
        if db_long_link:
            return {"url": f"127.0.0.1:8080/{db_long_link['short_link']}"}
        else:
            hash_link = str(hash(long_link))[0:5]
            sql = "INSERT INTO `links` (`long_link`, `short_link`) VALUES(%s, %s)"
            cursor.execute(sql, (long_link, hash_link))
            connection.commit()
            return {"url": f"127.0.0.1:8080/{hash_link}"}


@app.get("/r/{short_link}")
def redirect(short_link: str):
    if short_link in link_dict:
        result = RedirectResponse(url=link_dict[short_link]["long_link"])
        link_dict[short_link]["counter"] += 1
        return result
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )


@app.get("/get_count_of_short_link")
def get_count(short_link: str):
    if short_link in link_dict:
        return {"counter": link_dict[short_link]["counter"]}
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
