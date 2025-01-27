const express = require('express');
const config = require('./config/config');

const app = express();
const PORT = config.port || 3000;

// Middleware and routes setup
app.use(express.json());

// Example route
app.get('/', (req, res) => {
    res.send('Hello, World!');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});