const aiClient = require('../clients/ai.client');
const fs = require('fs');

const chat = async (req, res) => {
    try {
        const { question } = req.body;
        if (!question) {
            return res.status(400).json({ success: false, message: 'Question is required' });
        }
        
        // Forward question to FastAPI
        const data = await aiClient.askQuestion(question);
        
        // Return exactly what the AI returned, wrapped in our standard response
        res.json({ success: true, answer: data.answer });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
};

const uploadAndProcess = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'No file uploaded' });
        }
        
        // Upload to AI service
        await aiClient.uploadDocument(req.file.path, req.file.originalname);
        
        // Tell AI service to process it
        const processResult = await aiClient.processDocuments();
        
        // Delete local temporary file
        fs.unlinkSync(req.file.path);
        
        res.json({ success: true, data: processResult });
    } catch (error) {
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }
        res.status(500).json({ success: false, message: error.message });
    }
};

module.exports = {
    chat,
    uploadAndProcess
};
