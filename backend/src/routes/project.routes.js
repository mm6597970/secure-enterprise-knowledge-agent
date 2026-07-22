const express = require('express');
const router = express.Router();
const projectController = require('../controllers/project.controller');

/**
 * @swagger
 * /projects/current:
 *   get:
 *     summary: Get current projects
 *     tags: [Projects]
 *     responses:
 *       200:
 *         description: List of current projects
 */
router.get('/current', projectController.getCurrentProjects);

/**
 * @swagger
 * /projects/past:
 *   get:
 *     summary: Get past projects
 *     tags: [Projects]
 *     responses:
 *       200:
 *         description: List of past projects
 */
router.get('/past', projectController.getPastProjects);

module.exports = router;
