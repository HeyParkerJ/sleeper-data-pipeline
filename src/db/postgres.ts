import { Client } from 'pg';

export async function createPgClient(port: number) {
    const pgClient = new Client({
        host: 'localhost',
        port: port, // Port that the SSH tunnel is listening on
        database: process.env.DB_NAME,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD
      });

    await pgClient.connect();
    return pgClient;
}