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
