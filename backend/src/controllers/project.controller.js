const projectService = require('../services/project.service');

const getCurrentProjects = async (req, res) => {
    try {
        const data = await projectService.getCurrentProjects();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

const getPastProjects = async (req, res) => {
    try {
        const data = await projectService.getPastProjects();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = {
    getCurrentProjects,
    getPastProjects
};
