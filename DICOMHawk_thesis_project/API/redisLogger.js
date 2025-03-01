const redis = require('redis');
host="localhost"
if (process.env.Docker_ENV=="True"){
host="172.29.0.4"
}
// Create a client instance (default connects to localhost:6379)
var redisClient = redis.createClient({
    socket: {
      host: host, // Replace with your Redis server's IP address
      port: 6379  // Default Redis port; change if different
    }
  });



redisClient.on('error', function(error) {
  console.error(error);
});

// Connect to Redis
redisClient.connect();


module.exports = redisClient    