// Champion data utility
// Fetches champion data from DataDragon API

interface ChampionData {
  id: string
  key: string
  name: string
}

interface ChampionCache {
  data: Record<number, ChampionData>
  loaded: boolean
}

const championCache: ChampionCache = {
  data: {},
  loaded: false
}

// Get latest DDragon version
async function getLatestVersion(): Promise<string> {
  try {
    const response = await fetch('https://ddragon.leagueoflegends.com/api/versions.json')
    const versions = await response.json()
    return versions[0] // Latest version
  } catch (error) {
    console.error('Failed to fetch DDragon version:', error)
    return '14.24.1' // Fallback version
  }
}

// Load all champion data from DataDragon
export async function loadChampionData(): Promise<void> {
  if (championCache.loaded) return

  try {
    const version = await getLatestVersion()
    const response = await fetch(
      `https://ddragon.leagueoflegends.com/cdn/${version}/data/en_US/champion.json`
    )
    const data = await response.json()

    // Build cache with champion key (numeric ID) as index
    for (const champId in data.data) {
      const champ = data.data[champId]
      championCache.data[parseInt(champ.key)] = {
        id: champ.id,
        key: champ.key,
        name: champ.name
      }
    }

    championCache.loaded = true
    console.log('Champion data loaded:', Object.keys(championCache.data).length, 'champions')
  } catch (error) {
    console.error('Failed to load champion data:', error)
  }
}

// Get champion name by numeric ID
export function getChampionName(championId: number): string {
  const champ = championCache.data[championId]
  return champ?.name || `Champion ${championId}`
}

// Get champion icon URL by numeric ID
export function getChampionIconUrl(championId: number): string {
  const champ = championCache.data[championId]
  if (!champ) {
    return `https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/${championId}.png`
  }
  // Use DDragon for icon
  return `https://ddragon.leagueoflegends.com/cdn/14.24.1/img/champion/${champ.id}.png`
}

// Get all loaded champions
export function getAllChampions(): Record<number, ChampionData> {
  return championCache.data
}

// Check if champion data is loaded
export function isChampionDataLoaded(): boolean {
  return championCache.loaded
}

// Normalize champion name for comparison (remove spaces, accents, lowercase)
function normalizeChampionName(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove accents
    .replace(/[^a-z0-9]/g, '') // Remove non-alphanumeric
}

// Get champion ID by name (fuzzy match)
export function getChampionIdByName(name: string): number | null {
  if (!name || !championCache.loaded) return null

  const normalized = normalizeChampionName(name)

  // Direct match by normalized name
  for (const [id, champ] of Object.entries(championCache.data)) {
    if (normalizeChampionName(champ.name) === normalized) {
      return parseInt(id)
    }
    // Also try matching the internal ID (e.g., "MonkeyKing" for Wukong)
    if (normalizeChampionName(champ.id) === normalized) {
      return parseInt(id)
    }
  }

  // Partial match (starts with)
  for (const [id, champ] of Object.entries(championCache.data)) {
    if (normalizeChampionName(champ.name).startsWith(normalized)) {
      return parseInt(id)
    }
  }

  return null
}

// Parse a string that could be champion names or IDs (comma/space separated)
export function parseChampionInput(input: string): number[] {
  if (!input || !input.trim()) return []

  // Split by comma, semicolon, or multiple spaces
  const parts = input.split(/[,;]+|\s{2,}/).map(p => p.trim()).filter(Boolean)

  const results: number[] = []

  for (const part of parts) {
    // If it's a number, use it directly
    if (/^\d+$/.test(part)) {
      results.push(parseInt(part))
      continue
    }

    // Try to find champion by name
    const id = getChampionIdByName(part)
    if (id) {
      results.push(id)
    } else {
      console.warn(`Champion not found: "${part}"`)
    }
  }

  return results
}

// Get champion suggestions for autocomplete
export function searchChampions(query: string, limit = 10): Array<{ id: number; name: string }> {
  if (!query || !championCache.loaded) return []

  const normalized = normalizeChampionName(query)
  const results: Array<{ id: number; name: string; score: number }> = []

  for (const [id, champ] of Object.entries(championCache.data)) {
    const champNorm = normalizeChampionName(champ.name)

    // Exact start match gets highest score
    if (champNorm.startsWith(normalized)) {
      results.push({ id: parseInt(id), name: champ.name, score: 100 - champNorm.length })
    }
    // Contains match gets lower score
    else if (champNorm.includes(normalized)) {
      results.push({ id: parseInt(id), name: champ.name, score: 50 - champNorm.length })
    }
  }

  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ id, name }) => ({ id, name }))
}
