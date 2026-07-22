const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const swaggerUi = require('swagger-ui-express');
const swaggerSpec = require('./config/swagger');

const healthRoutes = require('./routes/health.routes');
const companyRoutes = require('./routes/company.routes');
const employeeRoutes = require('./routes/employee.routes');
const projectRoutes = require('./routes/project.routes');

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use('/health', healthRoutes);
app.use('/', companyRoutes); 
app.use('/', employeeRoutes);
app.use('/projects', projectRoutes);

module.exports = app;
