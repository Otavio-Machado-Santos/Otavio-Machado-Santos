#!/usr/bin/env python3
"""Gera os cards do perfil a partir do widget de contribuições e da API do GitHub.

Uso: gh auth login; python3 scripts/update-profile.py
Ou: python3 scripts/update-profile.py --data /caminho/dados.json [--date DD/MM/AAAA]
O modo --data renderiza uma coleta já realizada, sem nova consulta.
O workflow .github/workflows/update-profile.yml roda este script de hora em hora.
"""

import argparse
from datetime import datetime, timedelta
from html import escape
import json
from pathlib import Path
import re
import subprocess
import textwrap
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = "Otavio-Machado-Santos"
QUERY = '''query { user(login: "Otavio-Machado-Santos") {
  login
  repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
    pageInfo { hasNextPage }
    nodes { name stargazerCount primaryLanguage { name color } }
  }
} }'''
# O widget de contribuições do próprio perfil: a mesma página que o GitHub mostra a quem visita.
CALENDAR_URL = f"https://github.com/users/{USERNAME}/contributions"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
MONO_EM = 0.602  # largura do caractere nas fontes monoespaçadas acima
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
# Cores do próprio calendário do GitHub em cada tema.
THEMES = {
    "dark": {"border": "#30363d", "ink": "#e6edf3", "muted": "#8b949e", "link": "#4493f8", "chip": "#161b22",
             "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]},
    "light": {"border": "#d0d7de", "ink": "#1f2328", "muted": "#59636e", "link": "#0969da", "chip": "#f6f8fa",
              "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]},
}
TERMINAL = {"bg": "#0d1117", "green": "#39d353", "bar": "#2ea043", "accent": "#f46800"}  # cores do retrato

# Conteúdo editorial: o que aparece nos cards de projeto e de stack.
PROJECTS = [
    ("royal-mcp", "Royal MCP",
     "Fronteira de confiança para operar hosts SSH a partir de inventários do Royal TS/TSX, com isolamento de credenciais.",
     ["MCP", "SSH"]),
    ("Organizer_brain", "Caderno",
     "App nativo para macOS e iOS: captura rápida, rotina do dia e entregas do GitHub com revisão gerada por IA.",
     ["SwiftUI", "SwiftData"]),
    ("Scripts-Olt-Vsol-Cpu-Temp-SSH", "Monitoramento de OLTs VSOL",
     "Scripts para coletar temperatura de CPU por SSH e integrar os dados ao monitoramento do Zabbix.",
     ["Zabbix", "SSH"]),
    ("agentLangchainGroqV1", "Agente LangChain + Groq",
     "Agente conversacional com consultas dinâmicas sobre dados de incidentes em tempo real.",
     ["LangChain", "Groq"]),
]
# Dois cards lado a lado no desktop; em tela estreita, um embaixo do outro.
STACK = [
    [("Métricas e alertas", ["Zabbix", "Grafana", "Prometheus"]),
     ("Erros e telemetria", ["Sentry", "OpenTelemetry", "OTLP", "Collector"]),
     ("Automação e IA", ["Python", "n8n", "LangChain", "LLMs", "Shell", "PowerShell"])],
    [("DevOps e infra", ["Docker", "Kubernetes", "Linux", "Proxmox", "VMware", "Nginx", "AWS", "Azure"]),
     ("Dev e dados", ["Rust", "TypeScript", "JavaScript", "React", "Tauri", "MySQL", "PostgreSQL", "MariaDB"])],
]
CONTACTS = [("linkedin", "LinkedIn"), ("email", "E-mail"), ("x", "X · @Machadokkj")]

REPO_ICON = "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"
STAR_ICON = "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"


def number(value):
    return f"{value:,}".replace(",", ".")


def text(x, y, value, size, fill, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'


def write(name, width, height, content, title, background="none", border="#30363d"):
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">\n'
        f'<title>{escape(title)}</title>\n'
        f'<style>text{{font-family:{SANS}}}.mono{{font-family:{MONO}}}</style>\n'
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="8" fill="{background}" stroke="{border}"/>\n'
        f'{content}\n</svg>\n', encoding="utf-8")


def fetch_calendar():
    """Lê o calendário do widget do perfil, para o card mostrar exatamente o total e os níveis do GitHub.

    A API GraphQL conta alguns dias de outro jeito e fica com um total diferente do que aparece no perfil.
    """
    request = Request(CALENDAR_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8")
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    counts = {}
    for cell, label in re.findall(r'<tool-tip[^>]*\bfor="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>', page):
        count = re.match(r"\s*(No|[\d,]+) contributions?\b", label)
        if count:
            counts[cell] = 0 if count.group(1) == "No" else int(count.group(1).replace(",", ""))
    days = []
    for tag in re.findall(r'<td[^>]*\bdata-date="[^>]*>', page):
        date, cell, level = (re.search(rf'\b{name}="([^"]+)"', tag) for name in ("data-date", "id", "data-level"))
        if not (cell and level) or cell.group(1) not in counts:
            raise ValueError("O widget de contribuições mudou de formato: célula sem id, nível ou contagem.")
        days.append({"date": date.group(1), "contributionCount": counts[cell.group(1)],
                     "contributionLevel": LEVELS[int(level.group(1))]})
    if not total or not days:
        raise ValueError("O widget de contribuições mudou de formato: total ou células não encontrados.")
    days.sort(key=lambda day: day["date"])
    weeks = []
    for day in days:
        if not weeks or datetime.fromisoformat(day["date"]).weekday() == 6:  # a semana começa no domingo
            weeks.append({"contributionDays": []})
        weeks[-1]["contributionDays"].append(day)
    return {"totalContributions": int(total.group(1).replace(",", "")), "weeks": weeks}


def activity_summary(calendar):
    days = sorted((day for week in calendar["weeks"] for day in week["contributionDays"]), key=lambda day: day["date"])
    if not days:
        raise ValueError("Calendário vazio.")
    for previous, day in zip(days, days[1:]):
        if datetime.fromisoformat(day["date"]) - datetime.fromisoformat(previous["date"]) != timedelta(days=1):
            raise ValueError("Há uma lacuna ou data repetida no calendário retornado pela API.")
    if sum(day["contributionCount"] for day in days) != calendar["totalContributions"]:
        raise ValueError("O total de contribuições não corresponde às células do calendário.")
    current = longest = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] else 0
        longest = max(longest, run)
    # Um dia ainda em andamento sem contribuição não interrompe a sequência de ontem.
    for day in reversed(days if days[-1]["contributionCount"] else days[:-1]):
        if not day["contributionCount"]:
            break
        current += 1
    return days, current, longest


def render_calendar(calendar, updated):
    """O calendário de contribuições como o GitHub o desenha: mesmas células, níveis e cores."""
    weeks = calendar["weeks"]
    pitch, left, top = 15, 54, 76
    width, height = left + len(weeks) * pitch - 3 + 24, 222
    for theme, c in THEMES.items():
        parts = [f'<text x="24" y="40"><tspan font-size="20" font-weight="600" fill="{c["ink"]}">{number(calendar["totalContributions"])}</tspan>'
                 f'<tspan font-size="14" fill="{c["muted"]}" dx="7">contribuições no último ano</tspan></text>',
                 text(width - 24, 39, f"atualizado em {updated}", 12, c["muted"], 'text-anchor="end"')]
        for row, label in [(1, "seg"), (3, "qua"), (5, "sex")]:
            parts.append(text(24, top + row * pitch + 10, label, 11, c["muted"]))
        last_month, last_label = None, -9
        for col, week in enumerate(weeks):
            first = datetime.fromisoformat(week["contributionDays"][0]["date"])
            if (first.year, first.month) != last_month:
                last_month = (first.year, first.month)
                # A primeira coluna pode ser o resto de um mês: só rotula quando há espaço.
                starts_soon = col == 0 and first.day > 14
                if col - last_label >= 3 and not starts_soon:
                    parts.append(text(left + col * pitch, top - 10, MONTHS[first.month - 1], 11, c["muted"]))
                    last_label = col
            for day in week["contributionDays"]:
                row = (datetime.fromisoformat(day["date"]).weekday() + 1) % 7
                fill = c["levels"][LEVELS.index(day["contributionLevel"])]
                parts.append(f'<rect x="{left + col * pitch}" y="{top + row * pitch}" width="12" height="12" rx="2.5" fill="{fill}"/>')
        footer = top + 7 * pitch + 23
        parts.append(text(24, footer, "Calendário do GitHub, incluindo repositórios privados", 12, c["muted"]))
        legend = width - 24 - 31 - 5 * pitch
        parts.append(text(legend - 8, footer, "Menos", 11, c["muted"], 'text-anchor="end"'))
        for i, fill in enumerate(c["levels"]):
            parts.append(f'<rect x="{legend + i * pitch}" y="{footer - 10}" width="12" height="12" rx="2.5" fill="{fill}"/>')
        parts.append(text(width - 24, footer, "Mais", 11, c["muted"], 'text-anchor="end"'))
        write(f"contributions-{theme}.svg", width, height, "".join(parts),
              f"{number(calendar['totalContributions'])} contribuições no último ano", border=c["border"])


def render_activity(calendar, updated):
    """Card de terminal ao lado do retrato: mesma altura e moldura, sempre escuro."""
    days, current, longest = activity_summary(calendar)
    c, t = THEMES["dark"], TERMINAL
    best = max(days, key=lambda day: day["contributionCount"])
    best_date = datetime.fromisoformat(best["date"]).strftime("%d/%m")
    parts = [text(22, 27, "otavio@github ~ $ ./atividade", 12, t["green"], 'class="mono"'),
             text(498, 27, updated, 11, c["muted"], 'class="mono" text-anchor="end"')]
    stats = [(number(sum(bool(day["contributionCount"]) for day in days)), "dias ativos"),
             (number(current), "sequência atual"),
             (number(longest), "maior sequência"),
             (number(best["contributionCount"]), f"melhor dia · {best_date}")]
    for i, (value, label) in enumerate(stats):
        x = 22 + i * 122
        parts += [text(x, 78, value, 28, c["ink"], 'font-weight="600"'), text(x, 98, label, 12, c["muted"])]
    parts.append(f'<path d="M22 118H498" stroke="{c["border"]}"/>')
    parts.append(text(22, 144, "Contribuições por mês", 13, c["ink"], 'font-weight="600"'))

    totals = {}
    for day in days:
        totals[day["date"][:7]] = totals.get(day["date"][:7], 0) + day["contributionCount"]
    months = sorted(totals)[-12:]  # descarta o mês parcial do início do período
    peak = max(totals[m] for m in months) or 1
    base, tall, step, bar = 286, 104, 476 / len(months), 22
    for i, month in enumerate(months):
        x = 22 + i * step + (step - bar) / 2
        h = totals[month] / peak * tall
        if h < 3:
            parts.append(f'<rect x="{x:.1f}" y="{base - 2}" width="{bar}" height="2" fill="{c["border"]}"/>')
        else:
            r = min(4, h)
            parts.append(f'<path d="M{x:.1f} {base}v{-(h - r):.1f}a{r} {r} 0 0 1 {r} {-r}h{bar - 2 * r}a{r} {r} 0 0 1 {r} {r}v{h - r:.1f}z" fill="{t["bar"]}"/>')
        if totals[month] == peak:
            parts.append(text(f"{x + bar / 2:.1f}", f"{base - h - 7:.1f}", number(totals[month]), 11, c["ink"], 'text-anchor="middle" font-weight="600"'))
        parts.append(text(f"{x + bar / 2:.1f}", base + 17, MONTHS[int(month[5:]) - 1], 11, c["muted"], 'text-anchor="middle"'))
    parts.append(f'<path d="M22 {base}.5H498" stroke="{c["border"]}"/>')
    parts.append(f'<path d="M472 319H498" stroke="{t["accent"]}" stroke-width="3"/>')
    write("activity.svg", 520, 336, "".join(parts),
          f"Atividade no último ano: {stats[0][0]} dias ativos, sequência atual de {current} dias, maior sequência de {longest} dias, "
          f"melhor dia com {stats[3][0]} contribuições. Contribuições por mês: "
          + ", ".join(f"{MONTHS[int(m[5:]) - 1]} {totals[m]}" for m in months) + ".",
          background=t["bg"])


def pills(labels, x, y, c, size=12.5, height=26, pad=10, gap=8, limit=None):
    """Desenha etiquetas monoespaçadas, quebrando a linha em `limit`. Devolve (svg, y final, largura)."""
    parts, cursor = [], x
    for label in labels:
        w = round(len(label) * size * MONO_EM + 2 * pad)
        if limit and cursor + w > limit and cursor > x:
            cursor, y = x, y + height + gap
        parts.append(f'<rect x="{cursor}.5" y="{y}.5" width="{w}" height="{height}" rx="6" fill="{c["chip"]}" stroke="{c["border"]}"/>'
                     + text(cursor + pad, y + height / 2 + size * 0.36, label, size, c["ink"], 'class="mono"'))
        cursor += w + gap
    return "".join(parts), y, cursor - gap - x


def render_stack():
    width = 420
    for theme, c in THEMES.items():
        cards = []
        for groups in STACK:
            parts, y = [], 20
            for area, tools in groups:
                chips, end, _ = pills(tools, 20, y + 20, c, limit=width - 20)
                parts += [text(20, y + 10, area, 12, c["muted"]), chips]
                y = end + 26 + 18
            cards.append((parts, y, groups))
        height = max(y for _, y, _ in cards)
        for i, (parts, _, groups) in enumerate(cards, 1):
            write(f"stack-{i}-{theme}.svg", width, height, "".join(parts),
                  "; ".join(f"{area}: {', '.join(tools)}" for area, tools in groups), border=c["border"])


def render_projects(repositories):
    by_name = {repo["name"]: repo for repo in repositories}
    for name, title, description, tags in PROJECTS:
        repo = by_name[name]  # falha se um projeto em destaque deixar de ser público
        language = repo["primaryLanguage"] or {"name": "", "color": None}
        lines = textwrap.wrap(description, 54)
        if len(lines) > 3:
            raise ValueError(f"Descrição longa demais para o card de {name}.")
        for theme, c in THEMES.items():
            parts = [f'<path d="{REPO_ICON}" transform="translate(20 20)" fill="{c["muted"]}"/>',
                     text(44, 33, title, 15, c["link"], 'font-weight="600"')]
            parts += [text(20, 60 + i * 19, line, 13, c["ink"]) for i, line in enumerate(lines)]
            x = 20
            if language["name"]:
                parts += [f'<circle cx="{x + 6}" cy="122" r="6" fill="{language["color"] or c["muted"]}"/>',
                          text(x + 18, 126, language["name"], 12, c["muted"], 'class="mono"')]
                x += 18 + round(len(language["name"]) * 12 * MONO_EM) + 14
            for tag in tags:
                parts.append(text(x, 126, tag, 12, c["muted"], 'class="mono"'))
                x += round(len(tag) * 12 * MONO_EM) + 14
            if repo["stargazerCount"]:
                parts += [f'<path d="{STAR_ICON}" transform="translate(372 111) scale(.85)" fill="{c["muted"]}"/>',
                          text(400, 126, repo["stargazerCount"], 12, c["muted"], 'class="mono" text-anchor="end"')]
            write(f"project-{name.lower()}-{theme}.svg", 420, 146, "".join(parts), f"{title}: {description}", border=c["border"])


def render_contacts():
    for theme, c in THEMES.items():
        for key, label in CONTACTS:
            chip, _, w = pills([label], 0, 0, c, size=13, height=31, pad=14)
            (ASSETS / f"contact-{key}-{theme}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 1}" height="32" viewBox="0 0 {w + 1} 32" role="img" aria-label="{escape(label)}">'
                f'<title>{escape(label)}</title><style>.mono{{font-family:{MONO}}}</style>{chip}</svg>\n', encoding="utf-8")


def collect_public_commits(user):
    commits = []
    for repo in user["repositories"]["nodes"]:
        if repo["name"] == USERNAME:
            continue
        endpoint = f'repos/{USERNAME}/{repo["name"]}/commits?author={USERNAME}&per_page=5'
        result = subprocess.run(["gh", "api", endpoint], check=True, text=True, capture_output=True)
        for commit in json.loads(result.stdout):
            commits.append({"repo": repo["name"], "sha": commit["sha"], "date": commit["commit"]["author"]["date"],
                            "title": commit["commit"]["message"].splitlines()[0], "url": commit["html_url"]})
    return sorted(commits, key=lambda c: c["date"], reverse=True)[:4]


def render_commits(commits):
    def markdown(value):
        return re.sub(r'([\\`*\[\]<>])', r'\\\1', value)
    lines = []
    for commit in commits:
        date = datetime.fromisoformat(commit["date"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Sao_Paulo"))
        lines.append(f'- **{date:%d/%m/%Y} · {markdown(commit["repo"])}:** [{markdown(commit["title"])}]({commit["url"]}) · `{commit["sha"][:7]}`')
    readme = ROOT / "README.md"
    source = readme.read_text(encoding="utf-8")
    start, end = "<!-- public-commits:start -->", "<!-- public-commits:end -->"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError("Marcadores do histórico de commits ausentes ou duplicados no README.")
    before, rest = source.split(start)
    _, after = rest.split(end)
    readme.write_text(before + start + "\n\n" + "\n".join(lines) + "\n\n" + end + after, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--date", help="Data da coleta, DD/MM/AAAA; usada somente com --data.")
    args = parser.parse_args()
    if args.date and not args.data:
        parser.error("--date requer --data")
    if args.data:
        payload = json.loads(args.data.read_text(encoding="utf-8"))
    else:
        result = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"], check=True, text=True, capture_output=True)
        payload = json.loads(result.stdout)
    if payload.get("errors"):
        raise ValueError(payload["errors"])
    user = payload["data"]["user"]
    if user["login"] != USERNAME:
        raise ValueError("A API retornou um usuário diferente do perfil configurado.")
    if user["repositories"]["pageInfo"]["hasNextPage"]:
        raise ValueError("Mais de 100 repositórios: pagine a consulta antes de atualizar os cards.")
    updated = args.date or datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")
    calendar = user["contributionsCollection"]["contributionCalendar"] if args.data else fetch_calendar()
    activity_summary(calendar)  # valida datas e total antes de escrever qualquer card
    render_calendar(calendar, updated)
    render_activity(calendar, updated)
    render_stack()
    render_projects(user["repositories"]["nodes"])
    render_contacts()
    commits = payload.get("publicCommits") if args.data else collect_public_commits(user)
    if commits is not None:
        render_commits(commits)
    print(f"Cards de {USERNAME} atualizados. Coleta: {updated}.")


if __name__ == "__main__":
    main()
