import { Pool } from 'pg';
import { DBSleeperPlayer, SleeperPlayer } from '../types/SleeperPlayer';

// Create a connection pool
// const pool = new Pool({
//     user: process.env.DB_USER,
//     host: process.env.DB_HOST,
//     database: process.env.DB_NAME,
//     password: process.env.DB_PASSWORD,
//     port: parseInt(process.env.DB_PORT || '5432'),
//     ssl: {
//         rejectUnauthorized: false // Required for RDS SSL connections
//     }
// });

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
 * Creates the SQL for upserting a player with all fields
 */
const createUpsertQuery = (player: DBSleeperPlayer) => {
    const columns = Object.keys(player);
    const values = Object.values(player);
    
    const insertPart = `INSERT INTO sleeper_players (${columns.join(', ')})`;
    const valuePart = `VALUES (${values.map((_, i) => `$${i + 1}`).join(', ')})`;
    const updatePart = `ON CONFLICT (player_id) DO UPDATE SET ${
        columns.map(col => `${col} = EXCLUDED.${col}`).join(', ')
    }`;
    
    return {
        text: `${insertPart} ${valuePart} ${updatePart} RETURNING *`,
        values: values.map(val => 
            Array.isArray(val) ? JSON.stringify(val) : // Handle arrays (fantasy_positions)
            typeof val === 'object' ? JSON.stringify(val) : // Handle JSON objects (metadata)
            val
        )
    };
};

/**
 * Upserts a single Sleeper player into the database
 */
export const upsertPlayer = async (playerId: string, playerData: SleeperPlayer) => {
    const client = await pool.connect();
    try {
        const transformedPlayer = transformPlayerData(playerId, playerData);
        const query = createUpsertQuery(transformedPlayer);
        const result = await client.query(query);
        return result.rows[0];
    } catch (error) {
        console.error('Error upserting player:', playerId, error);
        throw error;
    } finally {
        client.release();
    }
};

/**
 * Upserts multiple Sleeper players into the database
 */
export const upsertPlayers = async (DatabaseConnection, players: Record<string, SleeperPlayer>) => {
    const client = await DatabaseConnection.pool.connect();
    console.log('Pool is connected')
    try {
        await client.query('BEGIN');

        const transformedPlayers = Object.entries(players).map(([id, player]) => 
            transformPlayerData(id, player)
        );

        const BATCH_SIZE = 1000;
        const results: any[] = [];

        // Process in batches
        for (let i = 0; i < transformedPlayers.length; i += BATCH_SIZE) {
            const batch = transformedPlayers.slice(i, i + BATCH_SIZE);
            const batchResults = await Promise.all(
                batch.map(player => {
                    const query = createUpsertQuery(player);
                    return client.query(query);
                })
            );
            results.push(...batchResults.map(r => r.rows[0]));
        }

        await client.query('COMMIT');
        return results;
    } catch (error) {
        await client.query('ROLLBACK');
        console.error('Error upserting players:', error);
        throw error;
    } finally {
        client.release();
    }
};

// Cleanup function to be called when shutting down
export const closePool = async () => {
    await pool.end();
};