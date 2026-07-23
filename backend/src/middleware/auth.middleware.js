const jwt = require('jsonwebtoken');
const pool = require('../config/database');

const verifyToken = async (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ success: false, message: 'Unauthorized: No token provided' });
    }
    
    const token = authHeader.split(' ')[1];
    
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'supersecret');
        
        // Fetch role from DB
        const [rows] = await pool.query(
            `SELECT u.user_id, u.email, r.role_name 
             FROM users u 
             JOIN user_roles ur ON u.user_id = ur.user_id 
             JOIN roles r ON ur.role_id = r.role_id 
             WHERE u.user_id = ?`, 
            [decoded.userId]
        );
        
        if (rows.length === 0) {
            return res.status(401).json({ success: false, message: 'Unauthorized: User not found' });
        }
        
        req.user = {
            userId: rows[0].user_id,
            email: rows[0].email,
            role: rows[0].role_name,
            department: 'Engineering' // Mock department for demo
        };
        next();
    } catch (err) {
        return res.status(401).json({ success: false, message: 'Unauthorized: Invalid token' });
    }
};

module.exports = { verifyToken };
