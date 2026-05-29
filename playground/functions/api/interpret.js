// Cloudflare Pages Function: AI Interpretation endpoint
// Lives at /api/interpret on the deployed Pages site
// Uses Workers AI binding (free tier, 10K req/day)

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      }
    });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'POST required' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }

  try {
    const chart = await request.json();
    const prompt = buildPrompt(chart);

    // Tier 1: Workers AI (free)
    try {
      const result = await env.AI.run('@cf/meta/llama-3-8b-instruct', {
        messages: [
          { role: 'system', content: 'You are a warm, knowledgeable Human Design interpreter. Use plain English. Be concise but insightful. Never use jargon like "Sacral," "Not-Self," or "Authority" without explaining it in everyday terms.' },
          { role: 'user', content: prompt }
        ],
        max_tokens: 500,
        temperature: 0.7,
      });
      
      if (result?.response) {
        return new Response(JSON.stringify({ 
          interpretation: result.response, 
          provider: 'cloudflare-workers-ai' 
        }), {
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }
    } catch (e) {
      console.log('Workers AI failed, trying fallback...', e.message);
    }

    // Tier 2: Gemini Flash fallback
    if (env.GEMINI_API_KEY) {
      try {
        const geminiResp = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${env.GEMINI_API_KEY}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              contents: [{ parts: [{ text: prompt }] }],
              generationConfig: { maxOutputTokens: 500, temperature: 0.7 }
            })
          }
        );
        const data = await geminiResp.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text) {
          return new Response(JSON.stringify({ interpretation: text, provider: 'gemini-flash' }), {
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
          });
        }
      } catch (e) {
        console.log('Gemini failed, using template...', e.message);
      }
    }

    // Tier 3: Template fallback
    return new Response(JSON.stringify({
      interpretation: templateInterpretation(chart),
      provider: 'template-fallback'
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });

  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}

function buildPrompt(chart) {
  return `Analyze this Human Design chart and give a plain-English interpretation. NO jargon. Be specific, practical, and kind. Under 300 words.

Chart Data:
- Type: ${chart.hd_type || chart.type || 'Unknown'}
- Profile: ${chart.profile || 'Unknown'}
- Decision-making style: ${chart.authority || 'Unknown'}
- Strategy: ${chart.strategy || 'Unknown'}
- Life theme: ${chart.incarnation_cross?.name || 'Unknown'}
- Defined centers: ${(chart.defined_centers || []).join(', ')}
- Open centers: ${(chart.undefined_centers || []).join(', ')}
- Channels: ${(chart.defined_channels || []).join(', ')}

Provide:
1. One-sentence core identity
2. How they make best decisions (plain English)
3. Their natural gifts (2-3 sentences)
4. Where they absorb others' energy
5. One practical experiment for today`;
}

function templateInterpretation(chart) {
  const type = chart.hd_type || chart.type || 'unique individual';
  const authority = chart.authority || 'inner wisdom';
  const centers = (chart.defined_centers || []).length;
  const channels = (chart.defined_channels || []).length;
  const cross = chart.incarnation_cross?.name || '';
  const profile = chart.profile || '';

  return `You are a ${type} with a ${profile} profile. With ${centers} defined centers and ${channels} channels, you carry consistent, reliable energy in specific areas — these are your natural gifts. The open centers in your chart are where you're most sensitive and perceptive, picking up wisdom from the world around you.

Your ${authority} is your internal compass. When you make decisions through this, you'll feel ${chart.signature || 'aligned and at peace'}. When you override it — rushing, letting others decide for you, or ignoring that quiet knowing — you'll feel ${chart.not_self_theme || 'off-track and frustrated'}.

Your life theme, the ${cross}, points toward a journey of growth and contribution that's uniquely yours.

**Today's experiment:** Before making your next decision — even a small one — pause and check in with your ${authority}. Notice what feels different when you let it guide you rather than your mind.`;
}
