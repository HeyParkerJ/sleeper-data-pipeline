import { SleeperApiClient, SleeperApiError } from "./sleeper/sleeper_wrapper";
import { upsertPlayers } from "./sleeper/upsert_sleeper_players";

const handler = async () => {
  const client = new SleeperApiClient({
    timeout: 3000,
    retries: 2
  });
  
  try {
    const players = await client.mockGetPlayers();

    try{
      await upsertPlayers(players)
    } catch(err) {
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