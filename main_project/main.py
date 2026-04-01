from typing import Optional
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from tables import User
from database import create_db_and_tables, engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

templates = Jinja2Templates(directory="templates")  # sua pasta de HTML

app = FastAPI()


# Monta a pasta static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # garante que as tabelas existam

@app.get("/login.html")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/PBS.html")
def PBS_page(request: Request):
    return templates.TemplateResponse("PBS.html", {"request": request})


@app.get("/fight.html")
def fight_page(request: Request):
    return templates.TemplateResponse("fight.html", {"request": request})

@app.post("/user")
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@app.get("/user")
def get_user_by_name(user: Optional[str] = None):
    with Session(engine) as session:
        if user:
            query = select(User).where(User.username.contains(user))
            return session.exec(query).all()
        query = select(User)
        return session.exec(query).all()
    

@app.post("/login")
def login(user: User):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user.username)).first()
        if not db_user or db_user.hashed_password != user.hashed_password:
            raise HTTPException(status_code=400, detail="Usuário ou senha inválidos")
        return {"message": "Login OK"}
    

@app.get("/selecao-pokemon")
def selecao_pokemon(request: Request):
    # você pode passar variáveis pro template se quiser
    return templates.TemplateResponse("PBS.html", {"request": request})