const express = require('express');
const cors = require('cors');
const Redis = require('ioredis');

const app = express();
app.use(cors());
app.use(express.json());

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const MEM_KEY = 'chat_memory';

app.get('/memory', async (req, res) => {
  const mem = await redis.lrange(MEM_KEY, 0, -1);
  res.json({ memory: mem });
});

app.post('/memory', async (req, res) => {
  const { message } = req.body;
  if (message) await redis.rpush(MEM_KEY, message);
  res.json({ status: 'ok' });
});

app.listen(6000, '127.0.0.1', () => console.log('Memory API listening on port 6000'));
