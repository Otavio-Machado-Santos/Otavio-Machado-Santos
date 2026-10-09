# Atualizar os cards do perfil

Os SVGs em `assets/` são servidos pelo próprio repositório. Não dependem de um serviço de estatísticas externo e não executam workflows de GitHub Actions.

Para coletar dados atuais, tenha Python 3.9+ e GitHub CLI autenticado:

```sh
python3 scripts/update-profile.py
git diff --stat
```

Revise e publique os SVGs atualizados pelo Git. Os cards mostram a data de coleta: não são estatísticas em tempo real. As linguagens refletem bytes de código dos repositórios públicos próprios, excluindo forks; não representam nível de domínio. O calendário segue os dados retornados pelo GitHub, sem modificar contribuições.

O cabeçalho em GIF e a versão PNG para movimento reduzido são elementos de apresentação. Os gráficos de atividade possuem uma versão SVG estática para quem prefere menos movimento.

As ilustrações de avatar foram geradas com IA a partir da foto pública do titular. A foto original não precisa ser incluída neste repositório.
