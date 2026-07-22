const pool = require('../config/database');

const employeeQuery = `
    SELECT 
        e.emp_id AS "ID",
        e.full_name AS "Employee", 
        e.department AS "Department", 
        s.role_name AS "Role", 
        e.salary_lpa AS "Salary", 
        m.full_name AS "Manager"
    FROM employees e
    LEFT JOIN salary_structure s ON e.role_id = s.role_id
    LEFT JOIN employees m ON e.manager_id = m.emp_id
`;

const getAllEmployees = async () => {
    const [rows] = await pool.query(employeeQuery);
    return rows;
};

const getEmployeeById = async (id) => {
    const [rows] = await pool.query(`${employeeQuery} WHERE e.emp_id = ?`, [id]);
    return rows[0];
};

const getLeavePolicy = async () => {
    const [rows] = await pool.query('SELECT leave_type AS "Leave Types", days_allowed AS "Days", notes AS "Notes" FROM leave_policy');
    return rows;
};

module.exports = {
    getAllEmployees,
    getEmployeeById,
    getLeavePolicy
};
