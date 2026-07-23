const fs = require('fs');
const mysql = require('mysql2/promise');
const path = require('path');
require('dotenv').config();

async function migrate() {
    try {
        const pool = mysql.createPool({
            host: process.env.DB_HOST || '127.0.0.1',
            port: process.env.DB_PORT || 3306,
            user: process.env.DB_USER || 'root',
            password: process.env.DB_PASSWORD || 'rootpassword',
            database: process.env.DB_NAME || 'nexora_systems',
            multipleStatements: true
        });

        const sqlFilePath = require('path').join(__dirname, '..', 'db_data.txt');
        const sql = require('fs').readFileSync(sqlFilePath, 'utf8');
        
        console.log('Applying db_data.txt to MySQL database...');
        
        try {
            await pool.query(sql);
        } catch (err) {
            console.error('Error executing query:', err.message);
        }
        
        console.log('Database updated successfully with Step 4 tables!');
        process.exit(0);
    } catch (err) {
        console.error('Error updating database:', err);
        process.exit(1);
    }
}

migrate();
