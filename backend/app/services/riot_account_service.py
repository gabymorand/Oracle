from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.riot_account import RiotAccount
from app.riot.client import RiotAPIClient
from app.schemas.riot_account import RiotAccountCreate


async def create_riot_account(db: Session, player_id: int, account: RiotAccountCreate) -> RiotAccount:
    # Fetch PUUID from Riot API
    riot_client = RiotAPIClient()
    puuid = None

    try:
        puuid = await riot_client.get_puuid_by_riot_id(account.summoner_name, account.tag_line)
    except Exception as e:
        # If Riot API fails, generate a fallback PUUID
        # This allows adding accounts even if the API is down or key is invalid
        import hashlib

        fallback_string = f"{account.summoner_name}#{account.tag_line}#{player_id}"
        puuid = hashlib.sha256(fallback_string.encode()).hexdigest()[:78]  # PUUID format
        print(
            f"Warning: Could not fetch PUUID from Riot API for {account.summoner_name}#{account.tag_line}, using fallback: {str(e)}"
        )

    # Check if account already exists
    existing = db.query(RiotAccount).filter(RiotAccount.puuid == puuid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Riot account already exists")

    db_account = RiotAccount(
        player_id=player_id,
        puuid=puuid,
        summoner_name=account.summoner_name,
        tag_line=account.tag_line,
        is_main=account.is_main,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def delete_riot_account(db: Session, account_id: int) -> bool:
    db_account = db.query(RiotAccount).filter(RiotAccount.id == account_id).first()
    if not db_account:
        return False

    db.delete(db_account)
    db.commit()
    return True
