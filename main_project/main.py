from typing import Optional
from fastapi import FastAPI, HTTPException, Form, Request, Response
from sqlmodel import Session, select
from tables import User
from database import create_db_and_tables, engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import random

templates = Jinja2Templates(directory="templates")  # sua pasta de HTML

app = FastAPI()

# Monta a pasta static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # garante que as tabelas existam


# ----------------- Páginas -----------------
@app.get("/login.html")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/PBS.html")
def PBS_page(request: Request):
    return templates.TemplateResponse("PBS.html", {"request": request})


@app.get("/build", response_class=HTMLResponse)
def build(request: Request):
    return templates.TemplateResponse("build.html", {"request": request})

@app.get("/fight", response_class=HTMLResponse)
def fight(request: Request):
    return templates.TemplateResponse("fight.html", {"request": request})

@app.get("/selecao-pokemon")
def selecao_pokemon(request: Request, user: str = "Player"):
    pokemon_list = []
    try:
        with open("static/last_evos_gen1_5.txt") as f:
            # Remove espaços e linhas vazias
            pokemon_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        pokemon_list = ["pikachu"]  # fallback

    return templates.TemplateResponse(
        "PBS.html",
        {
            "request": request,
            "username": user,
            "pokemons": pokemon_list
        }
    )



# ----------------- CRUD via HTMX -----------------
@app.post("/user", response_class=HTMLResponse)
def create_user_htmx(
    username: str = Form(...),
    password: str = Form(...)
):
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == username)).first()
        if existing_user:
            return '<span style="color:red">Usuário já existe!</span>'
        new_user = User(username=username, hashed_password=password)  # se for usar hash, substitua aqui
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return '<span style="color:lime">Conta criada com sucesso!</span>'

@app.post("/login", response_class=HTMLResponse)
def login_htmx(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == username)).first()
        if not db_user:
            # Retorna mensagem de erro dentro do HTMX target
            return '<span style="color:red">Usuário não encontrado!</span>'
        if db_user.hashed_password != password:
            return '<span style="color:red">Senha incorreta!</span>'
        
        # Login OK → envia header HX-Redirect
        response.headers["HX-Redirect"] = f"/selecao-pokemon?user={username}"
        return ""  # corpo vazio, HTMX só lê o header
    

# ----------------- Consulta de usuários (opcional) -----------------
@app.get("/user")
def get_user_by_name(user: Optional[str] = None):
    with Session(engine) as session:
        if user:
            query = select(User).where(User.username.contains(user))
            return session.exec(query).all()
        query = select(User)
        return session.exec(query).all()
    





#PARTE DA LUTA
