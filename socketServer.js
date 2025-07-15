const { createServer } = require('http');
const { Server } = require('socket.io');
const Redis = require('ioredis');

const redis = new Redis(process.env.REDIS_URL);
const httpServer = createServer();
const io = new Server(httpServer, { cors: { origin: '*' } });

redis.subscribe('novaos:queue', () => {});
redis.on('message', (_, msg) => {
  io.emit('message', JSON.parse(msg));
});

httpServer.listen(4000, () => console.log('Socket server on 4000'));
