from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field


mongodb_uri = "mongodb://localhost:27017"

#connects to mongo on startup and closes on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb = AsyncIOMotorClient(mongodb_uri)["qbet_db"]
    yield
    app.mongodb.client.close()

app = FastAPI(lifespan=lifespan)

"""
Bet Models ----------------------------------------------------------
"""

class Bet(BaseModel):
    team: str = Field(..., description="Team to bet on")
    amount: float = Field(..., gt=0, description="Amount to bet")

class BetOut(Bet):
    id: str = Field(..., description="ID of the bet")

"""
Game Models ----------------------------------------------------------
"""

class Round(BaseModel):
    team_a_econ: float = Field(..., gt=0, description="Team A economy")
    team_b_econ: float = Field(..., gt=0, description="Team B economy")
    team_a_score: int = Field(..., gt=0, description="Team A score") #can combine these two into a single field
    team_b_score: int = Field(..., gt=0, description="Team B score") #
    map_played: str = Field(..., description="Map played")
    current_round: int = Field(..., gt=0, description="Current round")
    team_a_kills_last_round: int = Field(..., gt=0, description="Team A kills last round")
    team_b_kills_last_round: int = Field(..., gt=0, description="Team B kills last round")
    team_a_assists_last_round: int = Field(..., gt=0, description="Team A assists last round")
    team_b_assists_last_round: int = Field(..., gt=0, description="Team B assists last round")
    win_type_last_round: str = Field(..., description="Win type last round")
    last_round_winner: str = Field(..., description="Last round winner")

class RoundOut(Round):
    id: str = Field(..., description="ID of the round")

class GameIn(BaseModel):
    team_a: str = Field(..., description="Team A name")
    team_b: str = Field(..., description="Team B name")
    map_played: str = Field(..., description="Map played")
    rounds: list[Round] = Field(..., description="List of rounds")
    total_rounds: int = Field(..., gt=0, description="Total rounds played")

class GameOut(GameIn):
    id: str = Field(..., description="ID of the game")

"""
Bet Endpoints ---------------------------------------------------------
"""
@app.post("/bet", response_model=BetOut)
async def place_bet(bet: Bet):
    doc = bet.model_dump()
    result = await app.mongodb["bets"].inest_one(doc)
    return BetOut(**doc, id=str(result.inserted_id))

@app.get("/bet/{bet_id}", response_class=BetOut)
async def get_bet(bet_id: str):
    doc = await app.mongodb["bests"].find_one({"_id": ObjectId(bet_id)})
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

@app.get("/game/{game_id}/rounds/{round_number}", response_Model=RoundOut)
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