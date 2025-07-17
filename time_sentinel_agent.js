const { createClient } = require('redis');  
const axios = require('axios');  

const restUrl = process.env.UPSTASH_REDIS_REST_URL;  
const token = process.env.UPSTASH_REDIS_REST_TOKEN;  
const host = restUrl.replace('https://', '');  
const redisUrl = `rediss://default:${token}@${host}:6379`;  

const redis = createClient({  
  url: redisUrl,  
  socket: {  
    reconnectStrategy: (retries) => Math.min(retries * 100, 3000)  
  }  
});  

redis.on('error', (err) => console.error('Redis Error', err));  

async function connectRedis() {  
  if (!redis.isOpen) await redis.connect();  
}  

async function sentinelCheck() {  
  await connectRedis();  
  try {  
    const current = new Date();  
    const deadline = new Date('2025-08-04');  
    const daysLeft = Math.ceil((deadline - current) / (86400000));  
    if (daysLeft < 20) {  
      await redis.publish('novaos:commands', `TimeSentinel: ${daysLeft} days to $25k/mo goal - Accelerate streams!`);  
    }  
    console.log(`Sentinel check: ${daysLeft} days left`);  
  } catch (error) {  
    console.error('Error:', error);  
  }  
}  

setInterval(sentinelCheck, 86400000); // Daily check  

sentinelCheck(); // Initial run  
