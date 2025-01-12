import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

// This is just some example code on creating a PG connection
async function main() {
    // Connection configuration
    const pool = new Pool({
        user: process.env.DB_USER,
        host: process.env.DB_HOST,
        database: process.env.DB_NAME,
        password: process.env.DB_PASSWORD,
        port: parseInt(process.env.DB_PORT || '5432'),
        ssl: {
            rejectUnauthorized: false // Required for RDS SSL connections
        }
    });

    try {
        // Test the connection
        console.log('Testing connection...');
        await pool.query('SELECT NOW()');
        console.log('Connection successful!');

        // Create a test table
        console.log('Creating test table...');
        await pool.query(`
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('Test table created successfully!');

        // Insert a test row
        console.log('Inserting test data...');
        const result = await pool.query(
            'INSERT INTO test_table (name) VALUES ($1) RETURNING *',
            ['Test Entry']
        );
        console.log('Inserted row:', result.rows[0]);

    } catch (error) {
        console.error('Error:', error);
    } finally {
        // Close the pool
        await pool.end();
    }
}

main();