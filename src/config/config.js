module.exports = {
    port: process.env.PORT || 3000,
    db: {
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 27017,
        name: process.env.DB_NAME || 'mydatabase'
    },
    jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret',
    apiUrl: process.env.API_URL || 'http://localhost:3000/api'
};