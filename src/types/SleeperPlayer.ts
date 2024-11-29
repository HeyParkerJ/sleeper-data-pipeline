export interface DBSleeperPlayer {
    // Core identifiers and info
    player_id: string;
    sleeper_id: string;
    sport: string;
    status: string;
    active: boolean;

    // Player names
    first_name: string;
    last_name: string;
    full_name: string;
    search_first_name: string | null;
    search_last_name: string | null;
    search_full_name: string | null;
    search_rank: number | null;
    hashtag: string | null;

    // Personal info
    age: number | null;
    birth_date: string | null;
    birth_city: string | null;
    birth_state: string | null;
    birth_country: string | null;
    height: string | null;
    weight: string | null;
    college: string | null;
    high_school: string | null;
    years_exp: number | null;

    // Team and depth chart info
    team: string | null;
    team_abbr: string | null;
    team_changed_at: string | null;
    position: string;
    fantasy_positions: string[];
    number: number | null;
    depth_chart_order: number | null;
    depth_chart_position: string | null;
    practice_participation: string | null;
    practice_description: string | null;

    // Injury information
    injury_status: string | null;
    injury_body_part: string | null;
    injury_notes: string | null;
    injury_start_date: string | null;

    // External IDs
    espn_id: number | null;
    yahoo_id: number | null;
    stats_id: number | null;
    sportradar_id: string | null;
    rotowire_id: number | null;
    fantasy_data_id: number | null;
    gsis_id: string | null;
    rotoworld_id: string | null;

    // Additional metadata
    metadata: {
        [key: string]: any;
    };
    news_updated: string | null;
}

export interface SleeperPlayer {
    // Core identifiers and info
    player_id: string;
    sport: string;
    status: string;
    active: boolean;

    // Player names
    first_name: string;
    last_name: string;
    full_name: string;
    search_first_name: string | null;
    search_last_name: string | null;
    search_full_name: string | null;
    search_rank: number | null;
    hashtag: string | null;

    // Personal info
    age: number | null;
    birth_date: string | null;
    birth_city: string | null;
    birth_state: string | null;
    birth_country: string | null;
    height: string | null;
    weight: string | null;
    college: string | null;
    high_school: string | null;
    years_exp: number | null;

    // Team and depth chart info
    team: string | null;
    team_abbr: string | null;
    team_changed_at: string | null;
    position: string;
    fantasy_positions: string[];
    number: number | null;
    depth_chart_order: number | null;
    depth_chart_position: string | null;
    practice_participation: string | null;
    practice_description: string | null;

    // Injury information
    injury_status: string | null;
    injury_body_part: string | null;
    injury_notes: string | null;
    injury_start_date: string | null;

    // External IDs
    espn_id: number | null;
    yahoo_id: number | null;
    stats_id: number | null;
    sportradar_id: string | null;
    rotowire_id: number | null;
    fantasy_data_id: number | null;
    gsis_id: string | null;
    rotoworld_id: string | null;

    // Additional metadata
    metadata: {
        [key: string]: any;
    };
    competitions: any[];
    news_updated: string | null;
}