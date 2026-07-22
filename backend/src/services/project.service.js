const pool = require('../config/database');

const getCurrentProjects = async () => {
    const [rows] = await pool.query('SELECT * FROM projects_current');
    return rows;
};

const getPastProjects = async () => {
    const [rows] = await pool.query('SELECT * FROM projects_past');
    return rows;
};

module.exports = {
    getCurrentProjects,
    getPastProjects
};
