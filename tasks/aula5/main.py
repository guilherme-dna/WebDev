from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI()

# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")


class User(BaseModel):
    name: str
    senha: str
    bio: str   

users_db=[]

@app.post("users")
async def cria_user(user:User):
    users_db.append(user.dict())
    return {"nome:" , user.nome}

@app.get("/")
async def ver_forms(request: Request):
    return templates.TemplateResponse(
        request=request, name="form.html", context={"users": users_db}
    )
    


@app.get("login")
async def get_login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"users": users_db}
    )

@app.get("/fds")
async def lista():
    return users_db


