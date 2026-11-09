# Cards do perfil

Os SVGs em `assets/` são gerados por `scripts/update-profile.py` a partir do widget de contribuições e da API do GitHub e servidos pelo próprio repositório, sem serviço externo de estatísticas.

O workflow `.github/workflows/update-profile.yml` roda o script de hora em hora e publica os cards quando mudam. O commit é do `github-actions[bot]` e não entra no meu calendário de contribuições. Para rodar na hora, use *Run workflow* na aba Actions ou, localmente, com Python 3.9+ e GitHub CLI autenticado:

```sh
python3 scripts/update-profile.py
git diff --stat
```

O que cada card mostra:

- `activity.svg`: dias ativos, sequência atual, maior sequência e melhor dia dentro do período do calendário, mais as contribuições dos últimos 12 meses. Os dados vêm do próprio widget de contribuições do perfil (`github.com/users/<login>/contributions`), então batem com o gráfico nativo; se o GitHub mudar o formato do widget, o script falha sem alterar os cards. A sequência atual pode terminar ontem enquanto o dia de hoje está em andamento.
- `stack-*.svg`, `project-*.svg` e `contact-*.svg`: conteúdo definido nas listas `STACK`, `PROJECTS` e `CONTACTS` no início do script. Linguagem e estrelas dos projetos vêm da API.

Os cards com sufixo `-dark` e `-light` acompanham o tema de quem visita. O histórico de commits no README lista os quatro mais recentes de minha autoria nas branches padrão dos projetos públicos.

O retrato ASCII se forma linha por linha durante quatro segundos e permanece completo por 3,5 segundos; com movimento reduzido, o README usa a versão estática. Para reconstruir o GIF a partir do retrato existente, use Python com Pillow e Arial ou DejaVu Sans:

```sh
python3 scripts/build-intro.py
```

As ilustrações de avatar foram geradas com IA a partir da foto pública do titular. A foto original não precisa ser incluída neste repositório.
