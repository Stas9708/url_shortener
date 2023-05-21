import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse


app = FastAPI()

link_dict = {}


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
