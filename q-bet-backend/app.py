from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from models import Bet, BetOut, GameIn, GameOut, Round, RoundOut

mongodb_uri = "mongodb://localhost:27017"

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(mongodb_uri)
    app.state.mongodb = client["qbet_db"]
    yield
    client.close()

app = FastAPI(lifespan=lifespan)

"""
Bet Endpoints ---------------------------------------------------------
"""
@app.post("/bet", response_model=BetOut)
async def place_bet(bet: Bet):
    doc = bet.model_dump()
    result = await app.state.mongodb["bets"].inest_one(doc)
    return BetOut(**doc, id=str(result.inserted_id))

@app.get("/bet/{bet_id}", response_class=BetOut) # type: ignore
async def get_bet(bet_id: str):
    doc = await app.mongodb["bests"].find_one({"_id": ObjectId(bet_id)}) # type: ignore
    return BetOut(**doc, id=bet_id) if doc else None

@app.get("/bets", response_model=list[BetOut])
async def get_bets():
    bets = await app.mongodb["bets"].find().to_list(100)
    return [
        BetOut(**{**bet, "id": str(bet["_id"])})
        for bet in bets
    ]
        
"""
Game Endpoints ---------------------------------------------------------
"""
@app.post("/game", response_model=GameOut)
async def create_game(game: GameIn):
    doc = game.model_dump()
    result = await app.mongodb["games"].insert_one(doc)
    return GameOut(**doc, id=str(result.inserted_id))

@app.get("/game/{game_id}", response_model=GameOut)
async def get_game(game_id: str):
    doc = await app.mongodb["games"].find_one({"_id": ObjectId(game_id)})
    return GameOut(**doc, id=game_id) if doc else None

@app.get("/games", response_model=list[GameOut])
async def get_games():
    games = await app.mongodb["games"].find().to_list(100)
    return [
        GameOut(**{**game, "id": str(game["_id"])})
        for game in games
    ]

@app.post("/game/{game_id}/rounds", response_model=RoundOut)
async def create_game_round(game_id: str, round: Round):
    doc = round.model_dump()
    result = await app.mongodb["games"].update_one(
        {"_id": ObjectId(game_id)},
        {"$push": {"rounds": doc}}
    )
    return RoundOut(**doc, id=str(result.upserted_id))


@app.get("/game/{game_id}/rounds", response_model=list[RoundOut])
async def get_game_rounds(game_id: str):
    doc = await app.mongodb["games"].find_one({"_id": ObjectId(game_id)})
    if not doc:
        return []
    return [
        RoundOut(**{**round, "id": str(round["_id"])})
        for round in doc["rounds"]
    ]

@app.get("/game/{game_id}/rounds/{round_number}", response_model=RoundOut)
async def get_game_round(game_id: str, round_number: int):
    doc = await app.mongodb["games"].find_one({"_id": ObjectId(game_id)})
    if doc and 0 <= round_number <= doc["total_rounds"]:
        round = doc["rounds"][round_number]
        return RoundOut(**{**round, "id": str(round["_id"])})
    return None

@app.get("/game/{game_id}/rounds/{round_id}", response_model=RoundOut)
async def get_game_round_by_id(game_id: str, round_id: str):
    doc = await app.mongodb["games"].find_one(
        {"_id": ObjectId(game_id), "rounds._id": ObjectId(round_id)},
        {"rounds.$": 1}
    )
    if not doc or not doc.get("rounds"):
        raise HTTPException(status_code=404, detail="Round not found")
    
    round = doc["rounds"][0]
    return RoundOut(**{**round, "id": str(round["_id"])})


@app.get("/testing", response_model=str)
async def testing():
    return "Hello, World!"


if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(
                "app:app", 
                host="127.0.0.1",
                port=8000,
                reload=True,
    )