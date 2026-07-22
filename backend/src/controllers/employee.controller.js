const employeeService = require('../services/employee.service');

const getEmployees = async (req, res) => {
    try {
        const data = await employeeService.getAllEmployees();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getEmployeeById = async (req, res) => {
    try {
        const id = req.params.id;
        const data = await employeeService.getEmployeeById(id);
        if (!data) {
            return res.status(404).json({ message: 'Employee not found' });
        }
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getLeavePolicy = async (req, res) => {
    try {
        const data = await employeeService.getLeavePolicy();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = {
    getEmployees,
    getEmployeeById,
    getLeavePolicy
};
