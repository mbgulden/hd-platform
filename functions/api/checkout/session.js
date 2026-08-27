export async function onRequest(context) {
  const target = 'https://api.humandesignengine.com/api/checkout/session' + new URL(context.request.url).search;
  const upstream = await fetch(target, { method: 'GET' });
  const headers = new Headers(upstream.headers);
  headers.set('access-control-allow-origin', '*');
  return new Response(await upstream.arrayBuffer(), { status: upstream.status, headers });
}
