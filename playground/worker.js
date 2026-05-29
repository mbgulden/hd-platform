// Cloudflare Worker: AI Interpretation for Human Design Engine Playground
// Uses Workers AI (free tier, 10K req/day) with round-robin fallback
// Deploy: npx wrangler deploy

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check
    if (url.pathname === '/api/ping') {
      return new Response(JSON.stringify({ status: 'ok', provider: 'cloudflare-workers-ai' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // AI Interpretation endpoint
    if (url.pathname === '/api/interpret' && request.method === 'POST') {
      try {
        const chartData = await request.json();
        const interpretation = await interpretChart(chartData, env);
        return new Response(JSON.stringify(interpretation), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (e) {
        return new Response(JSON.stringify({ error: e.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }
    }

    return new Response('Human Design Engine — AI Interpretation Worker', {
      headers: { ...corsHeaders, 'Content-Type': 'text/plain' }
    });
  }
};

async function interpretChart(chart, env) {
  // Build the prompt from chart data
  const prompt = buildPrompt(chart);

  // Round-robin: Workers AI → Gemini Flash → Template fallback
  let result;

  // Tier 1: Cloudflare Workers AI (free, 10K/day)
  try {
    result = await tryWorkersAI(prompt, env);
    if (result) return { interpretation: result, provider: 'cloudflare-workers-ai' };
  } catch (e) {
    console.log('Workers AI failed, trying Gemini...', e.message);
  }

  // Tier 2: Gemini Flash (if API key configured)
  if (env.GEMINI_API_KEY) {
    try {
      result = await tryGemini(prompt, env.GEMINI_API_KEY);
      if (result) return { interpretation: result, provider: 'gemini-flash' };
    } catch (e) {
      console.log('Gemini failed, using template...', e.message);
    }
  }

  // Tier 3: Template-based fallback
  return {
    interpretation: templateInterpretation(chart),
    provider: 'template-fallback'
  };
}

function buildPrompt(chart) {
  return `You are a warm, insightful Human Design interpreter. Analyze this chart data and give a plain-English interpretation. NO esoteric jargon — translate everything into everyday language. Be specific, practical, and kind. Keep it under 300 words.

Chart Data:
- Type: ${chart.hd_type || 'Unknown'}
- Profile: ${chart.profile || 'Unknown'}
- Authority (decision-making style): ${chart.authority || 'Unknown'}
- Strategy: ${chart.strategy || 'Unknown'}
- Definition: ${chart.definition || 'Unknown'}
- Incarnation Cross (life theme): ${chart.incarnation_cross?.name || 'Unknown'}
- Defined Centers: ${(chart.defined_centers || []).join(', ')}
- Undefined Centers: ${(chart.undefined_centers || []).join(', ')}
- Channels: ${(chart.defined_channels || []).join(', ')}
- Signature (feeling when aligned): ${chart.signature || 'Unknown'}
- Not-Self Theme (warning signal): ${chart.not_self_theme || 'Unknown'}

Please provide:
1. A one-sentence summary of who this person is at their core
2. How they're designed to make decisions (in plain English)
3. Their natural gifts (2-3 sentences)
4. Where they're most open to influence from others
5. One practical tip for living more aligned today`;
}

async function tryWorkersAI(prompt, env) {
  const model = '@cf/meta/llama-3-8b-instruct';

  const response = await env.AI.run(model, {
    messages: [
      { role: 'system', content: 'You are a warm, knowledgeable Human Design interpreter. Use plain English, no jargon. Be concise but insightful.' },
      { role: 'user', content: prompt }
    ],
    max_tokens: 500,
    temperature: 0.7,
  });

  return response?.response || null;
}

async function tryGemini(prompt, apiKey) {
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { maxOutputTokens: 500, temperature: 0.7 }
      })
    }
  );

  const data = await response.json();
  return data?.candidates?.[0]?.content?.parts?.[0]?.text || null;
}

function templateInterpretation(chart) {
  const type = chart.hd_type || 'unique individual';
  const authority = chart.authority || 'inner wisdom';
  const centers = (chart.defined_centers || []).length;
  const channels = (chart.defined_channels || []).length;
  const profile = chart.profile || '';
  const cross = chart.incarnation_cross?.name || '';

  return `You are a ${type} with a ${profile} profile — one of the world's natural guides and systems-thinkers. Your life theme, the ${cross}, points toward a journey of ${cross.toLowerCase().includes('rulership') ? 'leadership and direction' : cross.toLowerCase().includes('planning') ? 'community-building and foresight' : 'deep personal transformation'}.

With ${centers} defined centers and ${channels} channels, you carry consistent energy in specific areas of life — these are your reliable gifts. The undefined centers in your chart are where you're most sensitive to the world around you, picking up wisdom and conditioning from others.

Your ${authority} is your internal compass. When you make decisions through this, you'll feel ${chart.signature || 'aligned'}. When you override it, you'll feel ${chart.not_self_theme || 'off-track'}. 

**Today's experiment:** Notice one decision — even a small one — and wait for your ${authority} to give you clarity before acting. See what shifts.`;
}
