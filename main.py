"""
- написать страничку регистрации по примеру странички логина (добавить форму)
- написать 2 обработчика (get и post) для регистрации пользователя
    - get просто отображает страничку
    - post принимает данные пользователя из формы (логин и пароль), сохраняет их в словаре
    и делает переадресацию на страничку логина
"""


import uvicorn
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request, Form
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="./static/html")


link_dict = {}
registration_data = {}
count_of_users = 0


@app.get("/registration", response_class=HTMLResponse)
def registration_page(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/registration", response_class=HTMLResponse)
def registration(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    global count_of_users
    count_of_users += 1
    registration_data[count_of_users] = [username, password]
    user_response = RedirectResponse(url="/login")
    return user_response


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
    hash_link = str(hash(long_link))[0:5]
    link_dict[hash_link] = {"long_link": long_link, "counter": 0}
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
