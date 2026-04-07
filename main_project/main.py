from typing import Optional
from fastapi import FastAPI, HTTPException, Form, Request, Response , Body
from sqlmodel import Session, select
from tables import User ,BattleHistory
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
            pokemon_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        pokemon_list = ["pikachu"]

    # busca usuário no banco
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user)).first()
        if db_user:
            winstreak = db_user.winstreak
            best = db_user.best_streak
        else:
            winstreak = 0
            best = 0

    return templates.TemplateResponse(
        "PBS.html",
        {
            "request": request,
            "username": user,
            "pokemons": pokemon_list,
            "winstreak": winstreak,
            "best": best
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
    

@app.get("/history")
def history(request: Request, user: str):
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user)).first()
        if not db_user:
            return templates.TemplateResponse("history.html", {"request": request, "battles": [], "username": user})

        battles = session.exec(select(BattleHistory).where(BattleHistory.user_id == db_user.id).order_by(BattleHistory.timestamp.desc())).all()
        return templates.TemplateResponse("history.html", {"request": request, "battles": battles, "username": user})




#PARTE DA LUTA
@app.post("/update_winstreak")
def update_winstreak(data: dict = Body(...)):
    username = data.get("username")
    venceu = data.get("venceu", False)
    opponent = data.get("opponent", "Enemy")  # opcional

    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Atualiza winstreak e best_streak
        if venceu:
            user.winstreak += 1
            if user.winstreak > user.best_streak:
                user.best_streak = user.winstreak
            result = "win"
        else:
            user.winstreak = 0
            result = "loss"

        # Cria histórico de batalha
        battle = BattleHistory(user_id=user.id, opponent=opponent, result=result)
        session.add(battle)
        session.add(user)
        session.commit()
        session.refresh(user)

    return {"winstreak": user.winstreak, "best_streak": user.best_streak}