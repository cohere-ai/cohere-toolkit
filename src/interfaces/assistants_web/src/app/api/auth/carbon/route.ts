import { env } from '@/env.mjs';

export async function GET(request: Request): Promise<Response> {
  const res = await fetch('https://api.carbon.ai/auth/v1/access_token', {
    headers: {
      Authorization: 'Bearer ' + env.CABRON_AI_API_KEY,
      'customer-id': request.headers.get('customer-id') ?? '',
    },
  });
  const data = await res.json();

  return Response.json(data);
}
