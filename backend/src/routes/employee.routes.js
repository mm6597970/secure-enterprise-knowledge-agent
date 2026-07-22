const express = require('express');
const router = express.Router();
const employeeController = require('../controllers/employee.controller');

/**
 * @swagger
 * /employees:
 *   get:
 *     summary: Get all employees
 *     tags: [Employee]
 *     responses:
 *       200:
 *         description: List of employees
 */
router.get('/employees', employeeController.getEmployees);

/**
 * @swagger
 * /employees/{id}:
 *   get:
 *     summary: Get employee by ID
 *     tags: [Employee]
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Employee details
 *       404:
 *         description: Employee not found
 */
router.get('/employees/:id', employeeController.getEmployeeById);

/**
 * @swagger
 * /leave-policy:
 *   get:
 *     summary: Get leave policy
 *     tags: [Employee]
 *     responses:
 *       200:
 *         description: Leave policy details
 */
router.get('/leave-policy', employeeController.getLeavePolicy);

module.exports = router;
