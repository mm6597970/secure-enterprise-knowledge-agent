const healthService = require('../services/health.service');

const getHealth = (req, res) => {
    const status = healthService.checkHealth();
    res.json(status);
};

module.exports = {
    getHealth
};
