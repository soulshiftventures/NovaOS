const { createClient } = require('redis');  
const { Dropbox } = require('dropbox');  
const fetch = require('node-fetch');  

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

async function getAccessToken() {  
  const response = await fetch('https://api.dropboxapi.com/oauth2/token', {  
    method: 'POST',  
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },  
    body: new URLSearchParams({  
      grant_type: 'refresh_token',  
      refresh_token: process.env.DROPBOX_REFRESH_TOKEN,  
      client_id: '2vnitoo7fjno7po',  
      client_secret: '19wqn9zueedyxhm'  
    })  
  });  
  const data = await response.json();  
  if (data.error) throw new Error(data.error_description);  
  return data.access_token;  
}  

async function logToDropbox() {  
  await connectRedis();  
  try {  
    const accessToken = await getAccessToken();  
    const dbx = new Dropbox({ accessToken, fetch });  
    const logMessage = `Log at ${new Date().toISOString()}\n`;  
    await dbx.filesUpload({  
      path: `/novaos_logs/log_${Date.now()}.txt`,  
      contents: logMessage,  
      mode: 'add'  
    });  
    await redis.publish('novaos:commands', 'DropboxLogAgent: Logged to Dropbox');  
    console.log('Logged to Dropbox');  
  } catch (error) {  
    console.error('Error:', error);  
  }  
}  

setInterval(logToDropbox, 3600000); // Hourly  

logToDropbox(); // Initial  
