const { createClient } = require('redis');  
const axios = require('axios');  

const restUrl = process.env.UPSTASH_REDIS_REST_URL;  
const token = process.env.UPSTASH_REDIS_REST_TOKEN;  
const host = restUrl.replace('https://', '');  
const redisUrl = `rediss://default:${token}@${host}:6379`;  

const redis = createClient({  
  url: redisUrl,  
  socket: {  
    reconnectStrategy: (retries) => Math.min(retries * 100, 3000) // Reconnect with backoff  
  }  
});  

redis.on('error', (err) => console.error('Redis Error', err));  

async function connectRedis() {  
  if (!redis.isOpen) await redis.connect();  
}  

async function fetchTrend() {  
  await connectRedis();  
  try {  
    const response = await axios.get(`${restUrl}/incr/novaos:streams:active?_token=${token}`);  
    await redis.publish('novaos:commands', `TrendFetcher: Stream incremented to ${response.data.result}`);  
    console.log('Trend fetched, stream incremented');  
  } catch (error) {  
    console.error('Error:', error);  
  }  
}  

setInterval(fetchTrend, 7200000); // Every 2 hours  

fetchTrend(); // Initial run  
