// scripts.js
// Pokémon selection e fight logic

class Pokemon {
    constructor(nome, level=50) {
        this.nome = nome;
        this.level = level;
        this.hpMax = 0;
        this.hp = 0;
        this.attack = 0;
        this.defense = 0;
        this.moves = [];
        this.types = [];
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

        this.types = data.types.map(t => t.type.name);

        this.moves = await Promise.all(
            data.moves.slice(0,4).map(async m => {
                const moveRes = await fetch(m.move.url);
                const moveData = await moveRes.json();
                return {
                    name: moveData.name,
                    power: moveData.power || 40,
                    type: moveData.type.name
                };
            })
        );
    }

    calcularDano(target, moveIndex=0, crit=false) {
        const move = this.moves[moveIndex];
        const STAB = this.types.includes(move.type) ? 1.5 : 1;
        const effectiveness = getEffectiveness(move.type, target.types[0]);
        const critical = crit ? 1.5 : 1;
        const random = 0.85 + Math.random()*0.15;

        const dano = Math.floor(
            ((2*this.level*critical + 2)*move.power*(this.attack/target.defense)/50+2)
            * STAB * effectiveness * random
        );
        // aqui passa o alvo correto para atualizar barra
        target.receberDano(dano, target===player ? 'player' : 'enemy');
        return dano;
    }

    receberDano(dano, targetId='player') {
        this.hp -= dano;
        if(this.hp < 0) this.hp = 0;
        this.atualizarBarraHP(targetId);
    }

    atualizarBarraHP(targetId='player') {
        const barra = document.getElementById(targetId==='player' ? 'player-hp' : 'enemy-hp');
        if(barra) barra.style.width = `${(this.hp/this.hpMax)*100}%`;
    }
}

function getEffectiveness(moveType, targetType){
    const chart = { /* mesma tabela de antes */ };
    if(!chart[moveType]) return 1;
    return chart[moveType][targetType] || 1;
}