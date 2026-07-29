const aiClient = require('../clients/ai.client');
const fs = require('fs');

const chat = async (req, res) => {
    try {
        const { question, history } = req.body;
        if (!question) {
            return res.status(400).json({ success: false, message: 'Question is required' });
        }
        
        // Forward question, history, and user info to FastAPI
        const data = await aiClient.askQuestion(question, req.user, history || []);
        
        // Return AI response with Step 5 agent metadata
        res.json({ 
            success: true, 
            answer: data.answer,
            agent_chosen: data.agent_chosen,
            sql_query: data.sql_query,
            rag_docs: data.rag_docs,
            status: data.status
        });
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
