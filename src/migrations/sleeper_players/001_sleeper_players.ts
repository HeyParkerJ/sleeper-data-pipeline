import { Migration } from '../Migration';

// This is some minor infrastrucutre that I'll leverage later to automate this in a lambda
export const migration: Migration = {
    id: 1,
    name: "create_sleeper_players_table",
    up: "001_sleeper_players.sql",
}