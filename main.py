from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from models import Player, PlayerWithID, Enemy, EnemyWithID
from operations.operations_player import (read_all_players, read_one_player, create_player, update_player, delete_player, read_deleted_players, write_players_to_csv)
from operations.operations_enemy import (read_all_enemies, read_one_enemy, create_enemy, update_enemy, delete_enemy, read_deleted_enemies)

#bases de datos

from sqlalchemy.ext.asyncio import AsyncSession
from utils.conection_db import get_session, Base
from modelos.player_sql import PlayerModel

from utils.conection_db import init_db
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "world hello"}

@app.post("/players_create/", response_model=PlayerWithID)
async def add_player(player: Player, session: AsyncSession = Depends(get_session)):
    return await create_player(player, session)

@app.get("/players_add/", response_model=List[PlayerWithID])
async def get_players(session: AsyncSession = Depends(get_session)):
    return await read_all_players(session)

@app.get("/players/{player_id}", response_model=PlayerWithID)
async def get_player(player_id: int, session: AsyncSession = Depends(get_session)):
    player = await read_one_player(player_id, session)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.put("/players/{player_id}", response_model=PlayerWithID)
async def update_player_endpoint(player_id: int, player_update: Player, session: AsyncSession = Depends(get_session)):
    updated_player = await update_player(player_id, player_update.dict(exclude_unset=True), session)
    if not updated_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated_player

@app.delete("/players/{player_id}", response_model=PlayerWithID)
async def delete_player_endpoint(player_id: int, session: AsyncSession = Depends(get_session)):
    removed_player = await delete_player(player_id, session)
    if not removed_player:
        raise HTTPException(status_code=404, detail="Player not found")
    return removed_player

@app.get("/players/filter/", response_model=List[PlayerWithID])
async def filter_players(is_dead: Optional[bool] = None, session: AsyncSession = Depends(get_session)):
    players = await read_all_players(session)
    if is_dead is not None:
        players = [player for player in players if player.is_dead == is_dead]
    return players

@app.get("/players/search/", response_model=List[PlayerWithID])
async def search_players_by_health(min_health: int = Query(0, alias="minHealth"), session: AsyncSession = Depends(get_session)):
    players = await read_all_players(session)
    return [player for player in players if player.health >= min_health]

@app.get("/players/search_armor/", response_model=Optional[PlayerWithID])
async def search_player_by_armor(min_armor: int, session: AsyncSession = Depends(get_session)):
    players = await read_all_players(session)
    for player in players:
        if player.armor == min_armor:
            return player
    raise HTTPException(status_code=404, detail="No player found with the specified armor")

@app.put("/players/{player_id}/revive", response_model=PlayerWithID)
async def revive_player(player_id: int, session: AsyncSession = Depends(get_session)):
    player = await revive_player_by_id(player_id, session)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

# ---------------------
# Endpoints para Enemies
# ---------------------

@app.post("/enemies/", response_model=EnemyWithID)
async def add_enemy(enemy: Enemy, session: AsyncSession = Depends(get_session)):
    return await create_enemy(enemy, session)

@app.get("/enemies/", response_model=List[EnemyWithID])
async def get_enemies(session: AsyncSession = Depends(get_session)):
    return await read_all_enemies(session)

@app.get("/enemies/{enemy_id}", response_model=EnemyWithID)
async def get_enemy(enemy_id: int, session: AsyncSession = Depends(get_session)):
    enemy = await read_one_enemy(enemy_id, session)
    if not enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return enemy

@app.put("/enemies/{enemy_id}", response_model=EnemyWithID)
async def update_enemy_endpoint(enemy_id: int, enemy_update: Enemy, session: AsyncSession = Depends(get_session)):
    updated_enemy = await update_enemy(enemy_id, enemy_update.dict(exclude_unset=True), session)
    if not updated_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return updated_enemy

@app.delete("/enemies/{enemy_id}", response_model=EnemyWithID)
async def delete_enemy_endpoint(enemy_id: int, session: AsyncSession = Depends(get_session)):
    removed_enemy = await delete_enemy(enemy_id, session)
    if not removed_enemy:
        raise HTTPException(status_code=404, detail="Enemy not found")
    return removed_enemy

@app.get("/players_sql/")
async def get_players_sql(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PlayerModel))
    players = result.scalars().all()
    return players

@app.get("/players/deleted/", response_model=List[PlayerWithID])
async def get_deleted_players(session: AsyncSession = Depends(get_session)):
    return await read_deleted_players(session)

@app.get("/enemies/deleted/", response_model=List[EnemyWithID])
async def get_deleted_enemies(session: AsyncSession = Depends(get_session)):
    return await read_deleted_enemies(session)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)