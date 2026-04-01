
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

contador = 0


templates = Jinja2Templates(directory="Partials")


@app.post("/curtir", response_class=HTMLResponse)
async def curtir():
    global contador
    contador += 1
    return f"<div id='count-curtidas'>{contador}</div>"
    #return templates.TemplateResponse(request, "count.html" , {"contador":contador})


@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request,"index.html")


@app.get("/home/pagina1")
async def pagina1(request: Request):
    return templates.TemplateResponse(request, "pagina1.html")


@app.get("/home/pagina2")
async def pagina2(request: Request):
    return templates.TemplateResponse(request, "pagina2.html")



