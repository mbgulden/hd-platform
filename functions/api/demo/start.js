export async function onRequest(context) {
  const target = 'https://api.humandesignengine.com/api/demo/start';
  const request = context.request;
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders() });
  }
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'content-type': 'application/json', ...corsHeaders() },
    });
  }
  const upstream = await fetch(target, {
    method: 'POST',
    headers: { 'content-type': request.headers.get('content-type') || 'application/json' },
    body: await request.text(),
  });
  return proxyResponse(upstream);
}

function corsHeaders() {
  return {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'Content-Type, Stripe-Signature',
  };
}

async function proxyResponse(upstream) {
  const headers = new Headers(upstream.headers);
  for (const [key, value] of Object.entries(corsHeaders())) headers.set(key, value);
  return new Response(await upstream.arrayBuffer(), { status: upstream.status, headers });
}
