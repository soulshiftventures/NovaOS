import { NextResponse } from 'next/server';
import axios from 'axios';

export async function GET() {
  const redisUrl = 'https://square-gannet-57727.upstash.io';
  const redisToken = 'AeF_AAIjcDFkMjY5ODc3MzcwMDQ0OWJhYjAyN2YyYThkNTVjMTM1OXAxMA';
  try {
    const response = await axios.post(
      `${redisUrl}/get/novaos:streams:active`,
      {},
      { headers: { Authorization: `Bearer ${redisToken}` } }
    );
    const streamsActive = response.data.result || 1;
    const metrics = {
      streamsActive: Number(streamsActive),
      revenue: 25000,
      users: 100,
      lastUpdated: new Date().toISOString(),
    };
    return NextResponse.json(metrics);
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return NextResponse.json({ streamsActive: 1, revenue: 25000, users: 100, lastUpdated: new Date().toISOString() });
  }
}
