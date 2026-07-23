const jwt = require('jsonwebtoken');
const pool = require('../config/database');

const login = async (req, res) => {
    try {
        const { email, password } = req.body;
        const [users] = await pool.query(`
            SELECT u.*, r.role_name, e.full_name 
            FROM users u 
            LEFT JOIN user_roles ur ON u.user_id = ur.user_id 
            LEFT JOIN roles r ON ur.role_id = r.role_id 
            LEFT JOIN employees e ON u.emp_id = e.emp_id 
            WHERE u.email = ?
        `, [email]);
        
        if (users.length === 0) {
            return res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
        
        const user = users[0];
        
        // Mock password check for demo purposes
        let passwordMatch = false;
        if (user.password_hash.startsWith('hashed_pwd_') && password === 'password') {
            passwordMatch = true;
        }
        
        // Allow login if user explicitly pastes the db hash as the password
        if (password === user.password_hash) {
            passwordMatch = true;
        }

        if (!passwordMatch) {
            return res.status(401).json({ success: false, message: 'Invalid credentials' });
        }

        const token = jwt.sign(
            { userId: user.user_id }, 
            process.env.JWT_SECRET || 'supersecret', 
            { expiresIn: '1h' }
        );
        
        res.json({ 
            success: true, 
            token, 
            user: {
                id: user.user_id,
                email: user.email,
                name: user.full_name,
                role: user.role_name
            }
        });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
};

module.exports = { login };
