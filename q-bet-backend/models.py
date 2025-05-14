from pydantic import BaseModel, Field

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

class Round(BaseModel): #we can change the fields, i just put down what made sense to me 
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