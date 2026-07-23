const express = require('express');
const multer = require('multer');
const aiController = require('../controllers/ai.controller');

const router = express.Router();
// Save uploaded files to a temporary uploads directory
const upload = multer({ dest: 'uploads/' });

// Forward /chat to AI service
router.post('/chat', aiController.chat);

// Forward /upload to AI service and trigger processing
router.post('/upload', upload.single('file'), aiController.uploadAndProcess);

module.exports = router;
