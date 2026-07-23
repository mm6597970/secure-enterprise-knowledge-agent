const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000';

const askQuestion = async (question, user) => {
    try {
        const response = await axios.post(`${AI_SERVICE_URL}/chat`, { question, user });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'AI service unavailable.');
    }
};

const uploadDocument = async (filePath, originalName) => {
    try {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath), originalName);

        const response = await axios.post(`${AI_SERVICE_URL}/documents/upload`, formData, {
            headers: {
                ...formData.getHeaders(),
            },
        });
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'AI service unavailable.');
    }
};

const processDocuments = async () => {
    try {
        const response = await axios.post(`${AI_SERVICE_URL}/documents/process`);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'AI service unavailable.');
    }
};

module.exports = {
    askQuestion,
    uploadDocument,
    processDocuments
};
