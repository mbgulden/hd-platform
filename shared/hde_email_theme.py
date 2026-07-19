"""Human Design Engine light/sage transactional email theme.

Keep transactional emails pinned to the active HDE site theme so old navy/gold
or plain-only email styles do not creep back in. Source palette/type comes from
`src/layouts/Layout.astro` and `src/components/Nav.astro` in the canonical HDE
site:

- Outfit body typeface
- Playfair Display logo/headline typeface
- light cream page background
- sage text/accent palette
- understated rounded white cards
"""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from typing import Iterable

# Canonical HDE light/sage tokens. Keep these in hex form for email-client safety.
HDE_EMAIL_THEME = {
    "sage_deep": "#2F3631",
    "sage_dark": "#3F4741",
    "sage_mid": "#5F7261",
    "sage_light": "#8E9E90",
    "cream_bg": "#FAF7F0",
    "cream_light": "#FDFBF7",
    "taupe_muted": "#8C8275",
    "taupe_light": "#C7BFB5",
    "text_primary": "#2F3631",
    "text_secondary": "#5C625E",
    "text_muted": "#808682",
    "white": "#FFFFFF",
    "card_border": "rgba(95,114,97,.15)",
    "shadow": "0 8px 30px rgba(47,54,49,.03)",
}

BODY_FONT = "Outfit, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
DISPLAY_FONT = "'Playfair Display', Georgia, serif"
SITE_URL = "https://staging.humandesignengine.com/deconditioning/"


def brand_logo_html() -> str:
    t = HDE_EMAIL_THEME
    return (
        f"<div style=\"font-family:{DISPLAY_FONT};font-size:22px;line-height:1;"
        f"font-weight:700;letter-spacing:-.01em;color:{t['sage_deep']};\">"
        f"Human Design <span style=\"font-style:italic;font-weight:400;color:{t['sage_mid']};\">Engine</span>"
        "</div>"
    )


def html_email_shell(*, eyebrow: str, title: str, intro: str, cta_label: str | None = None,
                     cta_url: str | None = None, body_html: str = "") -> str:
    """Return a table-based HDE light/sage HTML email body."""
    t = HDE_EMAIL_THEME
    safe_url = escape(cta_url or "", quote=True)
    cta_block = ""
    if cta_label and cta_url:
        cta_block = f"""
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:{t['cream_light']};border:1px solid {t['sage_light']};border-radius:18px;\">
            <tr>
              <td style=\"padding:22px;\">
                <a href=\"{safe_url}\" style=\"display:inline-block;background:{t['sage_deep']};color:{t['cream_bg']};text-decoration:none;border-radius:30px;padding:13px 22px;font-weight:600;font-size:15px;\">{escape(cta_label)}</a>
                <p style=\"margin:16px 0 0;color:{t['text_muted']};font-size:13px;line-height:1.55;word-break:break-word;\">If the button does not open, copy this link:<br><a href=\"{safe_url}\" style=\"color:{t['sage_mid']};\">{safe_url}</a></p>
              </td>
            </tr>
          </table>"""
    return f"""<!doctype html>
<html lang=\"en\">
  <body style=\"margin:0;padding:0;background:{t['cream_bg']};color:{t['text_primary']};font-family:{BODY_FONT};\">
    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:{t['cream_bg']};padding:34px 14px;\">
      <tr>
        <td align=\"center\">
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:640px;background:{t['white']};border:1px solid {t['card_border']};border-radius:24px;overflow:hidden;box-shadow:{t['shadow']};\">
            <tr>
              <td style=\"padding:30px 30px 12px;\">
                {brand_logo_html()}
                <div style=\"margin-top:26px;color:{t['sage_mid']};font-weight:700;text-transform:uppercase;letter-spacing:.16em;font-size:12px;\">{escape(eyebrow)}</div>
                <h1 style=\"margin:14px 0 10px;font-family:{DISPLAY_FONT};font-size:38px;line-height:1.06;color:{t['sage_deep']};font-weight:600;\">{escape(title)}</h1>
                <p style=\"margin:0;color:{t['text_secondary']};font-size:17px;line-height:1.65;\">{escape(intro)}</p>
              </td>
            </tr>
            <tr>
              <td style=\"padding:18px 30px 8px;\">{cta_block}</td>
            </tr>
            <tr>
              <td style=\"padding:18px 30px 30px;color:{t['text_secondary']};font-size:16px;line-height:1.7;\">
                <div style=\"background:{t['cream_light']};border:1px solid {t['sage_light']};border-radius:18px;padding:20px 20px 4px;\">
                  {body_html}
                </div>
                <div style=\"height:1px;background:{t['card_border']};margin:26px 0 18px;\"></div>
                <p style=\"margin:0;color:{t['sage_deep']};font-family:{DISPLAY_FONT};font-size:17px;font-weight:700;\">Human Design <span style=\"font-style:italic;font-weight:400;color:{t['sage_mid']};\">Engine</span></p>
                <p style=\"margin:5px 0 0;color:{t['text_secondary']};font-size:14px;\">Your private Human Design sanctuary</p>
                <p style=\"margin:5px 0 0;font-size:13px;\"><a href=\"{SITE_URL}\" style=\"color:{t['sage_mid']};text-decoration:none;\">staging.humandesignengine.com/deconditioning</a></p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""


def paragraph(text: str) -> str:
    return f"<p style=\"margin:0 0 16px;\">{escape(text)}</p>"


def build_onboarding_email(deep_link: str) -> tuple[str, str, str]:
    subject = "Your next step: open your Human Design sanctuary"
    plain = f"""SOMATIC EXPERIMENT STATION

You’re in.
Nothing else to figure out right now. Your next step is simple.

Open your private Telegram sanctuary
{deep_link}

This link does not expire. If you get interrupted, overwhelmed, distracted, or need to
come back later, use this email and pick up right here.

If anything feels confusing, reply to this email and we’ll help.

Human Design Engine
Your private Human Design sanctuary
staging.humandesignengine.com/deconditioning
"""
    html = html_email_shell(
        eyebrow="Somatic Experiment Station",
        title="You’re in.",
        intro="Nothing else to figure out right now. Your next step is simple.",
        cta_label="Open your private Telegram sanctuary",
        cta_url=deep_link,
        body_html=(
            paragraph("This link does not expire. If you get interrupted, overwhelmed, distracted, or need to come back later, use this email and pick up right here.")
            + paragraph("If anything feels confusing, reply to this email and we’ll help.")
        ),
    )
    return subject, plain, html


def build_report_email(name: str, report_type: str) -> tuple[str, str, str]:
    title_report = report_type.title()
    subject = f"Your Human Design {title_report} report is ready, {name}"
    plain = f"""Hi {name},

Your Human Design {title_report} report is attached as a PDF.

Read it at your own pace. This is a private reference, not another task to perform.

If anything feels confusing, reply to this email and we’ll help.

Human Design Engine
Your private Human Design sanctuary
https://staging.humandesignengine.com/deconditioning/"""
    html = html_email_shell(
        eyebrow="Human Design Report",
        title=f"Your {title_report} report is ready.",
        intro=f"Hi {name}, your PDF is attached. Read it at your own pace.",
        body_html=(
            paragraph("This is a private reference, not another task to perform.")
            + paragraph("If anything feels confusing, reply to this email and we’ll help.")
        ),
    )
    return subject, plain, html


def attach_themed_alternative(msg: MIMEMultipart, plain: str, html: str) -> None:
    alternative = MIMEMultipart("alternative")
    alternative.attach(MIMEText(plain, "plain", "utf-8"))
    alternative.attach(MIMEText(html, "html", "utf-8"))
    msg.attach(alternative)


def build_themed_message(*, from_email: str, to_email: str, subject: str, plain: str, html: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg
