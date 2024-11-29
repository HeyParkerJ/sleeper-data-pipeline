import path from "path";
import fs from 'fs';
import { SleeperPlayer } from "../types/SleeperPlayer";

export interface SleeperLeagueResponse {
  total_rosters: number;
  status: 'pre_draft' | 'drafting' | 'in_season' | 'complete';
  sport: string;
  settings: Record<string, any>;
  season_type: string;
  season: string;
  scoring_settings: Record<string, any>;
  roster_positions: string[];
  previous_league_id: string;
  name: string;
  league_id: string;
  draft_id: string;
  avatar: string;
}

export interface SleeperPlayersResponse {
    [key: string]: SleeperPlayer;
}

export class SleeperApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'SleeperApiError';
  }
}

// Configuration interface for the client
export interface SleeperApiConfig {
  baseUrl?: string;
  timeout?: number;
  retries?: number;
}

interface RequestConfig<T> {
  endpoint: string;
  entityName: string;
  entityId: string;
  transform?: (data: any) => T;
}

export class SleeperApiClient {
  private baseUrl: string;
  private timeout: number;
  private retries: number;

  constructor(config: SleeperApiConfig = {}) {
    this.baseUrl = config.baseUrl || 'https://api.sleeper.app/v1';
    this.timeout = config.timeout || 5000;
    this.retries = config.retries || 1;
  }

  private async makeRequest<T>({
    endpoint,
    entityName,
    entityId,
    transform = (data: any) => data as T
  }: RequestConfig<T>): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.retries; attempt++) {
      try {
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
          signal: AbortSignal.timeout(this.timeout),
        });

        if (!response.ok) {
          if (response.status === 404) {
            throw new SleeperApiError(
              `${entityName} with ID ${entityId} not found`,
              404
            );
          }

          throw new SleeperApiError(
            `API request failed with status ${response.status}`,
            response.status,
            await response.json().catch(() => null)
          );
        }

        const data = await response.json();
        return transform(data);

      } catch (error) {
        lastError = error as Error;

        // Don't retry 404s or other client errors
        if (error instanceof SleeperApiError && error.statusCode && error.statusCode < 500) {
          throw error;
        }

        // If this is the last attempt, throw the error
        if (attempt === this.retries - 1) {
          throw new SleeperApiError(
            `Failed to fetch ${entityName} after ${this.retries} attempts: ${lastError.message}`
          );
        }

        // Wait before retrying (with exponential backoff)
        await new Promise(resolve =>
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }

    // This should never be reached due to the throw in the loop
    throw lastError || new Error('Unknown error occurred');
  }

  /**
   * Fetches a specific league by ID
   * @param leagueId - The ID of the league to retrieve
   * @returns Promise containing the league data
   * @throws SleeperApiError if the request fails
   */
  async getLeague(leagueId: string): Promise<SleeperLeagueResponse> {
    return this.makeRequest<SleeperLeagueResponse>({
      endpoint: `/league/${leagueId}`,
      entityName: 'League',
      entityId: leagueId
    });
  }

  /**
   * Fetches all players from sleeper - obviously limit this call
   * @returns Promise containing the player data
   * @throws SleeperApiError if the request fails
   */
  async getPlayers(): Promise<SleeperPlayersResponse> {
    return this.makeRequest<SleeperPlayersResponse>({
      endpoint: `/players/nfl`,
      entityName: 'Players',
      entityId: 'nfl'
    });
  }

  async mockGetPlayers() {
    try {
      const filePath = path.join(__dirname, '../data', 'MockSleeperPlayers.json');
      const jsonData = fs.readFileSync(filePath, 'utf-8');
      return JSON.parse(jsonData);
    } catch (error) {
      console.error('Error reading MockSleeperPlayers.json:', error);
      return null;
    }
  }
}