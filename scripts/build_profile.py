"""Génère tous les visuels du profil GitHub en SVG (thèmes clair et sombre).

Aucune dépendance externe. Les données d'activité viennent de l'API GraphQL
de GitHub via GITHUB_TOKEN, GH_TOKEN ou la CLI gh si elle est connectée.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("PROFILE_USER", "jeremyzn")
OUT = Path(__file__).resolve().parent.parent / "assets"

SANS = "Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
MONO_RATIO = 0.6  # largeur d'un caractère monospace, en fraction de la taille

THEMES = {
    "dark": {
        "bg": "#0B0B0D",
        "surface": "#131316",
        "line": "#24242A",
        "text": "#F3F1EC",
        "muted": "#8E8C87",
        "faint": "#5A5955",
        "accent": "#FF6B3D",
        "accent2": "#FFB168",
        "accent3": "#C2410C",
        "empty": "#1B1B1F",
        "orb": 0.55,
    },
    "light": {
        "bg": "#FAF8F4",
        "surface": "#FFFFFF",
        "line": "#E6E2DA",
        "text": "#141414",
        "muted": "#6B6862",
        "faint": "#A8A49C",
        "accent": "#E8501F",
        "accent2": "#FF9B54",
        "accent3": "#F7C3A0",
        "empty": "#EFEBE4",
        "orb": 0.38,
    },
}

MONTHS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
MONTHS_LONG = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
               "août", "septembre", "octobre", "novembre", "décembre"]


# Outils SVG

def svg(w: int, h: int, label: str, body: str, style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title>"
        f"<style>{style}</style>{body}</svg>"
    )


def text(x, y, content, size, fill, *, family=SANS, weight=400, anchor="start",
         spacing=0.0, extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'letter-spacing="{spacing}" {extra}>{escape(content)}</text>'
    )


def frame(w, h, t, r=28) -> str:
    return (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{r}" '
        f'fill="{t["bg"]}" stroke="{t["line"]}"/>'
    )


def eyebrow(x, y, label, t) -> str:
    return text(x, y - 4, label.upper(), 13, t["accent"], family=MONO, weight=600, spacing=2.4)


def chip_width(label: str, size: int = 15, pad: int = 16) -> float:
    return len(label) * size * MONO_RATIO + pad * 2


def chip(x, y, label, t, size=15, pad=16, h=38) -> str:
    w = chip_width(label, size, pad)
    return (
        f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" '
        f'fill="{t["surface"]}" stroke="{t["line"]}"/>'
        + text(f"{x + w / 2:.1f}", y + h / 2 + size * 0.35, label, size, t["text"],
               family=MONO, anchor="middle")
    )


# Hero

ROTATING = [
    "des interfaces web soignées",
    "des applications mobiles",
    "des API robustes",
    "une infra cloud fiable",
    "des intégrations IA utiles",
]


def hero(t) -> str:
    w, h = 1200, 440
    step = 2.6
    total = step * len(ROTATING)
    style = f"""
      .w {{ opacity: 0; animation: swap {total}s cubic-bezier(.2,.7,.2,1) infinite both; }}
      .w0 {{ opacity: 1; }}
      @keyframes swap {{
        0% {{ opacity: 0; transform: translateY(18px); }}
        4% {{ opacity: 1; transform: translateY(0); }}
        {100 / len(ROTATING) - 3:.2f}% {{ opacity: 1; transform: translateY(0); }}
        {100 / len(ROTATING):.2f}% {{ opacity: 0; transform: translateY(-18px); }}
        100% {{ opacity: 0; transform: translateY(-18px); }}
      }}
      .o1 {{ animation: drift1 22s ease-in-out infinite alternate; }}
      .o2 {{ animation: drift2 26s ease-in-out infinite alternate; }}
      .o3 {{ animation: drift3 30s ease-in-out infinite alternate; }}
      @keyframes drift1 {{ to {{ transform: translate(-90px, 50px); }} }}
      @keyframes drift2 {{ to {{ transform: translate(70px, -60px); }} }}
      @keyframes drift3 {{ to {{ transform: translate(-50px, -40px); }} }}
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
      @media (prefers-reduced-motion: reduce) {{
        .w, .o1, .o2, .o3, .cursor {{ animation: none; }}
        .w0 {{ opacity: 1; }}
      }}
    """
    words = "".join(
        f'<g class="w w{i}" style="animation-delay:{i * step}s">'
        + text(64, 372, phrase, 36, t["accent"], weight=600, spacing=-0.6)
        + "</g>"
        for i, phrase in enumerate(ROTATING)
    )
    grid = "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>' for x in range(620, w, 44)
    ) + "".join(
        f'<line x1="560" y1="{y}" x2="{w}" y2="{y}"/>' for y in range(22, h, 44)
    )
    body = f"""
      <defs>
        <clipPath id="clip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27"/></clipPath>
        <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0.07 0"/></filter>
        <radialGradient id="fade" cx="0.78" cy="0.5" r="0.45">
          <stop offset="0" stop-color="#fff" stop-opacity="1"/>
          <stop offset="1" stop-color="#fff" stop-opacity="0"/>
        </radialGradient>
        <mask id="gridmask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>
      </defs>
      {frame(w, h, t)}
      <g clip-path="url(#clip)">
        <g filter="url(#blur)" opacity="{t['orb']}">
          <circle class="o1" cx="930" cy="170" r="170" fill="{t['accent']}"/>
          <circle class="o2" cx="1060" cy="320" r="130" fill="{t['accent2']}"/>
          <circle class="o3" cx="800" cy="350" r="110" fill="{t['accent3']}"/>
        </g>
        <g stroke="{t['line']}" stroke-width="1" mask="url(#gridmask)">{grid}</g>
        <rect width="{w}" height="{h}" filter="url(#grain)"/>
      </g>
      {text(64, 82, "ZENOX", 14, t['muted'], family=MONO, spacing=3)}
      {text(w - 64, 82, "PARIS", 14, t['muted'], family=MONO, spacing=3, anchor="end")}
      {text(56, 250, "Jérémy", 156, t['text'], weight=700, spacing=-7)}
      {text(64, 322, "Je conçois, je code et je mets en ligne", 36, t['muted'], weight=500, spacing=-0.6)}
      {words}
    """
    return svg(w, h, "Jérémy, alias ZenoX. Développeur full stack, cloud, mobile et IA basé à Paris.", body, style)


# Ce que je fais

SERVICES = [
    ("Produit web", ["Applications full stack, SaaS, dashboards", "et espaces clients pensés pour l'usage,", "la vitesse et la durée."],
     "React  Next.js  TypeScript  Tailwind"),
    ("Back end et intégrations", ["API, authentification, paiements, webhooks", "et services tiers branchés sur des", "données propres et bien modélisées."],
     "Node.js  Prisma  PostgreSQL  Stripe"),
    ("Cloud et DevOps", ["Conteneurs, orchestration, déploiement", "continu et exploitation Linux pour", "des mises en production sereines."],
     "Docker  Kubernetes  AWS  Cloudflare"),
    ("Mobile et IA", ["Applications Flutter, notifications,", "wallets et fonctionnalités IA intégrées", "directement au cœur du produit."],
     "Flutter  Firebase  LLM  Automatisation"),
]


def services(t) -> str:
    w, pad, gap = 1200, 0, 20
    cw = (w - gap) / 2
    ch = 236
    top = 64
    h = top + ch * 2 + gap
    parts = [eyebrow(4, 24, "Ce que je fais", t)]
    for i, (title, lines, tags) in enumerate(SERVICES):
        cx = pad + (i % 2) * (cw + gap)
        cy = top + (i // 2) * (ch + gap)
        parts.append(
            f'<rect x="{cx + 0.5}" y="{cy + 0.5}" width="{cw - 1}" height="{ch - 1}" rx="22" '
            f'fill="{t["bg"]}" stroke="{t["line"]}"/>'
        )
        parts.append(text(cx + 36, cy + 52, f"{i + 1:02d}", 14, t["accent"], family=MONO, weight=600, spacing=1))
        parts.append(text(cx + 36, cy + 92, title, 28, t["text"], weight=650, spacing=-0.6))
        for j, line in enumerate(lines):
            parts.append(text(cx + 36, cy + 128 + j * 25, line, 17, t["muted"]))
        parts.append(f'<line x1="{cx + 36}" y1="{cy + ch - 46}" x2="{cx + cw - 36}" y2="{cy + ch - 46}" stroke="{t["line"]}"/>')
        parts.append(text(cx + 36, cy + ch - 20, tags, 13, t["faint"], family=MONO, spacing=0.6,
                          extra='xml:space="preserve"'))
    label = "Ce que je fais. " + " ".join(f"{s[0]}." for s in SERVICES)
    return svg(w, h, label, "".join(parts))


# Stack

STACK = [
    ("Front", ["TypeScript", "React", "Next.js", "Tailwind CSS", "Radix UI"]),
    ("Back", ["Node.js", "Prisma", "PostgreSQL", "MySQL", "MongoDB"]),
    ("Cloud", ["Docker", "Kubernetes", "AWS", "Cloudflare", "Vercel", "Linux"]),
    ("Mobile", ["Flutter", "Firebase", "Apple Wallet", "Google Wallet"]),
    ("Services", ["Stripe", "OAuth", "Webhooks", "LLM APIs", "Discord.js"]),
    ("Outils", ["Git", "GitHub Actions", "Bash", "Postman"]),
]


def stack(t) -> str:
    w = 1200
    top, row = 64, 58
    h = top + row * len(STACK) - 10
    parts = [eyebrow(4, 24, "Stack", t)]
    for r, (group, items) in enumerate(STACK):
        y = top + r * row
        parts.append(text(4, y + 25, group, 17, t["muted"], weight=500))
        x = 150
        for item in items:
            parts.append(chip(x, y, item, t))
            x += chip_width(item) + 10
    label = "Stack. " + " ".join(f"{g}: {', '.join(i)}." for g, i in STACK)
    return svg(w, h, label, "".join(parts))


# Activité

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes { languages(first: 10) { edges { size node { name } } } }
    }
  }
}
"""


def token() -> str | None:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                              check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def fetch() -> dict | None:
    tok = token()
    if not tok:
        print("Aucun jeton GitHub trouvé, activité générée sans données.")
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {tok}", "User-Agent": "profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if payload.get("errors"):
        raise SystemExit(f"Erreur API GitHub: {payload['errors']}")
    return payload["data"]["user"]


def streaks(days: list[tuple[date, int]]) -> tuple[int, int]:
    best = run = 0
    for _, count in days:
        run = run + 1 if count else 0
        best = max(best, run)
    current = 0
    for i, (_, count) in enumerate(reversed(days)):
        if count:
            current += 1
        elif i > 0:  # aujourd'hui peut encore être vide
            break
    return current, best


def activity(t, data: dict | None) -> str:
    w = 1200
    weeks = []
    total = repos = 0
    langs: dict[str, int] = {}
    if data:
        cal = data["contributionsCollection"]["contributionCalendar"]
        total = cal["totalContributions"]
        weeks = [[(date.fromisoformat(d["date"]), d["contributionCount"]) for d in wk["contributionDays"]]
                 for wk in cal["weeks"]]
        repos = data["repositories"]["totalCount"]
        for node in data["repositories"]["nodes"]:
            for edge in node["languages"]["edges"]:
                langs[edge["node"]["name"]] = langs.get(edge["node"]["name"], 0) + edge["size"]
    days = [d for wk in weeks for d in wk]
    current, best = streaks(days)
    active = sum(1 for _, c in days if c)

    parts = [eyebrow(4, 24, "Activité", t)]

    def plural(n: int, word: str) -> str:
        return word if n == 1 else word + "s"

    stats = [(f"{total}", f"{plural(total, 'contribution')} sur 12 mois"),
             (f"{active}", f"{plural(active, 'jour')} {plural(active, 'actif')}"),
             (f"{current}", f"{plural(current, 'jour')} de série en cours"),
             (f"{best}", f"{plural(best, 'jour')} de meilleure série")]
    col = w / 4
    for i, (value, label) in enumerate(stats):
        x = 4 + i * col
        parts.append(text(x, 112, value, 56, t["text"], weight=650, spacing=-2.5))
        parts.append(text(x, 142, label, 15, t["muted"]))

    # Calendrier
    cell, gap = 16, 4
    gx, gy = 4 + 40, 206
    peak = max([c for _, c in days] or [0])
    levels = [t["empty"], t["accent3"], t["accent2"], t["accent"], t["accent"]]

    def level(c: int) -> int:
        if c == 0 or peak == 0:
            return 0
        return min(4, 1 + int(3 * c / peak)) if peak > 1 else 3

    last_month = None
    for wi, wk in enumerate(weeks):
        x = gx + wi * (cell + gap)
        first = wk[0][0]
        if first.month != last_month and first.day <= 7 and wi < len(weeks) - 2:
            parts.append(text(x, gy - 14, MONTHS[first.month - 1], 12, t["faint"], family=MONO))
            last_month = first.month
        for d, c in wk:
            y = gy + d.isoweekday() % 7 * (cell + gap)
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{levels[level(c)]}">'
                         f'<title>{c} le {d.day} {MONTHS_LONG[d.month - 1]} {d.year}</title></rect>')
    for idx, name in ((1, "Lun"), (3, "Mer"), (5, "Ven")):
        parts.append(text(4, gy + idx * (cell + gap) + 12, name, 12, t["faint"], family=MONO))

    grid_bottom = gy + 7 * (cell + gap)

    # Langages
    ly = grid_bottom + 56
    parts.append(f'<line x1="4" y1="{ly - 30}" x2="{w}" y2="{ly - 30}" stroke="{t["line"]}"/>')
    ranked = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
    size_sum = sum(v for _, v in ranked) or 1
    palette = [t["accent"], t["accent2"], t["accent3"], t["muted"], t["faint"]]
    parts.append(text(4, ly + 8, "Langages", 17, t["muted"], weight=500))
    bx, bw = 150, w - 150
    x = bx
    parts.append(f'<clipPath id="bar"><rect x="{bx}" y="{ly - 6}" width="{bw}" height="12" rx="6"/></clipPath>')
    parts.append(f'<g clip-path="url(#bar)"><rect x="{bx}" y="{ly - 6}" width="{bw}" height="12" fill="{t["empty"]}"/>')
    for i, (_, v) in enumerate(ranked):
        seg = bw * v / size_sum
        parts.append(f'<rect x="{x:.1f}" y="{ly - 6}" width="{max(seg - 3, 1):.1f}" height="12" fill="{palette[i]}"/>')
        x += seg
    parts.append("</g>")
    lx = bx
    for i, (name, v) in enumerate(ranked):
        pct = f"{100 * v / size_sum:.0f} %"
        parts.append(f'<rect x="{lx}" y="{ly + 30}" width="10" height="10" rx="3" fill="{palette[i]}"/>')
        name_w = len(name) * 14 * MONO_RATIO
        parts.append(text(lx + 18, ly + 40, name, 14, t["text"], family=MONO))
        parts.append(text(f"{lx + 28 + name_w:.1f}", ly + 40, pct, 14, t["faint"], family=MONO))
        lx += 28 + name_w + len(pct) * 14 * MONO_RATIO + 36

    now = datetime.now(timezone.utc)
    stamp = f"Mis à jour le {now.day} {MONTHS_LONG[now.month - 1]} {now.year}"
    h = ly + 84
    parts.append(text(w, h - 4, stamp, 12, t["faint"], family=MONO, anchor="end", spacing=0.4))
    parts.append(text(4, h - 4, f"{repos} dépôts publics", 12, t["faint"], family=MONO, spacing=0.4))

    label = (f"Activité GitHub. {total} contributions sur 12 mois, {active} jours actifs, "
             f"série en cours de {current} {plural(current, 'jour')}, meilleure série de {best} {plural(best, 'jour')}.")
    return svg(w, h, label, "".join(parts))


# Boutons et contact

EMAIL = "contact@zenoxhq.fr"
INK = "#140A05"  # texte posé sur la couleur d'accent

ICONS = {
    "arrow": '<path d="M7 17 17 7M8.5 7H17v8.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7 8 6 8-6"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 11v5M8 8v.01M12 16v-5M12 13.5a2.5 2.5 0 0 1 5 0V16"/>',
    "grid": '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    "chat": '<path d="M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-8l-5 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"/>',
}

BUTTONS = [
    ("portfolio", "Portfolio", "arrow", True),
    ("contact", "Me contacter", "mail", False),
    ("linkedin", "LinkedIn", "linkedin", False),
    ("projets", "Projets", "grid", False),
    ("discord", "Discord", "chat", False),
]

NARROW, WIDE = set("fijlrtI.,' "), set("mwMW")


def sans_width(label: str, size: float) -> float:
    """Largeur approximative d'un texte sans serif semi gras."""
    em = 0.0
    for c in label:
        em += 0.32 if c in NARROW else 0.86 if c in WIDE else 0.68 if c.isupper() else 0.57
    return em * size


def icon(name: str, x: float, y: float, size: float, color: str, width: float = 1.9) -> str:
    k = size / 24
    return (f'<g transform="translate({x} {y}) scale({k})" fill="none" stroke="{color}" '
            f'stroke-width="{width / k:.2f}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>')


def button(t, label: str, icon_name: str, primary: bool) -> str:
    h, size, ic, gap, pad = 48, 15, 18, 10, 18
    tw = sans_width(label, size)
    w = round(pad + ic + gap + tw + pad + 2)
    fill = t["accent"] if primary else t["surface"]
    stroke = t["accent"] if primary else t["line"]
    fg = INK if primary else t["text"]
    if primary:  # libellé puis flèche
        tx, ix = pad, pad + tw + gap
    else:  # icône puis libellé
        ix, tx = pad, pad + ic + gap
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{h / 2}" fill="{fill}" stroke="{stroke}"/>'
        + icon(icon_name, ix, (h - ic) / 2, ic, fg)
        + text(tx, h / 2 + size * 0.36, label, size, fg, weight=600,
               extra=f'textLength="{tw:.1f}" lengthAdjust="spacing"')
    )
    return svg(w, h, label, body)


def contact(t) -> str:
    w, h = 1200, 330
    style = """
      .o1 { animation: drift1 24s ease-in-out infinite alternate; }
      .o2 { animation: drift2 28s ease-in-out infinite alternate; }
      @keyframes drift1 { to { transform: translate(-70px, 30px); } }
      @keyframes drift2 { to { transform: translate(60px, -40px); } }
      @media (prefers-reduced-motion: reduce) { .o1, .o2 { animation: none; } }
    """
    pill_w = 26 + 22 + 14 + len(EMAIL) * 18 * MONO_RATIO + 18 + 18 + 26
    body = f"""
      <defs>
        <clipPath id="clip"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27"/></clipPath>
        <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
      </defs>
      {frame(w, h, t)}
      <g clip-path="url(#clip)"><g filter="url(#blur)" opacity="{t['orb']}">
        <circle class="o1" cx="1010" cy="120" r="150" fill="{t['accent']}"/>
        <circle class="o2" cx="1120" cy="280" r="120" fill="{t['accent2']}"/>
      </g></g>
      {eyebrow(64, 84, "Contact", t)}
      {text(60, 158, "Un projet en tête ?", 64, t['text'], weight=700, spacing=-2.6)}
      {text(64, 200, "Parlons de votre produit, de l'idée jusqu'à la mise en production.", 22, t['muted'])}
      <rect x="64" y="236" width="{pill_w:.0f}" height="56" rx="28" fill="{t['accent']}"/>
      {icon("mail", 64 + 26, 236 + 17, 22, INK)}
      {text(64 + 26 + 22 + 14, 236 + 35, EMAIL, 18, INK, family=MONO, weight=600)}
      {icon("arrow", 64 + pill_w - 26 - 18, 236 + 19, 18, INK)}
    """
    return svg(w, h, f"Un projet en tête ? Écrivez moi à {EMAIL}", body, style)


def main() -> None:
    (OUT / "buttons").mkdir(parents=True, exist_ok=True)
    data = fetch()
    for name, theme in THEMES.items():
        files = {
            f"hero.{name}.svg": hero(theme),
            f"services.{name}.svg": services(theme),
            f"stack.{name}.svg": stack(theme),
            f"activity.{name}.svg": activity(theme, data),
            f"contact.{name}.svg": contact(theme),
        }
        for slug, label, icon_name, primary in BUTTONS:
            files[f"buttons/{slug}.{name}.svg"] = button(theme, label, icon_name, primary)
        for filename, content in files.items():
            (OUT / filename).write_text(content, encoding="utf-8")
            print(f"ok  assets/{filename}")


if __name__ == "__main__":
    main()
