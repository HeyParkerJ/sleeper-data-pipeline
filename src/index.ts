import { SleeperApiClient, SleeperApiError } from "./sleeper/sleeper_wrapper";
import { upsertPlayers, closePool } from "./sleeper/upsert_sleeper_players";
import { tunnelServerPort, connect } from './db/bastion'
import { getPrivateKey } from "./utils/getPrivateKey";
import { createPgClient } from "./db/postgres";

const handler = async () => {
  const sleeperClient = new SleeperApiClient({
    timeout: 3000,
    retries: 2
  });

  try {
    const tunnelServer = await connect();

    // Now that the tunnel is configured, 
    // try to connect to psql like it's local
    const pgC = await createPgClient(tunnelServerPort);

    // const players = await sleeperClient.mockGetPlayers();

    try {
      console.log('Upserting players!')

      // await upsertPlayers(dbConnection, players)
      console.log('Done upserting players! Closing pool.')

      await closePool()
      console.log('Pool is closed')
    } catch (err) {
      console.error(err)
    }
  } catch (error) {
    if (error instanceof SleeperApiError) {
      console.error('API Error:', error.message, error.statusCode);
    } else {
      console.error('Unexpected error:', error);
    }
  }

}

handler();