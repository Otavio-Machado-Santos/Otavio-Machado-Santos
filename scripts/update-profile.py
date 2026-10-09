#!/usr/bin/env python3
"""Atualiza os cards locais a partir da API do GitHub, sem GitHub Actions.

Uso: gh auth login; python3 scripts/update-profile.py
Ou: python3 scripts/update-profile.py --data /caminho/dados.json
O modo --data permite renderizar uma coleta já realizada, sem nova consulta.
"""

import argparse
from collections import defaultdict
from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USERNAME = "Otavio-Machado-Santos"
QUERY = '''query { user(login: "Otavio-Machado-Santos") {
  login
  repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
    totalCount pageInfo { hasNextPage }
    nodes { name stargazerCount forkCount languages(first: 100) {
      pageInfo { hasNextPage } edges { size node { name color } }
    } }
  }
  contributionsCollection { contributionCalendar {
    totalContributions weeks { contributionDays { date contributionCount contributionLevel } }
  } }
} }'''


def svg(width, height, content, title, desc=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<style>text{{font-family:Arial,Helvetica,sans-serif}}.mono{{font-family:Consolas,Menlo,monospace}}.muted{{fill:#8b949e}}.label{{fill:#e6edf3}}@media(prefers-reduced-motion:reduce){{.pulse{{animation:none}}}}</style>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="14" fill="#0d1117" stroke="#30363d"/>
{content}</svg>'''


def text(x, y, value, size=16, fill="#e6edf3", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(str(value))}</text>'


def write(name, width, height, content, title, desc=""):
    (ASSETS / name).write_text(svg(width, height, content, title, desc), encoding="utf-8")


def render(user, updated):
    repos = user["repositories"]
    if repos.get("pageInfo", {}).get("hasNextPage"):
        raise ValueError("Mais de 100 repositórios: pagine a consulta antes de atualizar os cards.")
    calendar = user["contributionsCollection"]["contributionCalendar"]
    nodes = repos["nodes"]
    ASSETS.mkdir(exist_ok=True)
    stats = [("Repositórios públicos", repos["totalCount"]),
             ("Contribuições no ano", calendar["totalContributions"]),
             ("Estrelas recebidas", sum(r["stargazerCount"] for r in nodes)),
             ("Forks recebidos", sum(r["forkCount"] for r in nodes))]
    parts = [text(26, 36, "Atividade no GitHub", 21),
             text(26, 60, f"Dados coletados em {updated}", 12, "#8b949e")]
    for i, (label, number) in enumerate(stats):
        x = 28 + (i % 2) * 213
        y = 113 + (i // 2) * 83
        parts += [text(x, y, f"{number:,}".replace(",", "."), 32, "#39d353"),
                  text(x, y + 23, label, 13, "#8b949e")]
    write("github-stats.svg", 460, 250, "".join(parts), "Atividade no GitHub", "; ".join(f"{a}: {b}" for a, b in stats))

    languages = defaultdict(int)
    colors = {}
    for repo in nodes:
        if repo["languages"].get("pageInfo", {}).get("hasNextPage"):
            raise ValueError("Mais de 100 linguagens: pagine a consulta antes de atualizar.")
        for edge in repo["languages"]["edges"]:
            lang = edge["node"]["name"]
            languages[lang] += edge["size"]
            colors[lang] = edge["node"]["color"] or "#8b949e"
    ordered = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    total = sum(languages.values())
    parts = [text(26, 36, "Linguagens nos projetos", 21),
             text(26, 60, "Proporção de código nos repositórios públicos", 12, "#8b949e")]
    x = 28
    if total:
        for lang, size in ordered:
            width = size / total * 404
            parts.append(f'<rect x="{x:.3f}" y="85" width="{width:.3f}" height="10" fill="{colors[lang]}"/>')
            x += width
        for i, (lang, size) in enumerate(ordered[:6]):
            x = 28 + i % 2 * 213
            y = 127 + i // 2 * 32
            parts += [f'<circle cx="{x+5}" cy="{y-5}" r="4" fill="{colors[lang]}"/>',
                      text(x+18, y, f"{lang}  {size/total*100:.1f}%", 13)]
    else:
        parts.append(text(28, 130, "Sem código público classificado.", 14, "#8b949e"))
    parts.append(text(26, 229, f"Coleta: {updated} · fonte: API do GitHub", 12, "#8b949e"))
    write("languages.svg", 460, 250, "".join(parts), "Linguagens nos repositórios públicos", "; ".join(f"{k}: {v} bytes" for k, v in ordered))

    levels = {"NONE": "#161b22", "FIRST_QUARTILE": "#0e4429", "SECOND_QUARTILE": "#006d32", "THIRD_QUARTILE": "#26a641", "FOURTH_QUARTILE": "#39d353"}
    weeks = calendar["weeks"]
    months = defaultdict(int)
    month_names = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    parts = [text(28, 39, "Meu histórico no GitHub", 24),
             text(28, 68, "Um ano de contribuições · volume por dia e por mês", 14, "#8b949e"),
             text(866, 39, f"{calendar['totalContributions']:,}".replace(",", "."), 30, "#39d353", 'text-anchor="end"'),
             text(866, 63, "contribuições", 12, "#8b949e", 'text-anchor="end"')]
    last_month = None
    for col, week in enumerate(weeks):
        for day in week["contributionDays"]:
            date = datetime.fromisoformat(day["date"])
            row = (date.weekday() + 1) % 7
            x, y = 28 + col * 16, 104 + row * 16
            month = date.strftime("%Y-%m")
            months[month] += day["contributionCount"]
            if month != last_month:
                # Não sobrepor o rótulo do último mês parcial.
                if col < len(weeks) - 2:
                    parts.append(text(x, 94, month_names[date.month - 1], 11, "#8b949e"))
                last_month = month
            parts.append(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{levels[day["contributionLevel"]]}"><title>{day["date"]}: {day["contributionCount"]} contribuições</title></rect>')
    parts += [text(28, 243, "Contribuições por mês", 13),
              text(866, 243, "Meses das extremidades são parciais", 11, "#8b949e", 'text-anchor="end"')]
    step = 840 / len(months)
    maximum = max(months.values(), default=1) or 1
    for i, (month, number) in enumerate(sorted(months.items())):
        x = 28 + i * step
        height = number / maximum * 56
        parts += [f'<rect x="{x:.2f}" y="{318-height:.2f}" width="{step-10:.2f}" height="{height:.2f}" rx="2" fill="#26a641"><title>{month}: {number} contribuições</title></rect>',
                  text(x + (step-10)/2, 336, month_names[int(month[5:]) - 1] + "/" + month[2:4], 11, "#8b949e", 'text-anchor="middle"')]
    parts.append(text(28, 365, f"Coleta: {updated} · fonte: calendário do GitHub · inclui commits, PRs e issues", 12, "#8b949e"))
    desc = "Calendário real de contribuições, com volume mensal. Os meses das extremidades são parciais."
    write("contributions.svg", 900, 388, "".join(parts), "Histórico de contribuições no GitHub", desc)


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


def render_commits(commits, updated):
    def markdown(value):
        return re.sub(r'([\\`*\[\]<>])', r'\\\1', value)
    lines = []
    for commit in commits:
        date = datetime.fromisoformat(commit["date"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Sao_Paulo"))
        lines.append(f'- **{date:%d/%m/%Y} · {markdown(commit["repo"])}:** [{markdown(commit["title"])}]({commit["url"]}) · `{commit["sha"][:7]}`')
    lines.append(f"\n<sub>Últimos commits de minha autoria nas branches padrão dos projetos públicos, excluindo este README. Coleta: {updated}.</sub>")
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
    updated = args.date or datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y")
    render(user, updated)
    commits = payload.get("publicCommits") if args.data else collect_public_commits(user)
    if commits is not None:
        render_commits(commits, updated)
    print(f"Cards de {USERNAME} atualizados. Coleta: {updated}.")


if __name__ == "__main__":
    main()
