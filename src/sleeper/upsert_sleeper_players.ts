import { createClient } from '@supabase/supabase-js';
import { DBSleeperPlayer, SleeperPlayer } from '../types/SleeperPlayer';

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

/**
 * Transforms raw Sleeper player data into database format
 */
const transformPlayerData = (playerId: string, player: SleeperPlayer): DBSleeperPlayer => {
    return {
    player_id: playerId,
    sleeper_id: player.player_id,
    first_name: player.first_name,
    last_name: player.last_name,
    full_name: player.full_name,
    position: player.position,
    fantasy_positions: player.fantasy_positions,
    team: player.team,
    team_abbr: player.team_abbr,
    team_changed_at: player.team_changed_at,
    number: player.number,
    active: player.active,
    status: player.status,
    sport: player.sport,
    search_first_name: player.search_first_name,
    search_last_name: player.search_last_name,
    search_full_name: player.search_full_name,
    search_rank: player.search_rank,
    hashtag: player.hashtag,
    age: player.age,
    height: player.height,
    weight: player.weight,
    birth_date: player.birth_date,
    birth_city: player.birth_city,
    birth_state: player.birth_state,
    birth_country: player.birth_country,
    college: player.college,
    high_school: player.high_school,
    years_exp: player.years_exp,
    injury_status: player.injury_status,
    injury_body_part: player.injury_body_part,
    injury_notes: player.injury_notes,
    injury_start_date: player.injury_start_date,
    practice_participation: player.practice_participation,
    practice_description: player.practice_description,
    depth_chart_position: player.depth_chart_position,
    depth_chart_order: player.depth_chart_order,
    news_updated: player.news_updated,
    espn_id: player.espn_id,
    yahoo_id: player.yahoo_id,
    stats_id: player.stats_id,
    sportradar_id: player.sportradar_id,
    rotowire_id: player.rotowire_id,
    fantasy_data_id: player.fantasy_data_id,
    gsis_id: player.gsis_id,
    rotoworld_id: player.rotoworld_id,
    metadata: player.metadata,
  };
};

/**
 * Upserts a single Sleeper player into the database
 */
export const upsertPlayer = async (playerId: string, playerData: SleeperPlayer) => {
  try {
    const transformedPlayer = transformPlayerData(playerId, playerData);
    
    const { data, error } = await supabase
      .from('sleeper_players')
      .upsert(transformedPlayer, {
        onConflict: 'player_id',
      });

    if (error) {
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Error upserting player:', playerId, error);
    throw error;
  }
};

/**
 * Upserts multiple Sleeper players into the database
 */
export const upsertPlayers = async (players: Record<string, SleeperPlayer>) => {
  try {
    const transformedPlayers = Object.entries(players).map(([id, player]) => 
      transformPlayerData(id, player)
    );
    
    // Supabase has a limit on the number of rows that can be upserted at once
    // So we'll chunk the data into smaller batches
    const BATCH_SIZE = 1000;
    const batches: any[] = [];
    
    for (let i = 0; i < transformedPlayers.length; i += BATCH_SIZE) {
      batches.push(transformedPlayers.slice(i, i + BATCH_SIZE));
    }
    
    const results = await Promise.all(
      batches.map(async (batch) => {
        const { data, error } = await supabase
          .from('sleeper_players')
          .upsert(batch, {
            onConflict: 'player_id',
          });

        if (error) {
          throw error;
        }

        return data;
      })
    );

    return results.flat();
  } catch (error) {
    console.error('Error upserting players:', error);
    throw error;
  }
};