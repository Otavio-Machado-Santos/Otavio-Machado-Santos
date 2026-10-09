#!/usr/bin/env python3
"""Atualiza os cards locais a partir da API do GitHub, sem GitHub Actions.

Uso: gh auth login; python3 scripts/update-profile.py
Ou: python3 scripts/update-profile.py --data /caminho/dados.json
O modo --data permite renderizar uma coleta já realizada, sem nova consulta.
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta
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

    render_activity(calendar, updated)


def activity_summary(calendar):
    days = sorted((day for week in calendar["weeks"] for day in week["contributionDays"]), key=lambda day: day["date"])
    if not days:
        raise ValueError("Calendário vazio.")
    if len({day["date"] for day in days}) != len(days):
        raise ValueError("O calendário contém datas duplicadas.")
    for previous, day in zip(days, days[1:]):
        if datetime.fromisoformat(day["date"]) - datetime.fromisoformat(previous["date"]) != timedelta(days=1):
            raise ValueError("Há uma lacuna no calendário retornado pela API.")
    if sum(day["contributionCount"] for day in days) != calendar["totalContributions"]:
        raise ValueError("O total de contribuições não corresponde às células do calendário.")
    current = longest = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] else 0
        longest = max(longest, run)
    # Um dia ainda em andamento sem contribuição não interrompe a sequência de ontem.
    eligible = days if days[-1]["contributionCount"] else days[:-1]
    for day in reversed(eligible):
        if not day["contributionCount"]:
            break
        current += 1
    return days, current, longest, sum(bool(day["contributionCount"]) for day in days)


def render_activity(calendar, updated):
    days, current, longest, active = activity_summary(calendar)
    levels = {"NONE": "#161b22", "FIRST_QUARTILE": "#0e4429", "SECOND_QUARTILE": "#006d32", "THIRD_QUARTILE": "#26a641", "FOURTH_QUARTILE": "#39d353"}
    weeks = calendar["weeks"]
    month_names = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    parts = [text(27, 33, "Meu histórico de contribuições", 19),
             text(873, 33, f"{calendar['totalContributions']:,}".replace(",", ".") + " contribuições", 18, "#39d353", 'text-anchor="end"')]
    for row, label in [(1, "seg"), (3, "qua"), (5, "sex")]:
        parts.append(text(13, 75 + row * 16, label, 10, "#8b949e"))
    last_month = None
    cells = []
    for col, week in enumerate(weeks):
        for day in week["contributionDays"]:
            date = datetime.fromisoformat(day["date"])
            row = (date.weekday() + 1) % 7
            x, y = 39 + col * 16, 64 + row * 16
            month = (date.year, date.month)
            if month != last_month:
                if col < len(weeks) - 2:
                    parts.append(text(x, 55, month_names[date.month - 1], 10, "#8b949e"))
                last_month = month
            delay = col * 0.065 + row * 0.036
            cells.append((x, y, levels[day["contributionLevel"]], delay, day))
    parts.append(text(27, 192, f"Coleta: {updated} · GitHub · commits, PRs e issues", 11, "#8b949e"))
    parts.append(text(729, 192, "menos", 10, "#8b949e"))
    for i, color in enumerate(levels.values()):
        parts.append(f'<rect x="{767+i*16}" y="181" width="12" height="12" rx="2" fill="{color}"/>')
    parts.append(text(855, 192, "mais", 10, "#8b949e"))
    motion = '''<style>
.day{transform-box:fill-box;transform-origin:center;animation:assemble .5s ease-out both}
.lit{animation:glow .75s ease-out both}
@keyframes assemble{0%{opacity:0;transform:scale(.15)}70%{opacity:1;transform:scale(1.12)}100%{opacity:1;transform:scale(1)}}
@keyframes glow{0%,45%{filter:brightness(2.2)}100%{filter:brightness(1)}}
@media(prefers-reduced-motion:reduce){.day,.lit{animation:none}}
</style>'''
    desc = f"Calendário de {days[0]['date']} a {days[-1]['date']}, com dados reais do GitHub. Inclui commits, pull requests e issues."
    for animated in (False, True):
        rendered = []
        for x, y, color, delay, day in cells:
            rect = f'<rect x="{x}" y="{y}" width="13" height="13" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]} contribuições</title></rect>'
            if animated:
                if day["contributionCount"]:
                    rect = f'<g class="lit" style="animation-delay:{delay:.3f}s">{rect}</g>'
                rect = f'<g class="day" style="animation-delay:{delay:.3f}s">{rect}</g>'
            rendered.append(rect)
        write("contributions-animated.svg" if animated else "contributions-static.svg", 900, 210,
              (motion if animated else "") + "".join(parts + rendered), "Meu calendário de contribuições", desc)

    parts = [text(28, 40, "ACTIVITY LOG", 17, "#39d353", 'class="mono"'),
             text(28, 72, f"Coleta: {updated}", 15, "#8b949e")]
    # Todas as sequências são limitadas ao período retornado pelo calendário.
    for x, y, value, lines in [(28, 153, current, ["Sequência atual", "dias seguidos"]),
                               (263, 153, longest, ["Maior sequência", "no período"]),
                               (28, 290, calendar["totalContributions"], ["Contribuições", "no período"]),
                               (263, 290, active, ["Dias ativos", f"de {len(days)} dias"])] :
        parts.append(text(x, y, f"{value:,}".replace(",", "."), 56, "#39d353"))
        parts.extend(text(x, y+32+i*23, line, 18, "#e6edf3" if i == 0 else "#8b949e") for i, line in enumerate(lines))
    parts.append('<path d="M28 222H472 M248 96V347" stroke="#30363d"/>')
    parts.append(text(28, 387, "Últimos 30 dias", 20))
    recent = days[-30:]
    maximum = max((day["contributionCount"] for day in recent), default=1) or 1
    for i, day in enumerate(recent):
        height = max(2, day["contributionCount"] / maximum * 76)
        color = "#26a641" if day["contributionCount"] else "#30363d"
        parts.append(f'<rect x="{28+i*15}" y="{486-height:.2f}" width="11" height="{height:.2f}" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]} contribuições</title></rect>')
    start, end = (datetime.fromisoformat(day["date"]).strftime("%d/%m/%Y") for day in (days[0], days[-1]))
    parts += [text(28, 516, f"Período: {start} — {end}", 14, "#8b949e"),
              text(28, 541, "Fonte: calendário de contribuições do GitHub", 14, "#8b949e")]
    write("streak-stats.svg", 500, 560, "".join(parts), "Minha atividade no GitHub",
          f"Sequência atual: {current} dias; maior sequência no período: {longest} dias; {calendar['totalContributions']} contribuições; {active} dias ativos em {len(days)}. {desc}")


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
