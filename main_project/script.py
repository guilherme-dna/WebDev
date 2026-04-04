import requests

input_file = "static/last_evos.txt"
output_file = "static/last_evos_gen1_5.txt"

filtered_pokemons = []

with open(input_file, "r", encoding="utf-8") as f:
    names = [line.strip().lower() for line in f if line.strip()]

for name in names:
    url = f"https://pokeapi.co/api/v2/pokemon-species/{name}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        # número da Pokédex
        dex_number = data["id"]
        if dex_number <= 649:  # até a 5ª geração
            filtered_pokemons.append(name)
    except requests.HTTPError:
        print(f"Pokémon não encontrado na API: {name}")

with open(output_file, "w", encoding="utf-8") as f:
    for name in filtered_pokemons:
        f.write(name + "\n")

print("Arquivo filtrado com sucesso! Só geração 1-5.")