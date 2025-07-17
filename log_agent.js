const { createClient } = require('redis');  
const fs = require('fs');  
const path = require('path');  

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

async function logActivity() {  
  await connectRedis();  
  try {  
    const logDir = path.join(__dirname, 'logs');  
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir);  
    const logFile = path.join(logDir, `log_${new Date().toISOString().split('T')[0]}.txt`);  
    const logMessage = `LogAgent: Activity at ${new Date().toISOString()}\n`;  
    fs.appendFileSync(logFile, logMessage);  
    await redis.publish('novaos:commands', `LogAgent: Logged activity to ${logFile}`);  
    console.log('Activity logged');  
  } catch (error) {  
    console.error('Error:', error);  
  }  
}  

setInterval(logActivity, 3600000); // Hourly log  

logActivity(); // Initial  
