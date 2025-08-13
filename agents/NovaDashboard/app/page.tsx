import { Redis } from '@upstash/redis';  
import NextDynamic from 'next/dynamic';  

export const dynamic = 'force-dynamic';  

const redis = Redis.fromEnv();  

const MetricsChart = NextDynamic(() => import('./components/MetricsChart'));  

export default async function Home() {  
  let streams = 1;  
  let revenue = 25000;  
  let users = 100;  
  try {  
    streams = (await redis.get<number>('novaos:streams:active')) || 1;  
    revenue = (await redis.get<number>('revenue')) || 25000;  
    users = (await redis.get<number>('users')) || 100;  
  } catch (error) {  
    console.error('Redis error:', error);  
  }  

  const chartData = [  
    { name: 'Streams', value: streams },  
    { name: 'Revenue', value: revenue },  
    { name: 'Users', value: users },  
  ];  

  return (  
    <main className="p-8">  
      <h1 className="text-2xl font-bold mb-4">NovaOS Dashboard</h1>  
      <div className="grid grid-cols-3 gap-4 mb-8">  
        <div className="p-4 border rounded">  
          <h2>Active Streams</h2>  
          <p className="text-4xl">{streams}</p>  
        </div>  
        <div className="p-4 border rounded">  
          <h2>Revenue ($)</h2>  
          <p className="text-4xl">{revenue}</p>  
        </div>  
        <div className="p-4 border rounded">  
          <h2>Users</h2>  
          <p className="text-4xl">{users}</p>  
        </div>  
      </div>  
      <h2 className="text-xl font-bold mb-4">Metrics Overview</h2>  
      <MetricsChart chartData={chartData} />  
    </main>  
  );  
}  
