const redis = require('redis');

// Create a client instance (default connects to localhost:6379)
const redisClient = redis.createClient();
redisClient.on('error', function(error) {
  console.error(error);
});

// Connect to Redis
redisClient.connect();


module.exports = redisClient