const { createClient } = require('redis');  
const axios = require('axios');  

const redis = createClient({  
  url: process.env.UPSTASH_REDIS_REST_URL,  
  token: process.env.UPSTASH_REDIS_REST_TOKEN,  
});  

redis.on('error', (err) => console.error('Redis Error', err));  

async function connectRedis() {  
  if (!redis.isOpen) await redis.connect();  
}  

async function fetchTrend() {  
  await connectRedis();  
  try {  
    const response = await axios.get(`${process.env.UPSTASH_REDIS_REST_URL}/incr/novaos:streams:active?_token=${process.env.UPSTASH_REDIS_REST_TOKEN}`);  
    await redis.publish('novaos:commands', `TrendFetcher: Stream incremented to ${response.data.result}`);  
    console.log('Trend fetched, stream incremented');  
  } catch (error) {  
    console.error('Error:', error);  
  }  
}  

setInterval(fetchTrend, 7200000); // Every 2 hours for trend updates  

fetchTrend(); // Initial run  
