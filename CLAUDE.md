# CLAUDE.md - Oracle North Star

## Objectifs MVP

**Oracle** est une app de coaching pour une équipe League of Legends (≈20 utilisateurs/jour).

### Fonctionnalités MVP prioritaires

1. **Accès simplifié** : code d'accès partagé + choix de rôle (Coach/Joueur/Head Coach)
2. **Gestion équipe** : 5 joueurs (Top/Jungle/Mid/ADC/Supp) + coachs positionnels + profils Riot multiples
3. **Statistiques** :
   - Stats pures (CS/min, KDA, gold/min, vision/min, KP%)
   - Stats comportementales (early deaths, roams, objectifs)
   - Source : SoloQ obligatoire + tag manuel "competitive"
4. **Espace coach-joueur** : objectifs + notes par joueur
5. **Draft planner** : historique drafts (picks/bans/résultat) + winrate global

### Non-objectifs (hors MVP)

- Création de comptes utilisateurs / MDP / MFA
- Oracle avancé (matchups stats, predictions)
- Champion builds automatisés
- CI/CD
- Scalabilité complexe
- Event bus / microservices

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI (Python 3.12), Pydantic, SQLAlchemy/SQLModel, Alembic |
| Database | PostgreSQL |
| Frontend | Vue 3 + TypeScript + Vite + Pinia + Vue Router + Tailwind CSS |
| Infra | Docker Compose (local) |
| Tests | pytest (backend), ruff (linter/formatter) |
| API Docs | OpenAPI (auto-généré par FastAPI) |
| Deployment | Railway (production future) |

---

## Architecture dossiers

```
oracle/
├── CLAUDE.md (ce fichier)
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml (ruff config)
│   ├── alembic/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/ (SQLAlchemy models)
│   │   ├── schemas/ (Pydantic schemas)
│   │   ├── routers/ (FastAPI routers)
│   │   ├── services/ (business logic)
│   │   └── riot/ (Riot API client + cache)
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/ (Pinia)
│   │   ├── views/
│   │   ├── components/
│   │   ├── api/ (typed API client)
│   │   └── types/
│   └── public/
└── docs/ (optionnel)
```

---

## Conventions

### Naming

- **Python** : snake_case (fonctions, variables), PascalCase (classes)
- **TypeScript** : camelCase (variables, fonctions), PascalCase (types, composants Vue)
- **Fichiers** : kebab-case.vue, snake_case.py
- **Routes API** : `/api/v1/resource` (pluriel si collection)

### Style

- **Backend** : ruff (formatter + linter), line-length = 100
- **Frontend** : Prettier + ESLint (Vue/TS), single quotes, 2 spaces
- **Commits** : `type(scope): message` (ex: `feat(api): add player CRUD`)

### Tests

- **Backend** : tests unitaires dans `/backend/tests`, nommage `test_*.py`
- **Frontend** : optionnel pour MVP (prévoir Vitest si temps)
- Coverage minimal : endpoints critiques (auth, CRUD players)

---

## Modèle de données MVP

### Tables principales

```sql
-- Players
players
  id (PK)
  summoner_name (unique, indexed)
  role (enum: top/jungle/mid/adc/support)
  created_at
  updated_at

-- RiotAccounts (1 joueur peut avoir plusieurs comptes)
riot_accounts
  id (PK)
  player_id (FK -> players.id)
  puuid (unique, indexed)
  summoner_name
  tag_line
  is_main (boolean)
  created_at

-- Notes/Objectives
player_notes
  id (PK)
  player_id (FK)
  author_role (enum: coach/head_coach)
  note_type (enum: objective/note)
  content (text)
  created_at
  updated_at

-- Drafts
drafts
  id (PK)
  date
  opponent_name
  blue_side (boolean)
  picks (jsonb: array de champion IDs)
  bans (jsonb: array de champion IDs)
  result (enum: win/loss/null)
  notes (text, optional)
  created_at

-- Games (cache stats Riot)
games
  id (PK)
  riot_account_id (FK)
  match_id (unique, indexed)
  game_type (enum: soloq/competitive)
  champion_id
  role
  stats (jsonb: kda, cs, vision, etc.)
  game_duration
  game_date
  created_at
```

### Relations

- 1 player → N riot_accounts
- 1 player → N player_notes
- 1 riot_account → N games

---

## Endpoints API MVP

### Auth
- `POST /api/v1/auth/validate-code` : valide le code d'accès + retourne token simple (JWT léger)

### Players
- `GET /api/v1/players` : liste joueurs
- `POST /api/v1/players` : créer joueur
- `GET /api/v1/players/{id}` : détails joueur + riot_accounts
- `PATCH /api/v1/players/{id}` : update joueur
- `DELETE /api/v1/players/{id}` : supprimer joueur

### Riot Accounts
- `POST /api/v1/players/{id}/riot-accounts` : ajouter compte Riot
- `DELETE /api/v1/riot-accounts/{id}` : supprimer compte

### Stats
- `GET /api/v1/stats/player/{player_id}` : synthèse stats joueur (tous comptes)
- `GET /api/v1/stats/lane/{lane}` : stats lane (ex: botlane = adc + support)
- `POST /api/v1/stats/refresh/{riot_account_id}` : fetch nouveaux matchs Riot API

### Notes/Objectives
- `GET /api/v1/players/{id}/notes` : liste notes/objectifs
- `POST /api/v1/players/{id}/notes` : créer note/objectif
- `PATCH /api/v1/notes/{id}` : update note
- `DELETE /api/v1/notes/{id}` : supprimer note

### Drafts
- `GET /api/v1/drafts` : liste drafts
- `POST /api/v1/drafts` : créer draft
- `GET /api/v1/drafts/{id}` : détails draft
- `DELETE /api/v1/drafts/{id}` : supprimer draft

### Health
- `GET /health` : healthcheck

---

## Riot API - Règles

### Rate Limits (Développement)

- 20 requests / 1 second
- 100 requests / 2 minutes

### Stratégie

1. **Client unique** : module `app/riot/client.py` avec retry + backoff exponentiel
2. **Cache DB** : stocker matchs dans table `games` (éviter re-fetch)
3. **Cache Redis** (optionnel futur) : TTL court pour puuid lookups
4. **Endpoints utilisés** :
   - `/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}` → PUUID
   - `/lol/summoner/v4/summoners/by-puuid/{puuid}` → Summoner info
   - `/lol/match/v5/matches/by-puuid/{puuid}/ids` → Match IDs
   - `/lol/match/v5/matches/{matchId}` → Match details

### Gestion erreurs

- 429 (rate limit) : retry avec header `Retry-After`
- 404 : compte inexistant
- 5xx : retry max 3 fois

### Variables d'environnement

```
RIOT_API_KEY=RGAPI-...
RIOT_API_REGION=euw1 (ou configurable)
RIOT_API_CACHE_TTL=3600 (secondes)
```

---

## Déploiement

### Local (MVP)
```bash
docker-compose up --build
```

### Production (Railway - futur)

- Backend : service FastAPI (Dockerfile)
- Frontend : service Vite build (serve static)
- PostgreSQL : managed Railway Postgres
- Variables d'env via Railway UI
- Pas de CI/CD pour l'instant (deploy manuel)

---

## Prochaines étapes (post-scaffold)

1. ✅ Scaffold complet (structure + docker)
2. 🔄 Implémenter endpoints MVP (CRUD players, auth, notes, drafts)
3. 🔄 Riot API client fonctionnel + cache
4. 🔄 Frontend : écrans code d'accès, dashboard, player profile, draft planner
5. 🔄 Stats computation logic (agrégation games → metrics)
6. 🔄 Tests backend (pytest sur endpoints critiques)
7. 🔄 Polish UI/UX (Tailwind composants)
8. 🔄 Deploy Railway (config + test prod)

---

## Décisions clés

| Décision | Justification |
|----------|---------------|
| Pas d'auth complexe | 20 users/jour, code partagé suffit (JWT simple sans refresh) |
| SQLAlchemy (pas SQLModel) | Maturité + flexibilité migrations Alembic |
| Postgres (pas SQLite) | Prêt prod, jsonb pour stats/drafts |
| Pas de Redis initialement | Cache DB suffit, ajout facile si besoin |
| Tailwind (pas UI lib) | Flexibilité + légèreté, pas de dépendance lourde |
| Monorepo simple | Pas besoin turborepo/nx pour 2 apps |
| Docker Compose | Dev local simple, Railway utilise Dockerfiles |

---

**Version** : 1.0 (2026-01-17)
**Maintainer** : Claude Code
**Statut** : Scaffold MVP en cours
