"""
Draft import service - parses draft URLs from various sources
Supported sources:
- draftlol.dawe.gg
- Manual entry
- (Future) Image OCR
"""

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

import httpx


# Champion name to ID mapping (partial, will be expanded)
# This is a subset - full mapping should be loaded from DataDragon
CHAMPION_NAME_TO_ID = {
    "aatrox": 266, "ahri": 103, "akali": 84, "akshan": 166, "alistar": 12,
    "amumu": 32, "anivia": 34, "annie": 1, "aphelios": 523, "ashe": 22,
    "aurelion sol": 136, "aurora": 893, "azir": 268, "bard": 432, "belveth": 200,
    "blitzcrank": 53, "brand": 63, "braum": 201, "briar": 233, "caitlyn": 51,
    "camille": 164, "cassiopeia": 69, "chogath": 31, "corki": 42, "darius": 122,
    "diana": 131, "draven": 119, "drmundo": 36, "ekko": 245, "elise": 60,
    "evelynn": 28, "ezreal": 81, "fiddlesticks": 9, "fiora": 114, "fizz": 105,
    "galio": 3, "gangplank": 41, "garen": 86, "gnar": 150, "gragas": 79,
    "graves": 104, "gwen": 887, "hecarim": 120, "heimerdinger": 74, "hwei": 910,
    "illaoi": 420, "irelia": 39, "ivern": 427, "janna": 40, "jarvaniv": 59,
    "jax": 24, "jayce": 126, "jhin": 202, "jinx": 222, "kaisa": 145,
    "kalista": 429, "karma": 43, "karthus": 30, "kassadin": 38, "katarina": 55,
    "kayle": 10, "kayn": 141, "kennen": 85, "khazix": 121, "kindred": 203,
    "kled": 240, "kogmaw": 96, "ksante": 897, "leblanc": 7, "leesin": 64,
    "leona": 89, "lillia": 876, "lissandra": 127, "lucian": 236, "lulu": 117,
    "lux": 99, "malphite": 54, "malzahar": 90, "maokai": 57, "masteryi": 11,
    "milio": 902, "missfortune": 21, "wukong": 62, "mordekaiser": 82, "morgana": 25,
    "naafiri": 950, "nami": 267, "nasus": 75, "nautilus": 111, "neeko": 518,
    "nidalee": 76, "nilah": 895, "nocturne": 56, "nunu": 20, "olaf": 2,
    "orianna": 61, "ornn": 516, "pantheon": 80, "poppy": 78, "pyke": 555,
    "qiyana": 246, "quinn": 133, "rakan": 497, "rammus": 33, "reksai": 421,
    "rell": 526, "renata": 888, "renekton": 58, "rengar": 107, "riven": 92,
    "rumble": 68, "ryze": 13, "samira": 360, "sejuani": 113, "senna": 235,
    "seraphine": 147, "sett": 875, "shaco": 35, "shen": 98, "shyvana": 102,
    "singed": 27, "sion": 14, "sivir": 15, "skarner": 72, "smolder": 901,
    "sona": 37, "soraka": 16, "swain": 50, "sylas": 517, "syndra": 134,
    "tahmkench": 223, "taliyah": 163, "talon": 91, "taric": 44, "teemo": 17,
    "thresh": 412, "tristana": 18, "trundle": 48, "tryndamere": 23, "twistedfate": 4,
    "twitch": 29, "udyr": 77, "urgot": 6, "varus": 110, "vayne": 67,
    "veigar": 45, "velkoz": 161, "vex": 711, "vi": 254, "viego": 234,
    "viktor": 112, "vladimir": 8, "volibear": 106, "warwick": 19, "xayah": 498,
    "xerath": 101, "xinzhao": 5, "yasuo": 157, "yone": 777, "yorick": 83,
    "yuumi": 350, "zac": 154, "zed": 238, "zeri": 221, "ziggs": 115,
    "zilean": 26, "zoe": 142, "zyra": 143, "ambessa": 799,
}


def normalize_champion_name(name: str) -> str:
    """Normalize champion name for lookup"""
    return re.sub(r"[^a-z]", "", name.lower())


def get_champion_id(name: str) -> Optional[int]:
    """Get champion ID from name"""
    normalized = normalize_champion_name(name)
    return CHAMPION_NAME_TO_ID.get(normalized)


async def parse_draftlol_url(url: str) -> Optional[dict]:
    """
    Parse a draftlol.dawe.gg URL to extract draft data.

    The URL format is typically:
    https://draftlol.dawe.gg/draft/ENCODED_DATA

    Where ENCODED_DATA contains the draft information.
    """
    try:
        parsed = urlparse(url)

        # Check if it's a draftlol URL
        if "draftlol" not in parsed.netloc and "dawe.gg" not in parsed.netloc:
            return None

        # The draft data is usually in the path or query params
        # Try to extract from the URL path
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) >= 2 and path_parts[0] == "draft":
            draft_id = path_parts[1]

            # Try to fetch the draft data from the API
            # draftlol might have an API endpoint
            async with httpx.AsyncClient() as client:
                # Try different API endpoints
                api_urls = [
                    f"https://draftlol.dawe.gg/api/draft/{draft_id}",
                    f"https://draftlol.dawe.gg/api/drafts/{draft_id}",
                ]

                for api_url in api_urls:
                    try:
                        response = await client.get(api_url, timeout=10.0)
                        if response.status_code == 200:
                            data = response.json()
                            return parse_draftlol_response(data)
                    except Exception:
                        continue

        return None

    except Exception as e:
        print(f"Error parsing draftlol URL: {e}")
        return None


def parse_draftlol_response(data: dict) -> Optional[dict]:
    """Parse the response from draftlol API"""
    try:
        # The structure depends on the actual API response
        # This is a best guess based on common patterns
        result = {
            "blue_bans": [],
            "red_bans": [],
            "blue_picks": [],
            "red_picks": [],
        }

        # Try to extract bans
        if "bans" in data:
            bans = data["bans"]
            if isinstance(bans, dict):
                result["blue_bans"] = [get_champion_id(c) for c in bans.get("blue", [])]
                result["red_bans"] = [get_champion_id(c) for c in bans.get("red", [])]

        # Try to extract picks
        if "picks" in data:
            picks = data["picks"]
            if isinstance(picks, dict):
                result["blue_picks"] = [get_champion_id(c) for c in picks.get("blue", [])]
                result["red_picks"] = [get_champion_id(c) for c in picks.get("red", [])]

        # Filter out None values
        result["blue_bans"] = [b for b in result["blue_bans"] if b is not None]
        result["red_bans"] = [b for b in result["red_bans"] if b is not None]
        result["blue_picks"] = [p for p in result["blue_picks"] if p is not None]
        result["red_picks"] = [p for p in result["red_picks"] if p is not None]

        return result

    except Exception as e:
        print(f"Error parsing draftlol response: {e}")
        return None


def parse_draft_string(draft_string: str) -> Optional[list]:
    """
    Parse a draft string that might be in various formats:
    - Comma-separated champion names
    - Champion IDs
    - Pipe-separated format like "ban1|ban2|...|pick1|pick2|..."
    """
    try:
        # Check if it's already numeric IDs
        parts = re.split(r"[,|;\s]+", draft_string.strip())

        result = []
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Try as numeric ID first
            if part.isdigit():
                result.append(int(part))
            else:
                # Try as champion name
                champ_id = get_champion_id(part)
                if champ_id:
                    result.append(champ_id)

        return result if result else None

    except Exception as e:
        print(f"Error parsing draft string: {e}")
        return None


async def import_draft_from_url(url: str, is_blue_side: bool = True) -> dict:
    """
    Main function to import a draft from a URL.

    Returns a dict with:
    - success: bool
    - message: str
    - data: dict with our_bans, opponent_bans, our_picks, opponent_picks
    """
    if not url:
        return {
            "success": False,
            "message": "No URL provided",
            "data": None,
        }

    # Try to parse draftlol URL
    draft_data = await parse_draftlol_url(url)

    if draft_data:
        # Convert based on which side we are
        if is_blue_side:
            return {
                "success": True,
                "message": "Draft imported successfully from draftlol",
                "data": {
                    "our_bans": draft_data["blue_bans"],
                    "opponent_bans": draft_data["red_bans"],
                    "our_picks": draft_data["blue_picks"],
                    "opponent_picks": draft_data["red_picks"],
                },
            }
        else:
            return {
                "success": True,
                "message": "Draft imported successfully from draftlol",
                "data": {
                    "our_bans": draft_data["red_bans"],
                    "opponent_bans": draft_data["blue_bans"],
                    "our_picks": draft_data["red_picks"],
                    "opponent_picks": draft_data["blue_picks"],
                },
            }

    return {
        "success": False,
        "message": "Could not parse draft from URL. The URL format may not be supported or the draft data is not accessible.",
        "data": None,
    }
