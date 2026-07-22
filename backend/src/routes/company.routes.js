const express = require('express');
const router = express.Router();
const companyController = require('../controllers/company.controller');

/**
 * @swagger
 * /company:
 *   get:
 *     summary: Get company information
 *     tags: [Company]
 *     responses:
 *       200:
 *         description: Company information
 */
router.get('/company', companyController.getCompany);

/**
 * @swagger
 * /leadership:
 *   get:
 *     summary: Get company leadership
 *     tags: [Company]
 *     responses:
 *       200:
 *         description: Leadership information
 */
router.get('/leadership', companyController.getLeadership);

/**
 * @swagger
 * /history:
 *   get:
 *     summary: Get company history
 *     tags: [Company]
 *     responses:
 *       200:
 *         description: History information
 */
router.get('/history', companyController.getHistory);

/**
 * @swagger
 * /income:
 *   get:
 *     summary: Get income timeline
 *     tags: [Company]
 *     responses:
 *       200:
 *         description: Income information
 */
router.get('/income', companyController.getIncome);

/**
 * @swagger
 * /collaborations:
 *   get:
 *     summary: Get company collaborations
 *     tags: [Company]
 *     responses:
 *       200:
 *         description: Collaborations information
 */
router.get('/collaborations', companyController.getCollaborations);

module.exports = router;
