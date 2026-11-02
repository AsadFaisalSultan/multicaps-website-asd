#!/usr/bin/env python3
"""
Multicaps static site builder.

Each file in _build/pages/ is a page body with a small header block:

    <!--
    title: Page title
    description: Meta description
    path: about.html
    nav: about
    image: assets/img/some-image.jpg
    -->
    ...body html...

Run:  python3 _build/build.py
Output is written to the project root (plain HTML, no server needed).

Shortcodes available inside page bodies:
    {{root}}             relative path to site root ("" or "../")
    {{icon:name}}        inline SVG icon (see ICONS)
    {{cta}}              closing call-to-action band
    {{clients_marquee}}  scrolling client logo strip
    {{client_wall}}      full grid of client logos
    {{size_chart}}       interactive capsule size chart
    {{size_table}}       capsule specification table
    {{process}}          8-step production flow
    {{year}}             current year
"""
import datetime
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGES = os.path.join(HERE, "pages")
SITE_URL = "https://multicaps.net/"

PHONE = "+92 300 1268033"
PHONE_LINK = "+923001268033"
EMAIL = "info@multicaps.net"
WHATSAPP = "https://wa.me/923001268033"

# ---------------------------------------------------------------- icons
def svg(paths, fill=False):
    if fill:
        return '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' + paths + "</svg>"
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + "</svg>")

ICONS = {
    "arrow": svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "chevron": svg('<path d="M6 9l6 6 6-6"/>'),
    "phone": svg('<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>'),
    "mail": svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "pin": svg('<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>'),
    "download": svg('<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>'),
    "check": svg('<path d="M5 12.5l4.5 4.5L19 7.5"/>'),
    "shield": svg('<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>'),
    "ruler": svg('<path d="M3 17L17 3l4 4L7 21l-4-4z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>'),
    "palette": svg('<path d="M12 3a9 9 0 0 0 0 18c1.1 0 1.7-.8 1.7-1.7 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.2 0-.9.8-1.7 1.7-1.7H16a5 5 0 0 0 5-5c0-4-4-7.2-9-7.2z"/><circle cx="7.5" cy="11.5" r="1"/><circle cx="10.5" cy="7.5" r="1"/><circle cx="15" cy="8" r="1"/>'),
    "printer": svg('<path d="M7 8V3h10v5"/><rect x="3" y="8" width="18" height="9" rx="2"/><path d="M7 14h10v7H7z"/>'),
    "capsule": svg('<rect x="2.5" y="8" width="19" height="8" rx="4" transform="rotate(-35 12 12)"/><path d="M9.2 8.3l5.6 7.4" transform="rotate(0)"/>'),
    "flask": svg('<path d="M9 3h6M10 3v6L4.5 18.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3"/><path d="M7 15h10"/>'),
    "leaf": svg('<path d="M5 19c0-8 5-14 15-15-1 10-7 15-15 15z"/><path d="M5 19l7-7"/>'),
    "sun": svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>'),
    "factory": svg('<path d="M3 21V10l6 4V10l6 4V5h6v16H3z"/><path d="M7 17h2M12 17h2M17 17h1"/>'),
    "users": svg('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6.5 6.5 0 0 1 3.5 5.5"/>'),
    "globe": svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z"/>'),
    "eye": svg('<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>'),
    "box": svg('<path d="M3 7.5L12 3l9 4.5v9L12 21l-9-4.5v-9z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9"/>'),
    "thermo": svg('<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/><path d="M12 9v7"/>'),
    "doc": svg('<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>'),
    "play": svg('<path d="M7 4.5v15l13-7.5z"/>', fill=True),
    "whatsapp": svg('<path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21h.01c5.46 0 9.9-4.45 9.9-9.91C21.95 6.45 17.5 2 12.04 2zm5.8 14.03c-.25.69-1.44 1.33-1.98 1.38-.51.05-1 .24-3.36-.7-2.84-1.12-4.65-4.02-4.79-4.21-.14-.19-1.14-1.52-1.14-2.9 0-1.38.72-2.06.98-2.34.25-.28.55-.35.74-.35l.53.01c.17.01.4-.06.62.48.25.6.84 2.06.91 2.21.07.15.12.32.02.51-.1.19-.15.32-.29.49-.15.17-.31.38-.44.51-.15.15-.3.31-.13.6.17.3.76 1.25 1.63 2.03 1.12 1 2.07 1.31 2.36 1.46.3.15.47.12.64-.07.17-.2.74-.86.94-1.16.2-.3.39-.25.66-.15.27.1 1.72.81 2.02.96.3.15.49.22.56.35.07.12.07.71-.18 1.4z"/>', fill=True),
    "facebook": svg('<path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.6V21h3.1z"/>', fill=True),
    "linkedin": svg('<path d="M6.9 8.6H3.8V20h3.1V8.6zM5.4 3.5a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6zM20.2 13.4c0-3-.7-5.1-4.1-5.1-1.7 0-2.8.9-3.2 1.8h-.1V8.6H9.9V20H13v-5.6c0-1.5.3-2.9 2.1-2.9 1.8 0 1.9 1.7 1.9 3V20h3.2v-6.6z"/>', fill=True),
    "youtube": svg('<path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3L10 15z"/>', fill=True),
}

# ---------------------------------------------------------------- data
# (file number in assets/img/clients/, company name), in display order
CLIENTS = [
    (30, "Searle"), (2, "Macter"), (9, "Wilson's Healthcare"), (20, "Bosch Pharmaceuticals"),
    (5, "Scotmann Pharmaceuticals"), (21, "Don Valley Pharmaceuticals"), (1, "Global Pharmaceuticals"),
    (12, "Platinum Pharmaceuticals"), (11, "Opal Laboratories"), (13, "Tabros Pharma"), (4, "SJG"),
    (7, "Danas Pharmaceuticals"), (10, "Medisure"), (14, "EPLA"), (15, "Wellborne Pharmachem"),
    (17, "Rotex Pharmaceutical"), (18, "Amros Pharmaceuticals"), (19, "Akson Pharmaceuticals"),
    (22, "Zafa Pharmaceutical Laboratories"), (23, "Wilshire Laboratories"), (24, "Pearl Pharmaceuticals"),
    (25, "Bryon Pharmaceuticals"), (26, "Hoover Pharmaceuticals"), (27, "Jans Pharmaceuticals"),
    (28, "KCI Pharma"), (29, "Arsons Pharmaceuticals"), (31, "Aulton Pharmaceuticals"),
    (32, "Ethical Laboratories"), (33, "FAS Pharmaceuticals"),
    (8, "Fahmir Pharma"),
]

# size, closed length (mm), cap OD, body OD, volume (ml), avg weight (mg)
SIZES = [
    ("00", 23.3, 8.53, 8.18, 0.91, 118),
    ("0el", 23.5, 7.64, 7.34, 0.78, 107),
    ("0", 21.7, 7.64, 7.34, 0.68, 96),
    ("1", 19.4, 6.91, 6.63, 0.50, 76),
    ("2", 18.0, 6.35, 6.07, 0.37, 61),
    ("3", 15.9, 5.82, 5.57, 0.30, 48),
    ("4", 14.3, 5.32, 5.05, 0.21, 38),
]

# (stage, description, image, image alt)
PROCESS = [
    ("Raw material sourcing", "We buy halal-certified, TSE/BSE-free pharmaceutical gelatin and edible food-grade colours only from approved, audited suppliers. Every lot arrives with full documentation.",
     "colour-dispensing.jpg", "Gelatin and colour solutions prepared in stainless-steel vessels"),
    ("Incoming quality testing", "Each lot of gelatin and colourant is sampled and tested by our QC laboratory, and released for production only when it meets specification.",
     "lab-microscope.jpg", "Quality control analyst examining a sample under a microscope"),
    ("Gelatin melting", "Released gelatin is dissolved and conditioned in jacketed stainless-steel tanks, then blended with colours to the exact viscosity the dipping line needs.",
     "gelatin-melting.jpg", "Technician at a stainless-steel gelatin melting tank"),
    ("Capsule forming", "Stainless-steel pins dip into the gelatin solution, then the film is dried, stripped, trimmed and joined into matched caps and bodies.",
     "capsule-pins.jpg", "Yellow capsule bodies forming on stainless-steel pins"),
    ("Printing", "Logos, names and product codes are printed in edible pharmaceutical ink using axial, spin or multicolour printing, to your approved artwork.",
     "inspection-line.jpg", "White capsules carried along the automated inspection line"),
    ("Inspection", "PLC-controlled lines with high-resolution cameras and laser sensors check every capsule and automatically remove any with defects.",
     "inspection-line.jpg", "Capsules moving along the automated camera inspection line"),
    ("Packing & storage", "Approved capsules are sealed and cartoned, then held under controlled temperature and humidity so they reach you in perfect condition.",
     "sorting-machine.jpg", "Finished capsules in the sorting and packing area"),
    ("Dispatch", "Orders leave the plant with their batch documentation, for customers across Pakistan and in export markets.",
     "capsules-red-yellow.jpg", "Finished red and yellow hard gelatin capsules"),
]

# ---------------------------------------------------------------- partials
def nav_html(active, r):
    def cls(key):
        return ' is-active' if active == key else ''

    def cur(key):
        return ' aria-current="page"' if active == key else ''

    about_keys = ("about", "sustainability", "events", "careers")
    return f'''
<header class="site-header">
  <div class="container">
    <a class="brand" href="{r}index.html" aria-label="Multicaps home">
      <img src="{r}assets/img/logo.png" alt="Multicaps, Capsules for Quality Products" width="440" height="202">
    </a>
    <div class="header-actions">
      <a class="btn btn--primary btn--sm header-cta" href="{r}request-sample.html">Request a Sample</a>
      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav"><span></span></button>
    </div>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul class="nav__list">
        <li class="nav__item nav__item--has-menu{' is-active' if active in about_keys else ''}">
          <a class="nav__link" href="{r}about.html"{cur("about")}>About {ICONS["chevron"]}</a>
          <div class="nav__menu">
            <a href="{r}about.html"><strong>Our Company</strong><span>Our story since 1975, mission and values</span></a>
            <a href="{r}sustainability.html"><strong>Sustainability</strong><span>Solar energy and green initiatives</span></a>
            <a href="{r}events.html"><strong>Events &amp; Exhibitions</strong><span>Meet us at Pharma Asia and beyond</span></a>
            <a href="{r}careers.html"><strong>Careers</strong><span>Open positions at Multicaps</span></a>
          </div>
        </li>
        <li class="nav__item{cls("products")}"><a class="nav__link" href="{r}products.html"{cur("products")}>Products</a></li>
        <li class="nav__item{cls("facility")}"><a class="nav__link" href="{r}facility.html"{cur("facility")}>Facility</a></li>
        <li class="nav__item{cls("quality")}"><a class="nav__link" href="{r}quality.html"{cur("quality")}>Quality</a></li>
        <li class="nav__item{cls("blog")}"><a class="nav__link" href="{r}blog/index.html"{cur("blog")}>Insights</a></li>
        <li class="nav__item{cls("contact")}"><a class="nav__link" href="{r}contact.html"{cur("contact")}>Contact</a></li>
      </ul>
      <a class="btn btn--primary btn--sm nav__cta" href="{r}request-sample.html">Request a Sample</a>
    </nav>
  </div>
</header>'''


def topbar_html(r):
    return f'''
<div class="topbar">
  <div class="container">
    <div class="topbar__group">
      <a href="tel:{PHONE_LINK}">{ICONS["phone"]} {PHONE}</a>
      <a href="mailto:{EMAIL}">{ICONS["mail"]} {EMAIL}</a>
      <span class="topbar__hide-sm" style="display:inline-flex;align-items:center;gap:8px">{ICONS["clock"]} Plant operates 24/7</span>
    </div>
    <div class="topbar__group topbar__hide-sm">
      <a href="{r}assets/docs/Multicaps-Company-Profile.pdf" target="_blank" rel="noopener">{ICONS["download"]} Company profile (PDF)</a>
    </div>
  </div>
</div>'''


def footer_html(r):
    return f'''
<footer class="site-footer">
  <div class="container footer-top">
    <div class="footer-brand">
      <img src="{r}assets/img/logo-white.png" alt="Multicaps" width="440" height="202" loading="lazy">
      <p>Manufacturer of halal-certified empty hard gelatin capsule shells for the pharmaceutical and nutraceutical industry. Karachi, Pakistan, since 1975.</p>
      <div class="socials">
        <a href="https://www.facebook.com/multicapscapsules/" target="_blank" rel="noopener" aria-label="Multicaps on Facebook">{ICONS["facebook"]}</a>
        <a href="https://www.linkedin.com/company/multicaps-capsules-for-quality-product/" target="_blank" rel="noopener" aria-label="Multicaps on LinkedIn">{ICONS["linkedin"]}</a>
        <a href="https://www.youtube.com/watch?v=mlgEvtvZ7RE" target="_blank" rel="noopener" aria-label="Multicaps on YouTube">{ICONS["youtube"]}</a>
        <a href="{WHATSAPP}" target="_blank" rel="noopener" aria-label="Chat with Multicaps on WhatsApp">{ICONS["whatsapp"]}</a>
      </div>
    </div>
    <div class="footer-col">
      <h3>Company</h3>
      <ul>
        <li><a href="{r}about.html">About Multicaps</a></li>
        <li><a href="{r}facility.html">Our Facility</a></li>
        <li><a href="{r}quality.html">Quality &amp; Compliance</a></li>
        <li><a href="{r}sustainability.html">Sustainability</a></li>
        <li><a href="{r}events.html">Events &amp; Exhibitions</a></li>
        <li><a href="{r}careers.html">Careers</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Products &amp; resources</h3>
      <ul>
        <li><a href="{r}products.html">Hard Gelatin Capsules</a></li>
        <li><a href="{r}products.html#sizes">Capsule Sizes</a></li>
        <li><a href="{r}products.html#colours">Colours &amp; Printing</a></li>
        <li><a href="{r}blog/index.html">Insights</a></li>
        <li><a href="{r}request-sample.html">Request a Sample</a></li>
        <li><a href="{r}assets/docs/Multicaps-Company-Profile.pdf" target="_blank" rel="noopener">Company Profile (PDF)</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Contact</h3>
      <ul>
        <li><a href="tel:{PHONE_LINK}">{PHONE}</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      </ul>
      <address class="mt-s"><strong>Head Office</strong>C-197, Block 2, P.E.C.H.S, Karachi 74500</address>
      <address><strong>Production Plant</strong>A-92, Phase 1, S.I.T.E Super Highway Industrial Area, North Karachi 75340</address>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">
      <span>&copy; <span data-year>{datetime.date.today().year}</span> Multicaps. All rights reserved.</span>
      <nav aria-label="Legal">
        <a href="{r}privacy-policy.html">Privacy Policy</a>
        <a href="{r}terms.html">Terms of Use</a>
      </nav>
    </div>
  </div>
</footer>
<a class="wa-float" href="{WHATSAPP}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{ICONS["whatsapp"]}</a>'''


def cta_html(r):
    return f'''
<section class="cta-band">
  <div class="cta-band__img" aria-hidden="true"><img src="{r}assets/img/capsules-red-yellow.jpg" alt="" loading="lazy" width="1228" height="900"></div>
  <div class="container cta-band__inner">
    <div>
      <h2>Planning your next capsule order?</h2>
      <p>Tell us the size, colour, printing and quantity you need. Our sales team will come back to you with samples and a quotation.</p>
    </div>
    <div class="cta-band__actions">
      <a class="btn btn--primary" href="{r}request-sample.html">Request a Sample {ICONS["arrow"]}</a>
      <a class="cta-band__phone" href="tel:{PHONE_LINK}">{ICONS["phone"]}<span><small>Or call our sales team</small><strong>{PHONE}</strong></span></a>
    </div>
  </div>
</section>'''


def client_imgs(r, lazy=True):
    loading = ' loading="lazy"' if lazy else ""
    return [f'<img src="{r}assets/img/clients/client-{i:02d}.jpg" alt="{name}" width="300" height="200"{loading}>'
            for i, name in CLIENTS]


def marquee_html(r):
    imgs = client_imgs(r)
    dup = [re.sub(r'alt="[^"]*"', 'alt=""', i) for i in imgs]
    return f'''
<section class="clients-strip" aria-label="Our clients">
  <div class="container">
    <p class="clients-strip__label">Supplying more than 450 pharmaceutical companies, including</p>
  </div>
  <div class="marquee">
    <div class="marquee__track">{"".join(imgs)}<span aria-hidden="true" style="display:contents">{"".join(dup)}</span></div>
  </div>
</section>'''


def client_wall_html(r):
    return '<ul class="client-wall">' + "".join(f"<li>{i}</li>" for i in client_imgs(r)) + "</ul>"


def capsule_svg(length, cap_d, body_d, max_len=23.5, max_d=8.6):
    """Vertical two-piece capsule drawn to scale (units: mm): domed cap over a domed body."""
    w, h = max_d + 0.6, max_len + 0.6
    cx = w / 2
    bottom = h - 0.3
    top = bottom - length
    cap_len = length * 0.55
    cap_bottom = top + cap_len
    rc, rb = cap_d / 2, body_d / 2
    body_top = cap_bottom - 2.5
    body = (f'<path d="M{cx - rb:.2f} {body_top:.2f} V{bottom - rb:.2f} A{rb:.2f} {rb:.2f} 0 0 0 {cx + rb:.2f} {bottom - rb:.2f} '
            f'V{body_top:.2f} Z" fill="#f6f4ef" stroke="#c4cbd1" stroke-width="0.14"/>')
    cap = (f'<path d="M{cx - rc:.2f} {cap_bottom:.2f} V{top + rc:.2f} A{rc:.2f} {rc:.2f} 0 0 1 {cx + rc:.2f} {top + rc:.2f} '
           f'V{cap_bottom:.2f} Z" fill="#d4521a"/>'
           f'<rect x="{cx - rc + 0.8:.2f}" y="{top + rc * 0.8:.2f}" width="0.6" height="{cap_len - rc * 0.8 - 1.2:.2f}" rx="0.3" fill="#fff" opacity=".3"/>')
    return f'<svg viewBox="0 0 {w:.2f} {h:.2f}" aria-hidden="true">{body}{cap}</svg>'


def size_chart_html(r):
    items = []
    for s, length, cap, body, vol, wt in SIZES:
        items.append(
            f'<button class="size-item{" is-active" if s == "0" else ""}" type="button" aria-pressed="{"true" if s == "0" else "false"}" '
            f'data-size="Size {s}" data-volume="{vol:.2f} ml" data-length="{length:.1f} mm" data-weight="{wt} mg" aria-label="Size {s}">'
            f'{capsule_svg(length, cap, body)}'
            f'<span class="size-item__label"><strong>{s}</strong><span>{vol:.2f} ml</span></span></button>'
        )
    return f'<div class="sizes__chart" data-size-chart>{"".join(items)}</div>'


def size_table_html(r):
    rows = []
    for s, length, cap, body, vol, wt in SIZES:
        fill = round(vol * 0.8 * 1000)
        rows.append(f"<tr><th scope=\"row\">{s}</th><td>{length:.1f}</td><td>{cap:.2f}</td><td>{body:.2f}</td>"
                    f"<td>{vol:.2f}</td><td>{wt}</td><td>{fill}</td></tr>")
    return f'''
<div class="table-wrap">
  <table class="spec-table">
    <caption class="visually-hidden">Hard gelatin capsule size specifications</caption>
    <thead><tr><th scope="col">Size</th><th scope="col">Closed length (mm)</th><th scope="col">Cap diameter (mm)</th><th scope="col">Body diameter (mm)</th><th scope="col">Volume (ml)</th><th scope="col">Avg. shell weight (mg)</th><th scope="col">Fill weight at 0.8 g/ml (mg)</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</div>
<p class="table-note">Typical industry reference values. Multicaps specification sheets with tolerances are provided with every quotation.</p>'''


def size_options_html(r):
    items = []
    for s_, length, cap, body, vol, wt in SIZES:
        items.append(
            f'<label class="option"><input class="choice-input" type="radio" name="Capsule size" value="{s_}" required>'
            f'<span class="size-option__box">{capsule_svg(length, cap, body)}<strong>{s_}</strong><small>{vol:.2f} ml</small></span></label>'
        )
    items.append('<label class="option"><input class="choice-input" type="radio" name="Capsule size" value="Not sure" required>'
                 '<span class="size-option__box size-option__box--text">Not sure yet</span></label>')
    return '<div class="options options--sizes">' + "".join(items) + "</div>"


def process_html(r):
    tabs, panels = [], []
    total = len(PROCESS)
    for i, (title, desc, img, alt) in enumerate(PROCESS, 1):
        active = i == 1
        tabs.append(
            f'<button class="flow__tab{" is-active" if active else ""}" type="button" role="tab" id="flow-tab-{i}" '
            f'aria-controls="flow-panel-{i}" aria-selected="{"true" if active else "false"}" tabindex="{"0" if active else "-1"}">{title}</button>'
        )
        panels.append(
            f'<div class="flow__panel{" is-active" if active else ""}" role="tabpanel" id="flow-panel-{i}" aria-labelledby="flow-tab-{i}">'
            f'<div class="flow__media"><img src="{r}assets/img/{img}" alt="{alt}" width="1350" height="900" loading="lazy"></div>'
            f'<div class="flow__body"><span class="flow__count">Stage {i} of {total}</span><h3>{title}</h3><p>{desc}</p></div>'
            f'</div>'
        )
    return f'''
<div class="flow" data-flow>
  <div class="flow__tabs" role="tablist" aria-label="Production stages">{"".join(tabs)}</div>
  <div class="flow__stage">
    <div class="flow__progress" aria-hidden="true"><span style="width:{100 / total:.1f}%"></span></div>
    {"".join(panels)}
    <div class="flow__controls">
      <button class="flow__arrow" type="button" data-flow-prev aria-label="Previous stage">{ICONS["arrow"]}</button>
      <button class="flow__arrow" type="button" data-flow-next aria-label="Next stage">{ICONS["arrow"]}</button>
    </div>
  </div>
</div>'''



# ---------------------------------------------------------------- page shell
def page_html(meta, body, r):
    title = meta["title"]
    full_title = title if "Multicaps" in title else f"{title} | Multicaps"
    desc = meta.get("description", "")
    path = meta["path"]
    canonical = SITE_URL + ("" if path == "index.html" else path.replace("index.html", ""))
    image = SITE_URL + meta.get("image", "assets/img/hero-capsule-line.jpg")
    og_type = meta.get("ogtype", "website")
    schema = meta.get("schema", "")
    robots = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Multicaps">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13202b">
<link rel="icon" type="image/png" href="{r}assets/img/favicon.png">
<link rel="apple-touch-icon" href="{r}assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100,400..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/style.css">
{schema}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
{topbar_html(r)}
{nav_html(meta.get("nav", ""), r)}
<main id="main">
{body}
</main>
{footer_html(r)}
<script src="{r}assets/js/main.js" defer></script>
</body>
</html>
'''


def parse(text):
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)", text, re.S)
    meta, body = {}, text
    if m:
        body = m.group(2)
        key = None
        for line in m.group(1).strip().splitlines():
            km = re.match(r"^(\w+):\s?(.*)$", line)
            if km and not line.startswith(" "):
                key = km.group(1)
                meta[key] = km.group(2).strip()
            elif key:
                meta[key] += "\n" + line
    return meta, body


def render(body, r):
    body = body.replace("{{cta}}", cta_html(r))
    body = body.replace("{{clients_marquee}}", marquee_html(r))
    body = body.replace("{{client_wall}}", client_wall_html(r))
    body = body.replace("{{size_chart}}", size_chart_html(r))
    body = body.replace("{{size_table}}", size_table_html(r))
    body = body.replace("{{process}}", process_html(r))
    body = body.replace("{{size_options}}", size_options_html(r))
    body = body.replace("{{year}}", str(datetime.date.today().year))
    body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)
    body = body.replace("{{root}}", r)
    return body


def main():
    urls = []
    for name in sorted(os.listdir(PAGES)):
        if not name.endswith(".html"):
            continue
        with open(os.path.join(PAGES, name), encoding="utf-8") as f:
            meta, body = parse(f.read())
        path = meta["path"]
        depth = path.count("/")
        r = "/" if meta.get("absolute") else "../" * depth
        meta["schema"] = render(meta.get("schema", ""), r)
        html = page_html(meta, render(body, r), r)
        out = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        if not meta.get("noindex"):
            urls.append(SITE_URL + ("" if path == "index.html" else path.replace("index.html", "")))
        print("built", path)

    today = datetime.date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls]
    sitemap.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write("\n".join(sitemap) + "\n")
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /_build/\n\nSitemap: {SITE_URL}sitemap.xml\n")
    print("built sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
