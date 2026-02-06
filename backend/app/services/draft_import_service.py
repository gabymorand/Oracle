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


async def parse_drafter_lol_url(url: str) -> Optional[dict]:
    """
    Parse a drafter.lol URL to extract draft data.

    URL format: https://drafter.lol/draft/CaFDm6yW?game=1
    """
    try:
        parsed = urlparse(url)

        if "drafter.lol" not in parsed.netloc:
            return None

        # Extract draft ID from path: /draft/CaFDm6yW
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]

        if len(path_parts) < 2 or path_parts[0] != "draft":
            return None

        draft_id = path_parts[1]

        # Parse game number from query string
        query_params = parse_qs(parsed.query)
        game_num = query_params.get("game", ["1"])[0]

        async with httpx.AsyncClient() as client:
            # Try different API endpoints for drafter.lol
            api_urls = [
                f"https://drafter.lol/api/draft/{draft_id}",
                f"https://drafter.lol/api/drafts/{draft_id}",
                f"https://drafter.lol/api/v1/draft/{draft_id}",
                f"https://api.drafter.lol/draft/{draft_id}",
                f"https://api.drafter.lol/v1/draft/{draft_id}",
            ]

            for api_url in api_urls:
                try:
                    response = await client.get(api_url, timeout=10.0)
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "")
                        if "json" in content_type:
                            data = response.json()
                            result = parse_drafter_lol_response(data, game_num)
                            if result:
                                return result
                except Exception:
                    continue

            # Try fetching the page and looking for embedded data
            try:
                page_response = await client.get(url, timeout=10.0)
                if page_response.status_code == 200:
                    result = parse_drafter_lol_html(page_response.text, game_num)
                    if result:
                        return result
            except Exception as e:
                print(f"Error fetching drafter.lol page: {e}")

        return None

    except Exception as e:
        print(f"Error parsing drafter.lol URL: {e}")
        return None


def parse_drafter_lol_response(data: dict, game_num: str = "1") -> Optional[dict]:
    """Parse response from drafter.lol API"""
    try:
        result = {
            "blue_bans": [],
            "red_bans": [],
            "blue_picks": [],
            "red_picks": [],
        }

        # Helper to convert champion data to ID
        def to_champion_id(champ) -> Optional[int]:
            if isinstance(champ, int):
                return champ
            if isinstance(champ, str):
                if champ.isdigit():
                    return int(champ)
                return get_champion_id(champ)
            if isinstance(champ, dict):
                for key in ["id", "championId", "champion_id", "key"]:
                    if key in champ and champ[key]:
                        val = champ[key]
                        if isinstance(val, int):
                            return val
                        if isinstance(val, str) and val.isdigit():
                            return int(val)
                for key in ["name", "championName", "champion_name"]:
                    if key in champ and champ[key]:
                        return get_champion_id(champ[key])
            return None

        # Try to find game-specific data
        games = data.get("games", [])
        if games and len(games) >= int(game_num):
            game_data = games[int(game_num) - 1]
            data = game_data  # Use game-specific data

        # Common formats
        # Format: {bluePicks: [...], redPicks: [...], blueBans: [...], redBans: [...]}
        for key in ["bluePicks", "blue_picks", "blueTeam.picks", "blue.picks"]:
            if key in data:
                result["blue_picks"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["redPicks", "red_picks", "redTeam.picks", "red.picks"]:
            if key in data:
                result["red_picks"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["blueBans", "blue_bans", "blueTeam.bans", "blue.bans"]:
            if key in data:
                result["blue_bans"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["redBans", "red_bans", "redTeam.bans", "red.bans"]:
            if key in data:
                result["red_bans"] = [to_champion_id(c) for c in data[key]]
                break

        # Format: {teams: [{picks: [...], bans: [...]}, {...}]}
        if "teams" in data and isinstance(data["teams"], list) and len(data["teams"]) >= 2:
            blue_team = data["teams"][0]
            red_team = data["teams"][1]
            if not result["blue_picks"] and "picks" in blue_team:
                result["blue_picks"] = [to_champion_id(c) for c in blue_team["picks"]]
            if not result["red_picks"] and "picks" in red_team:
                result["red_picks"] = [to_champion_id(c) for c in red_team["picks"]]
            if not result["blue_bans"] and "bans" in blue_team:
                result["blue_bans"] = [to_champion_id(c) for c in blue_team["bans"]]
            if not result["red_bans"] and "bans" in red_team:
                result["red_bans"] = [to_champion_id(c) for c in red_team["bans"]]

        # Format: {actions: [{type: "pick"/"ban", team: "blue"/"red", champion: ...}]}
        if "actions" in data:
            for action in data["actions"]:
                champ_id = to_champion_id(action.get("champion") or action.get("championId"))
                if not champ_id:
                    continue
                team = str(action.get("team", "")).lower()
                action_type = str(action.get("type", "")).lower()
                if "blue" in team:
                    if "ban" in action_type:
                        result["blue_bans"].append(champ_id)
                    elif "pick" in action_type:
                        result["blue_picks"].append(champ_id)
                elif "red" in team:
                    if "ban" in action_type:
                        result["red_bans"].append(champ_id)
                    elif "pick" in action_type:
                        result["red_picks"].append(champ_id)

        # Filter out None values
        result["blue_bans"] = [b for b in result["blue_bans"] if b is not None]
        result["red_bans"] = [b for b in result["red_bans"] if b is not None]
        result["blue_picks"] = [p for p in result["blue_picks"] if p is not None]
        result["red_picks"] = [p for p in result["red_picks"] if p is not None]

        if any([result["blue_bans"], result["red_bans"], result["blue_picks"], result["red_picks"]]):
            return result

        return None

    except Exception as e:
        print(f"Error parsing drafter.lol response: {e}")
        return None


def parse_drafter_lol_html(html: str, game_num: str = "1") -> Optional[dict]:
    """Parse draft data from drafter.lol HTML page"""
    try:
        import json

        # Look for Next.js/React data patterns
        patterns = [
            r'__NEXT_DATA__["\']?\s*[>:]\s*(\{.+?\})\s*</script>',
            r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\});',
            r'"draft"\s*:\s*(\{[^}]+(?:\{[^}]*\}[^}]*)*\})',
            r'draft-data["\']?\s*[:=]\s*["\']?(\{.+?\})["\']?',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    # Navigate to draft data if nested
                    if "props" in data and "pageProps" in data["props"]:
                        data = data["props"]["pageProps"]
                    if "draft" in data:
                        data = data["draft"]
                    result = parse_drafter_lol_response(data, game_num)
                    if result:
                        return result
                except json.JSONDecodeError:
                    continue

        return None

    except Exception as e:
        print(f"Error parsing drafter.lol HTML: {e}")
        return None


async def parse_draftlol_url(url: str) -> Optional[dict]:
    """
    Parse a draftlol.dawe.gg URL to extract draft data.

    URL formats:
    - https://draftlol.dawe.gg/YIARt3s- (spectator view)
    - https://draftlol.dawe.gg/YIARt3s-/F7Nn7OwO (blue side view)
    - https://draftlol.dawe.gg/YIARt3s-/bjqXphld (red side view)
    """
    try:
        parsed = urlparse(url)

        # Check if it's a draftlol URL
        if "draftlol" not in parsed.netloc and "dawe.gg" not in parsed.netloc:
            return None

        # Extract draft ID from URL path
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]

        if not path_parts:
            return None

        # First part is the draft ID (e.g., YIARt3s-)
        draft_id = path_parts[0]

        async with httpx.AsyncClient() as client:
            # Try different API endpoints
            api_urls = [
                f"https://draftlol.dawe.gg/api/{draft_id}",
                f"https://draftlol.dawe.gg/api/draft/{draft_id}",
                f"https://draftlol.dawe.gg/api/drafts/{draft_id}",
            ]

            for api_url in api_urls:
                try:
                    response = await client.get(api_url, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        result = parse_draftlol_response(data)
                        if result:
                            return result
                except Exception:
                    continue

            # If no API works, try to scrape the page directly
            try:
                page_response = await client.get(url, timeout=10.0)
                if page_response.status_code == 200:
                    result = parse_draftlol_html(page_response.text)
                    if result:
                        return result
            except Exception as e:
                print(f"Error fetching page: {e}")

        return None

    except Exception as e:
        print(f"Error parsing draftlol URL: {e}")
        return None


def parse_draftlol_html(html: str) -> Optional[dict]:
    """
    Parse draft data from the HTML page.
    The data is often embedded in a script tag as JSON or JS variables.
    """
    try:
        # Look for draft data in script tags
        # Common patterns: window.__DRAFT__ = {...}, draftData = {...}, etc.

        # Pattern 1: JSON data in script
        json_patterns = [
            r'window\.__DRAFT__\s*=\s*(\{[^;]+\});?',
            r'window\.draftData\s*=\s*(\{[^;]+\});?',
            r'"draft"\s*:\s*(\{[^}]+\})',
            r'data-draft\s*=\s*["\'](\{[^"\']+\})["\']',
        ]

        import json

        for pattern in json_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    result = parse_draftlol_response(data)
                    if result:
                        return result
                except json.JSONDecodeError:
                    continue

        # Pattern 2: Look for champion images/picks in specific classes
        # Format: class="champion-pick" data-champion="Aatrox" or similar
        pick_pattern = r'(?:data-champion|champion-name|pick)["\']?\s*[:=]\s*["\']?([A-Za-z]+)["\']?'
        ban_pattern = r'(?:data-ban|ban-champion|banned)["\']?\s*[:=]\s*["\']?([A-Za-z]+)["\']?'

        picks = re.findall(pick_pattern, html, re.IGNORECASE)
        bans = re.findall(ban_pattern, html, re.IGNORECASE)

        if picks:
            # Assume first 5 are blue, next 5 are red
            blue_picks = [get_champion_id(p) for p in picks[:5]]
            red_picks = [get_champion_id(p) for p in picks[5:10]]
            blue_bans = [get_champion_id(b) for b in bans[:5]]
            red_bans = [get_champion_id(b) for b in bans[5:10]]

            return {
                "blue_bans": [b for b in blue_bans if b],
                "red_bans": [b for b in red_bans if b],
                "blue_picks": [p for p in blue_picks if p],
                "red_picks": [p for p in red_picks if p],
            }

        return None

    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None


def parse_draftlol_response(data: dict) -> Optional[dict]:
    """Parse the response from draftlol API"""
    try:
        result = {
            "blue_bans": [],
            "red_bans": [],
            "blue_picks": [],
            "red_picks": [],
        }

        # Helper to convert champion data to ID
        def to_champion_id(champ) -> Optional[int]:
            if isinstance(champ, int):
                return champ
            if isinstance(champ, str):
                # Could be name or ID as string
                if champ.isdigit():
                    return int(champ)
                return get_champion_id(champ)
            if isinstance(champ, dict):
                # Could be {id: 123} or {name: "Aatrox"} or {championId: 123}
                for key in ["id", "championId", "champion_id"]:
                    if key in champ and champ[key]:
                        return int(champ[key]) if str(champ[key]).isdigit() else None
                for key in ["name", "championName", "champion_name"]:
                    if key in champ and champ[key]:
                        return get_champion_id(champ[key])
            return None

        # Format 1: {bans: {blue: [...], red: [...]}, picks: {blue: [...], red: [...]}}
        if "bans" in data:
            bans = data["bans"]
            if isinstance(bans, dict):
                result["blue_bans"] = [to_champion_id(c) for c in bans.get("blue", [])]
                result["red_bans"] = [to_champion_id(c) for c in bans.get("red", [])]
            elif isinstance(bans, list):
                # Might be flat list: first 5 blue, next 5 red
                result["blue_bans"] = [to_champion_id(c) for c in bans[:5]]
                result["red_bans"] = [to_champion_id(c) for c in bans[5:10]]

        if "picks" in data:
            picks = data["picks"]
            if isinstance(picks, dict):
                result["blue_picks"] = [to_champion_id(c) for c in picks.get("blue", [])]
                result["red_picks"] = [to_champion_id(c) for c in picks.get("red", [])]
            elif isinstance(picks, list):
                result["blue_picks"] = [to_champion_id(c) for c in picks[:5]]
                result["red_picks"] = [to_champion_id(c) for c in picks[5:10]]

        # Format 2: {blueBans: [...], redBans: [...], bluePicks: [...], redPicks: [...]}
        for key in ["blueBans", "blue_bans", "blueban"]:
            if key in data:
                result["blue_bans"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["redBans", "red_bans", "redban"]:
            if key in data:
                result["red_bans"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["bluePicks", "blue_picks", "bluepick"]:
            if key in data:
                result["blue_picks"] = [to_champion_id(c) for c in data[key]]
                break
        for key in ["redPicks", "red_picks", "redpick"]:
            if key in data:
                result["red_picks"] = [to_champion_id(c) for c in data[key]]
                break

        # Format 3: {teams: [{bans: [...], picks: [...]}, {...}]}
        if "teams" in data and isinstance(data["teams"], list) and len(data["teams"]) >= 2:
            blue_team = data["teams"][0]
            red_team = data["teams"][1]
            if "bans" in blue_team:
                result["blue_bans"] = [to_champion_id(c) for c in blue_team["bans"]]
            if "picks" in blue_team:
                result["blue_picks"] = [to_champion_id(c) for c in blue_team["picks"]]
            if "bans" in red_team:
                result["red_bans"] = [to_champion_id(c) for c in red_team["bans"]]
            if "picks" in red_team:
                result["red_picks"] = [to_champion_id(c) for c in red_team["picks"]]

        # Format 4: {draft: {actions: [{type: "ban", team: "blue", champion: ...}, ...]}}
        if "draft" in data and "actions" in data.get("draft", {}):
            for action in data["draft"]["actions"]:
                champ_id = to_champion_id(action.get("champion") or action.get("championId"))
                if not champ_id:
                    continue
                team = action.get("team", "").lower()
                action_type = action.get("type", "").lower()
                if team == "blue":
                    if "ban" in action_type:
                        result["blue_bans"].append(champ_id)
                    elif "pick" in action_type:
                        result["blue_picks"].append(champ_id)
                elif team == "red":
                    if "ban" in action_type:
                        result["red_bans"].append(champ_id)
                    elif "pick" in action_type:
                        result["red_picks"].append(champ_id)

        # Filter out None values
        result["blue_bans"] = [b for b in result["blue_bans"] if b is not None]
        result["red_bans"] = [b for b in result["red_bans"] if b is not None]
        result["blue_picks"] = [p for p in result["blue_picks"] if p is not None]
        result["red_picks"] = [p for p in result["red_picks"] if p is not None]

        # Only return if we found some data
        if any([result["blue_bans"], result["red_bans"], result["blue_picks"], result["red_picks"]]):
            return result

        return None

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
        "message": "Import automatique non disponible pour ce site (les donnees sont chargees cote client). Utilisez l'entree manuelle avec les noms des champions (ex: Aatrox, Ahri, Zed).",
        "data": None,
    }
