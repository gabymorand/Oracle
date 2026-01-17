from sqlalchemy.orm import Session

from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerUpdate


def get_all_players(db: Session) -> list[Player]:
    return db.query(Player).all()


def get_player(db: Session, player_id: int) -> Player | None:
    return db.query(Player).filter(Player.id == player_id).first()


def create_player(db: Session, player: PlayerCreate) -> Player:
    db_player = Player(summoner_name=player.summoner_name, role=player.role)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def update_player(db: Session, player_id: int, player_update: PlayerUpdate) -> Player | None:
    db_player = get_player(db, player_id)
    if not db_player:
        return None

    update_data = player_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_player, field, value)

    db.commit()
    db.refresh(db_player)
    return db_player


def delete_player(db: Session, player_id: int) -> bool:
    db_player = get_player(db, player_id)
    if not db_player:
        return False

    db.delete(db_player)
    db.commit()
    return True
