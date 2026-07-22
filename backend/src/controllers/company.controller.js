const companyService = require('../services/company.service');

const getCompany = async (req, res) => {
    try {
        const data = await companyService.getCompanyInfo();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getLeadership = async (req, res) => {
    try {
        const data = await companyService.getLeadershipInfo();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getHistory = async (req, res) => {
    try {
        const data = await companyService.getCompanyHistory();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getIncome = async (req, res) => {
    try {
        const data = await companyService.getIncomeTimeline();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getCollaborations = async (req, res) => {
    try {
        const data = await companyService.getCollaborations();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = {
    getCompany,
    getLeadership,
    getHistory,
    getIncome,
    getCollaborations
};
