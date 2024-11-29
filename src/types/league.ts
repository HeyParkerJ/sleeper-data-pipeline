// NOTE: AI generated, not confirmed to be good

export type LeagueStatus = 'pre_draft' | 'drafting' | 'in_season' | 'complete';

export type SportType = 'nfl' | 'nba' | 'mlb'; // Expanded for other sports Sleeper supports

export type SeasonType = 'regular' | 'playoffs';

// League Settings interface - we can expand this based on actual settings object
export interface LeagueSettings {
    // Common league settings
    league_type?: number;
    draft_type?: number;
    trade_deadline?: string;
    waiver_type?: number;
    waiver_day_of_week?: number;
    start_week?: number;
    playoff_week_start?: number;
    daily_waivers?: boolean;
    reserve_slots?: number;
    playoff_teams?: number;
    num_teams?: number;
    [key: string]: any; // Allow for additional settings
}

// Scoring Settings interface - can be expanded based on actual scoring rules
export interface ScoringSettings {
    // Common scoring settings
    pass_td?: number;
    pass_yd?: number;
    pass_int?: number;
    rush_td?: number;
    rush_yd?: number;
    rec_td?: number;
    rec_yd?: number;
    fgm?: number;
    xpm?: number;
    def_td?: number;
    pts_allow?: number;
    [key: string]: number | undefined; // All scoring settings are numbers
}

// Possible roster positions in NFL fantasy
export type RosterPosition = 
    | 'QB'  // Quarterback
    | 'RB'  // Running Back
    | 'WR'  // Wide Receiver
    | 'TE'  // Tight End
    | 'K'   // Kicker
    | 'DEF' // Defense
    | 'DL'  // Defensive Line
    | 'LB'  // Linebacker
    | 'DB'  // Defensive Back
    | 'FLEX'// RB/WR/TE
    | 'SUPER_FLEX' // QB/RB/WR/TE
    | 'IDP_FLEX' // DL/LB/DB
    | 'BN'  // Bench
    | 'IR'  // Injured Reserve
    | 'WRRB_FLEX'; // WR/RB

// Main League interface
export interface League {
    total_rosters: number;
    status: LeagueStatus;
    sport: SportType;
    settings: LeagueSettings;
    season_type: SeasonType;
    season: string;
    scoring_settings: ScoringSettings;
    roster_positions: RosterPosition[];
    previous_league_id: string;
    name: string;
    league_id: string;
    draft_id: string;
    avatar: string;
}

// Type for the API response which is an array of leagues
export type LeaguesResponse = League[];

// Utility type for API endpoint
export interface SleeperApiEndpoints {
    leagues: {
        response: LeaguesResponse;
        // Add request parameters if needed
        // request: {
        //     user_id: string;
        // };
    };
}