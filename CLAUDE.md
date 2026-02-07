# CLAUDE.md - Oracle North Star

## Objectifs MVP

**Oracle** est une app de coaching pour une equipe League of Legends (~20 utilisateurs/jour).

### Fonctionnalites implementees

1. **Acces simplifie** : code d'acces par equipe (multi-tenant) + choix de role (Coach/Joueur/Head Coach)
2. **Gestion equipe** : 5 joueurs (Top/Jungle/Mid/ADC/Supp) + coachs positionnels + profils Riot multiples (main + smurfs)
3. **Statistiques** :
   - Stats pures (CS/min, KDA, gold/min, vision/min, KP%) agregees sur tous les comptes
   - Stats ranked (W/L, winrate) combinees depuis tous les comptes Riot
   - Champion stats (winrate, KDA par champion)
   - SoloQ Activity view (grille hebdo, detection smurf, matchups)
   - Total LP equipe (Master+) sur le dashboard
4. **Espace coach-joueur** : objectifs + notes par joueur
5. **Draft planner** : DraftSeries (BO1/BO3/BO5) avec games, import JSON V4/V5, historique
6. **Calendrier** : events (scrim, official_match, training), auto-creation DraftSeries, badges W/L
7. **Tier List** : tier list de champions par joueur
8. **Scrim Management** : equipes adverses, reviews, scouting joueurs
9. **Sponsors page** : highlights equipe (winrate, pentakills, matchs recents)
10. **Rank tracking** : current + peak rank, historique de rank, graphes

### Non-objectifs (hors MVP)

- Oracle avance (matchups stats, predictions)
- Champion builds automatises
- CI/CD
- Scalabilite complexe
- Event bus / microservices

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI (Python 3.12), Pydantic, SQLAlchemy, Alembic |
| Database | PostgreSQL |
| Frontend | Vue 3 + TypeScript + Vite + Pinia + Vue Router + Tailwind CSS |
| Infra | Docker Compose (local) |
| Tests | pytest (backend), ruff (linter/formatter) |
| API Docs | OpenAPI (auto-genere par FastAPI) |
| Deployment | Railway (production future) |

---

## Architecture dossiers

```
TSC/
├── CLAUDE.md
├── docker-compose.yml
├── .env
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml (ruff config)
│   ├── alembic/
│   │   └── versions/ (15 migrations)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── player.py (Player, Role)
│   │   │   ├── riot_account.py (RiotAccount)
│   │   │   ├── coach.py (Coach)
│   │   │   ├── game.py (Game, GameType)
│   │   │   ├── player_note.py (PlayerNote)
│   │   │   ├── draft.py (DraftSeries, DraftGame, Draft)
│   │   │   ├── team.py (Team)
│   │   │   ├── calendar.py (CalendarEvent, PlayerAvailability)
│   │   │   ├── tier_list.py (ChampionTier)
│   │   │   ├── rank_history.py (RankHistory)
│   │   │   └── scrim_management.py (OpponentTeam, ScrimReview, ScoutedPlayer)
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── players.py
│   │   │   ├── coaches.py
│   │   │   ├── games.py
│   │   │   ├── player_notes.py
│   │   │   ├── drafts.py
│   │   │   ├── draft_series.py
│   │   │   ├── riot_accounts.py
│   │   │   ├── stats.py
│   │   │   ├── admin.py
│   │   │   ├── calendar.py
│   │   │   ├── tier_list.py
│   │   │   └── scrim_management.py
│   │   ├── services/
│   │   │   ├── player_service.py
│   │   │   ├── coach_service.py
│   │   │   ├── player_note_service.py
│   │   │   ├── draft_service.py
│   │   │   ├── draft_import_service.py
│   │   │   ├── riot_account_service.py
│   │   │   ├── stats_service.py
│   │   │   ├── admin_service.py
│   │   │   ├── calendar_service.py
│   │   │   ├── scrim_management_service.py
│   │   │   ├── tier_list_service.py
│   │   │   ├── match_import_service.py
│   │   │   └── email_service.py
│   │   └── riot/
│   │       └── client.py (RiotAPIClient avec retry + backoff)
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/index.ts
│   │   ├── stores/ (Pinia - auth, etc.)
│   │   ├── api/index.ts (typed API client)
│   │   ├── types/index.ts
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RoleSelectionView.vue
│   │   │   ├── PlayerSelectionView.vue
│   │   │   ├── CoachSelectionView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── PlayerView.vue
│   │   │   ├── AnalyticsView.vue
│   │   │   ├── SoloQActivityView.vue
│   │   │   ├── CalendarView.vue
│   │   │   ├── PlanningView.vue
│   │   │   ├── DraftsView.vue
│   │   │   ├── ScrimsView.vue
│   │   │   ├── CoachesManagementView.vue
│   │   │   ├── TierListView.vue
│   │   │   ├── AdminView.vue
│   │   │   └── SponsorsView.vue
│   │   └── components/
│   │       ├── AppNavbar.vue
│   │       ├── AppLogo.vue
│   │       ├── RankBadge.vue
│   │       ├── RankGraph.vue
│   │       ├── StatsGraph.vue
│   │       ├── ChampionStats.vue
│   │       └── GameDetailModal.vue
│   └── public/
```

---

## Conventions

### Naming

- **Python** : snake_case (fonctions, variables), PascalCase (classes)
- **TypeScript** : camelCase (variables, fonctions), PascalCase (types, composants Vue)
- **Fichiers** : kebab-case.vue (PascalCase aussi accepte), snake_case.py
- **Routes API** : `/api/v1/resource` (pluriel si collection)

### Style

- **Backend** : ruff (formatter + linter), line-length = 100
- **Frontend** : single quotes, 2 spaces
- **Commits** : `type(scope): message` (ex: `feat(api): add player CRUD`)

---

## Modele de donnees (actuel)

### Tables principales

```sql
-- Teams (multi-tenant)
teams
  id (PK), name, access_code (unique), created_at

-- Players
players
  id (PK), team_id (FK), summoner_name, role, email, created_at, updated_at

-- RiotAccounts (1 joueur -> N comptes, 1 main + smurfs)
riot_accounts
  id (PK), player_id (FK), puuid (unique), summoner_id,
  summoner_name, tag_line, is_main,
  rank_tier, rank_division, lp, wins, losses,
  peak_tier, peak_division, peak_lp,
  last_refreshed_at, created_at, updated_at

-- RankHistory (historique de rang)
rank_history
  id (PK), riot_account_id (FK), tier, division, lp, recorded_at

-- Games (cache stats Riot)
games
  id (PK), riot_account_id (FK), match_id (unique),
  game_type (soloq/competitive), champion_id, role,
  stats (jsonb), game_duration, game_date, is_pentakill, created_at

-- Coaches
coaches
  id (PK), team_id (FK), name, role, created_at

-- PlayerNotes
player_notes
  id (PK), player_id (FK), coach_id (FK), author_role, note_type, content,
  created_at, updated_at

-- DraftSeries (BO1/BO3/BO5)
draft_series
  id (PK), team_id (FK), date, opponent_name, format, notes, created_at

-- DraftGames (1 serie -> N games)
draft_games
  id (PK), series_id (FK), game_number, blue_side, result,
  blue_bans/red_bans/blue_picks/red_picks (jsonb),
  match_data (jsonb, import V4/V5), notes, created_at

-- CalendarEvents
calendar_events
  id (PK), team_id (FK), draft_series_id (FK, nullable),
  event_type (scrim/official_match/training/other),
  title, date, start_time, end_time, opponent_name, opponent_players (jsonb),
  location, notes, created_at

-- PlayerAvailability
player_availabilities
  id (PK), player_id (FK), date, time_slot, is_available

-- ChampionTier (tier list)
champion_tiers
  id (PK), player_id (FK), team_id (FK), champion_id, tier, notes

-- ScrimManagement
opponent_teams, scrim_reviews, scouted_players
```

### Relations principales

- 1 team -> N players, N coaches, N draft_series, N calendar_events
- 1 player -> N riot_accounts, N player_notes, N availabilities, N champion_tiers
- 1 riot_account -> N games, N rank_history
- 1 draft_series -> N draft_games
- 1 calendar_event -> 0..1 draft_series (auto-cree pour scrims)

---

## Endpoints API (principaux)

### Auth
- `POST /api/v1/auth/validate-code` : valide code equipe, retourne token JWT

### Players
- `GET/POST /api/v1/players` : liste / creer joueur
- `GET/PATCH/DELETE /api/v1/players/{id}` : detail / update / supprimer

### Riot Accounts
- `POST /api/v1/players/{id}/riot-accounts` : ajouter compte Riot
- `DELETE /api/v1/riot-accounts/{id}` : supprimer compte
- `PATCH /api/v1/riot-accounts/{id}/set-main` : definir compte principal
- `PATCH /api/v1/riot-accounts/{id}/rank` : mise a jour rank manuelle

### Stats
- `GET /api/v1/stats/player/{player_id}` : stats joueur (tous comptes agreges)
- `GET /api/v1/stats/lane/{lane}` : stats lane (botlane = adc + support)
- `POST /api/v1/stats/refresh/{riot_account_id}` : fetch Riot API
- `GET /api/v1/stats/champions/{player_id}` : stats par champion
- `GET /api/v1/stats/activity/{team_id}` : grille SoloQ hebdo
- `GET /api/v1/stats/highlights/{team_id}` : highlights equipe (sponsors)

### Draft Series
- `GET/POST /api/v1/draft-series` : liste / creer series
- `GET/DELETE /api/v1/draft-series/{id}` : detail / supprimer
- `POST /api/v1/draft-series/{id}/games` : ajouter game a serie
- `POST /api/v1/draft-series/{id}/import` : import JSON V4/V5

### Calendar
- `GET/POST /api/v1/calendar/events` : liste / creer event (auto-cree DraftSeries pour scrims)
- `PATCH/DELETE /api/v1/calendar/events/{id}` : update / supprimer

### Notes, Coaches, TierList, ScrimManagement, Admin, Games
- CRUD standard sur chaque ressource

---

## Riot API

### Rate Limits (Dev)
- 20 req/s, 100 req/2min

### Strategie
1. **Client unique** : `app/riot/client.py` avec retry + backoff exponentiel
2. **Cache DB** : matchs stockes dans `games` (eviter re-fetch)
3. **Rank auto** : `fetch_and_update_rank()` met a jour tier/division/lp/wins/losses + peak
4. **Match import** : `fetch_and_store_matches()` stocke les 20 derniers matchs

### Endpoints Riot utilises
- `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` -> PUUID
- `/lol/summoner/v4/summoners/by-puuid/{puuid}` -> Summoner info
- `/lol/league/v4/entries/by-summoner/{summonerId}` -> Rank info
- `/lol/match/v5/matches/by-puuid/{puuid}/ids` -> Match IDs
- `/lol/match/v5/matches/{matchId}` -> Match details

### Gestion erreurs
- 429 : retry avec `Retry-After`
- 401/403 : message clair "API key invalid/expired"
- 404 : compte inexistant
- 5xx : retry max 3 fois

---

## Deploiement

### Local
```bash
docker-compose up --build
```

### Production (Railway - futur)
- Backend : FastAPI (Dockerfile)
- Frontend : Vite build (serve static)
- PostgreSQL : managed Railway Postgres

---

## Avancement

### Fait
- [x] Scaffold complet (structure + docker + multi-tenant)
- [x] Auth par code d'equipe (JWT)
- [x] CRUD Players + Coaches + Notes
- [x] Riot API client (PUUID, rank, matches, retry/backoff)
- [x] Multi-comptes Riot (main + smurfs, toggle main)
- [x] Stats joueur (agregation tous comptes, ranked W/L combines)
- [x] Stats champion (winrate, KDA par champion)
- [x] SoloQ Activity (grille hebdo, detection smurf, matchups)
- [x] Dashboard (LP total Master+, stats equipe)
- [x] Draft planner (DraftSeries BO1/3/5, import JSON V4/V5)
- [x] Calendrier (events, auto-creation DraftSeries, badges W/L, bouton "Voir Draft")
- [x] GameDetailModal (voir stats match depuis calendrier)
- [x] Tier List par joueur
- [x] Scrim Management (adversaires, reviews, scouting)
- [x] Sponsors page (highlights equipe)
- [x] Rank tracking (current + peak, historique, graphes)
- [x] Admin panel

### A faire
- [ ] Tests backend (pytest sur endpoints critiques)
- [ ] Deploy Railway (config + test prod)
- [ ] Stats comportementales (early deaths, roams, objectifs)
- [ ] Invitations calendrier Google (email_service existe mais pas branche)

---

## Decisions cles

| Decision | Justification |
|----------|---------------|
| Multi-tenant par code equipe | Simple, pas de MDP, ~20 users/jour |
| SQLAlchemy (pas SQLModel) | Maturite + flexibilite migrations Alembic |
| PostgreSQL + jsonb | Stats/drafts en JSON, pret prod |
| Tailwind CSS | Flexibilite + legerete |
| Monorepo simple | 2 apps, pas besoin de tooling complexe |
| Docker Compose | Dev local simple, Railway utilise Dockerfiles |
| Rank data sur RiotAccount | Pas besoin table separee, refresh via Riot API |
| DraftSeries auto-cree | A la creation d'un scrim, serie draft liee automatiquement |

---

**Version** : 2.0 (2026-02-07)
**Maintainer** : Claude Code
**Statut** : MVP fonctionnel, en iteration
