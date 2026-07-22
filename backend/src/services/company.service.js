const pool = require('../config/database');

const getCompanyInfo = async () => {
    const [rows] = await pool.query('SELECT legal_name AS "Company Name", ceo_name AS "CEO", founded_year AS "Founded Year", industry AS "Industry", headquarters AS "Headquarters" FROM company_info LIMIT 1');
    return rows[0] || {};
};

const getLeadershipInfo = async () => {
    const [rows] = await pool.query('SELECT name, designation, joined_year FROM leadership');
    return rows;
};

const getCompanyHistory = async () => {
    const [rows] = await pool.query('SELECT event_year, milestone FROM company_history ORDER BY event_year ASC');
    return rows;
};

const getIncomeTimeline = async () => {
    const [rows] = await pool.query('SELECT financial_year, revenue_cr AS "Revenue", net_profit_margin_pct AS "Profit", employee_count AS "Employee Count" FROM income_timeline ORDER BY fy_id ASC');
    return rows;
};

const getCollaborations = async () => {
    const [rows] = await pool.query('SELECT partner_name AS "Partners", since_year AS "Since Year", collab_type AS "Type" FROM collaborations');
    return rows;
};

module.exports = {
    getCompanyInfo,
    getLeadershipInfo,
    getCompanyHistory,
    getIncomeTimeline,
    getCollaborations
};
