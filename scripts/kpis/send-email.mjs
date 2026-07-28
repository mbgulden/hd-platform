#!/usr/bin/env node
// scripts/kpis/send-email.mjs
// Send the rendered KPI HTML report to mbgulden@gmail.com via SMTP/SendGrid.
// Falls back to writing the email to /tmp/kpi-email.eml so the rest of the cron can run without live credentials.

import fs from 'node:fs';
let nodemailer = null;
try {
  nodemailer = (await import('nodemailer')).default;
} catch {
  nodemailer = null;
}

async function main() {
  const args = process.argv.slice(2);
  const reportJsonPath = args[0];
  if (!reportJsonPath || !fs.existsSync(reportJsonPath)) {
    console.error('usage: node send-email.mjs <report.json>');
    process.exit(2);
  }
  const report = JSON.parse(fs.readFileSync(reportJsonPath, 'utf8'));

  const subjectPrefix = (process.env.HDE_KPI_SUBJECT_PREFIX) || '[HDE KPI]';
  const subject = `${subjectPrefix} ${report.kind} — ${report.windowStartISO.slice(0, 10)}`;
  const to = process.env.HDE_KPI_EMAIL_TO || 'mbgulden@gmail.com';
  const from = process.env.HDE_KPI_EMAIL_FROM || 'HDE BI Notifications <bi@humandesignengine.com>';

  const text = Object.values(report.collections).map((coll) => (
    `${coll.title}\n` +
    coll.metrics.map((m) => `  - ${m.label}: ${m.formatted} (${m.delta_pct})`).join('\n')
  )).join('\n\n');

  const html = report.html || `<pre>${text}</pre>`;

  const smtpHost = process.env.HDE_SMTP_HOST;
  const smtpUser = process.env.HDE_SMTP_USER;
  const smtpPass = process.env.HDE_SMTP_PASS;

  if (!smtpHost) {
    const eml = [
      `From: ${from}`,
      `To: ${to}`,
      `Subject: ${subject}`,
      `MIME-Version: 1.0`,
      `Content-Type: text/html; charset=utf-8`,
      '',
      html,
    ].join('\n');
    fs.writeFileSync('/tmp/kpi-email.eml', eml);
    console.log('no SMTP configured; wrote email to /tmp/kpi-email.eml');
    return;
  }

  const transport = nodemailer.createTransport({
    host: smtpHost,
    port: Number(process.env.HDE_SMTP_PORT || 587),
    secure: process.env.HDE_SMTP_SECURE === 'true',
    auth: smtpUser ? { user: smtpUser, pass: smtpPass } : undefined,
  });
  await transport.sendMail({ from, to, subject, text, html });
  console.log(`sent ${subject} → ${to}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
