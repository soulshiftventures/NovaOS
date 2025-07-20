'use client';  

import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';  

export default function MetricsChart({ chartData }: { chartData: any[] }) {  
  return (  
    <BarChart width={600} height={300} data={chartData}>  
      <XAxis dataKey="name" />  
      <YAxis domain={[0, 26000]} ticks={[0, 6500, 13000, 19500, 26000]} />  
      <Tooltip />  
      <Bar dataKey="value" fill="#8884d8" />  
    </BarChart>  
  );  
}  
