const url = 'https://pokeapi.co/api/v2/pokemon/1/';

fetch(url)

.then(response => response.json()) // Converte a resposta em JSON

 .then(data => {

  // Agora 'data' contém as informações do Pokémon

  console.log('Nome do Pokémon:', data.name);

  console.log('Altura do Pokémon:', data.height);

 })

 .catch(error => {

  console.error('Ocorreu um erro:', error);

 });


function mostrarCadastro() {
    document.getElementById("cadastro").style.display = "block";
    document.getElementById("login").style.display = "none";
}

function mostrarLogin() {
    document.getElementById("cadastro").style.display = "none";
    document.getElementById("login").style.display = "block";
}



class Pokemon {
    constructor(nome, level=50) {
        this.nome = nome;
        this.level = level;
        this.hpMax = 0;
        this.hp = 0;
        this.attack = 0;
        this.defense = 0;
        this.moves = [];     // {name, power, type}
        this.types = [];     // ["electric", "flying"]
    }

    async loadData() {
        const url = `https://pokeapi.co/api/v2/pokemon/${this.nome.toLowerCase()}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Pokémon não encontrado");
        const data = await res.json();

        const baseStats = {};
        data.stats.forEach(stat => baseStats[stat.stat.name] = stat.base_stat);

        this.hpMax = Math.floor((baseStats.hp * 2 * this.level) / 100 + this.level + 10);
        this.hp = this.hpMax;
        this.attack = Math.floor((baseStats.attack * 2 * this.level) / 100 + 5);
        this.defense = Math.floor((baseStats.defense * 2 * this.level) / 100 + 5);

        // Tipos do Pokémon
        this.types = data.types.map(t => t.type.name);

        // Pega 4 primeiros ataques e adiciona power e type
        this.moves = await Promise.all(
            data.moves.slice(0,4).map(async m => {
                const moveRes = await fetch(m.move.url);
                const moveData = await moveRes.json();
                return {
                    name: moveData.name,
                    power: moveData.power || 40, // moves sem power = 40
                    type: moveData.type.name
                };
            })
        );
    }

    // Calcula dano usando a fórmula clássica
    calcularDano(target, moveIndex=0, crit=false) {
        const move = this.moves[moveIndex];
        if (!move.power) move.power = 40;

        // STAB: 1.5 se o tipo do movimento estiver entre os tipos do Pokémon
        const STAB = this.types.includes(move.type) ? 1.5 : 1;

        // Tipo do alvo (simplificação: considerar apenas 1º tipo)
        const effectiveness = getEffectiveness(move.type, target.types[0]);

        // Crítico
        const critical = crit ? 1.5 : 1;

        // random 0.85 a 1
        const random = 0.85 + Math.random() * 0.15;

        const dano = Math.floor(
            ((2 * this.level * critical + 2) * move.power * (this.attack/target.defense)/50 + 2)
            * STAB * effectiveness * random
        );

        target.receberDano(dano);
        return dano;
    }

    receberDano(dano) {
        this.hp -= dano;
        if (this.hp < 0) this.hp = 0;
        this.atualizarBarraHP();
    }

    atualizarBarraHP() {
        const barra = document.getElementById(`${this.nome}-hp`);
        if (barra) barra.style.width = `${(this.hp/this.hpMax)*100}%`;
    }
}

function getEffectiveness(moveType, targetType) {
    const chart = {
        normal:    {rock:0.5, ghost:0, steel:0.5},
        fire:      {fire:0.5, water:0.5, grass:2, ice:2, bug:2, rock:0.5, dragon:0.5, steel:2},
        water:     {fire:2, water:0.5, grass:0.5, ground:2, rock:2, dragon:0.5},
        electric:  {water:2, electric:0.5, grass:0.5, ground:0, flying:2, dragon:0.5},
        grass:     {fire:0.5, water:2, grass:0.5, poison:0.5, ground:2, flying:0.5, bug:0.5, rock:2, dragon:0.5, steel:0.5},
        ice:       {fire:0.5, water:0.5, grass:2, ice:0.5, ground:2, flying:2, dragon:2, steel:0.5},
        fighting:  {normal:2, ice:2, rock:2, dark:2, steel:2, poison:0.5, flying:0.5, psychic:0.5, bug:0.5, ghost:0},
        poison:    {grass:2, poison:0.5, ground:0.5, rock:0.5, ghost:0.5, steel:0},
        ground:    {fire:2, electric:2, grass:0.5, poison:2, flying:0, bug:0.5, rock:2, steel:2},
        flying:    {electric:0.5, grass:2, fighting:2, bug:2, rock:0.5, steel:0.5},
        psychic:   {fighting:2, poison:2, psychic:0.5, dark:0, steel:0.5},
        bug:       {fire:0.5, grass:2, fighting:0.5, poison:0.5, flying:0.5, psychic:2, ghost:0.5, dark:2, steel:0.5, fairy:0.5},
        rock:      {fire:2, ice:2, fighting:0.5, ground:0.5, flying:2, bug:2, steel:0.5},
        ghost:     {normal:0, psychic:2, ghost:2, dark:0.5},
        dragon:    {dragon:2, steel:0.5, fairy:0},
        dark:      {fighting:0.5, psychic:2, ghost:2, dark:0.5, fairy:0.5},
        steel:     {fire:0.5, water:0.5, electric:0.5, ice:2, rock:2, steel:0.5, fairy:2},
        fairy:     {fire:0.5, fighting:2, poison:0.5, dragon:2, dark:2, steel:0.5},
    };

    if (!chart[moveType]) return 1;
    return chart[moveType][targetType] || 1;
}

// Seleção de Pokémon na tela de escolha (PBS.html)
document.querySelectorAll(".pokemon_selection").forEach(img => {
    img.addEventListener("click", () => {
        const nome = img.dataset.name;
        // Salva no localStorage para pegar depois na fight.html
        localStorage.setItem("selectedPokemon", nome);
        // Vai pra tela de batalha
        window.location.href = "fight.html";
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const formLogin = document.getElementById("form-login");

    formLogin.addEventListener("submit", async (e) => {
        e.preventDefault(); // previne o envio normal do formulário

        const username = document.getElementById("login-username").value;
        const password = document.getElementById("login-password").value;

        try {
            const res = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    hashed_password: password // ou password se você ainda não estiver hashando
                })
            });

            if (!res.ok) {
                const data = await res.json();
                alert("Erro: " + data.detail);
                return;
            }

            // Login OK, redireciona para seleção de Pokémon
            window.location.href = "/selecao-pokemon";

        } catch (err) {
            console.error(err);
            alert("Erro de conexão com o servidor");
        }
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const formCadastro = document.getElementById("form-cadastro");

    formCadastro.addEventListener("submit", async (e) => {
        e.preventDefault(); // evita o envio normal do form

        const username = document.getElementById("cad-username").value;
        const password = document.getElementById("cad-password").value;

        try {
            const response = await fetch("/user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    hashed_password: password
                })
            });

            if (response.ok) {
                alert("Usuário criado com sucesso!");
                // opcional: redirecionar para seleção de Pokémon
                window.location.href = "/selecao-pokemon";
            } else {
                const data = await response.json();
                alert("Erro: " + (data.detail || "Não foi possível criar o usuário"));
            }
        } catch (err) {
            console.error(err);
            alert("Erro de conexão com a API");
        }
    });
});

// scripts.js

// só executa se estivermos na fight.html

if (window.location.pathname.includes("fight.html")) {
    const playerNome = localStorage.getItem("selectedPokemon") || "pikachu";

    // escolhe inimigo aleatório diferente do player usando a lista global já existente
    let enemyNome;
    do {
        enemyNome = pokemons[Math.floor(Math.random() * pokemons.length)];
    } while (enemyNome === playerNome);

    // Atualiza HTML
    document.getElementById("player-name").innerText = playerNome;
    document.getElementById("player-pokemon").src = 
        `https://img.pokemondb.net/sprites/black-white/anim/back-normal/${playerNome}.gif`;

    document.getElementById("enemy-name").innerText = enemyNome;
    document.getElementById("enemy-pokemon").src = 
        `https://img.pokemondb.net/sprites/black-white/anim/normal/${enemyNome}.gif`;
}