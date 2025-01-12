export interface Migration {
    id: number;
    name: string;
    up: string;   // Location of .sql file
    down?: string; // SQL to reverse the migration
}