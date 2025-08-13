const express = require('express');
const cors = require('cors');
const Redis = require('ioredis');

const app = express();
app.use(cors());  // <-- Enable cross-origin requests

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const QUEUE = process.env.REDIS_QUEUE || 'novaos:queue';

app.get('/metrics', async (req, res) => {
  const queueDepth = await redis.llen(QUEUE);
  res.json({ queueDepth });
});

const PORT = process.env.METRICS_PORT || 5000;
app.listen(PORT, '127.0.0.1', function() {
  console.log('Metrics API listening on 127.0.0.1:' + PORT);
});
