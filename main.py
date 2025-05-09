from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from models import Player, PlayerWithID, Enemy, EnemyWithID
from operations.operations_player import (read_all_players, read_one_player, create_player, update_player, delete_player, read_deleted_players, write_players_to_csv)
from operations.operations_enemy import (read_all_enemies, read_one_enemy, create_enemy, update_enemy, delete_enemy, read_deleted_enemies)
import uvicorn

#bases de datos
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import SessionLocal
from modelos.player_sql import PlayerModel
from sqlalchemy.future import select


app = FastAPI()



@app.post("/players_create/", response_model=PlayerWithID)
async def add_player(player: Player):
    return create_player(player)

@app.get("/players_add/", response_model=List[PlayerWithID])
async def get_players():
    return read_all_players()

@app.get("/players/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int):
    player = read_one_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/players/{player_id}", response_model=PlayerWithID)
async def update_player_endpoint(player_id: int, player_update: Player):
    updated_player = update_player(player_id, player_update.dict(exclude_unset=True))
    if not updated_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated_player

@app.delete("/players/{player_id}", response_model=PlayerWithID)
async def delete_player_endpoint(player_id: int):
    removed_player = delete_player(player_id)
    if not removed_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return removed_player

@app.get("/players/filter/", response_model=List[PlayerWithID])
async def filter_players(is_dead: Optional[bool] = None):
    players = read_all_players()
    if is_dead is not None:
        players = [player for player in players if player.is_dead == is_dead]
    return players

@app.get("/players/search/", response_model=List[PlayerWithID])
async def search_players_by_health(min_health: int = Query(0, alias="minHealth")):
    players = read_all_players()
    return [player for player in players if player.health >= min_health]

# ---------------------
# Endpoints para Enemies
# ---------------------

@app.post("/enemies/", response_model=EnemyWithID)
async def add_enemy(enemy: Enemy):
    return create_enemy(enemy)

@app.get("/enemies/", response_model=List[EnemyWithID])
async def get_enemies():
    return read_all_enemies()

@app.get("/enemies/{enemy_id}", response_model=EnemyWithID)
async def get_enemy(enemy_id: int):
    enemy = read_one_enemy(enemy_id)
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return enemy

@app.put("/enemies/{enemy_id}", response_model=EnemyWithID)
async def update_enemy_endpoint(enemy_id: int, enemy_update: Enemy):
    updated_enemy = update_enemy(enemy_id, enemy_update.dict(exclude_unset=True))
    if not updated_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return updated_enemy

@app.delete("/enemies/{enemy_id}", response_model=EnemyWithID)
async def delete_enemy_endpoint(enemy_id: int):
    removed_enemy = delete_enemy(enemy_id)
    if not removed_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return removed_enemy

@app.get("/players/search_armor/", response_model=Optional[PlayerWithID])
async def search_player_by_armor(min_armor: int):
    players = read_all_players()
    for player in players:
        if player.armor == min_armor:
            return player
    raise HTTPException(status_code=404, detail="No player found with the specified armor")

@app.put("/players/{player_id}/revive", response_model=PlayerWithID)
async def revive_player(player_id: int):
    players = read_all_players()
    for player in players:
        if player.id == player_id:
            player.is_dead = False
            write_players_to_csv(players)  # 🔥 Aquí guardamos el cambio
            return player
    raise HTTPException(status_code=404, detail="Player not found")


#base de datos
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.get("/players_sql/")
async def get_players_sql(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PlayerModel))
    players = result.scalars().all()
    return players


@app.get("/players/deleted/", response_model=List[PlayerWithID])
async def get_deleted_players():
    return read_deleted_players()


@app.get("/enemies/deleted/", response_model=List[EnemyWithID])
async def get_deleted_enemies():
    return read_deleted_enemies()




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)