# Atualizar os cards do perfil

Os SVGs em `assets/` são servidos pelo próprio repositório. Não dependem de um serviço de estatísticas externo e não executam workflows de GitHub Actions.

Para coletar dados atuais, tenha Python 3.9+ e GitHub CLI autenticado:

```sh
python3 scripts/update-profile.py
git diff --stat
```

Revise e publique os SVGs atualizados pelo Git. Os cards mostram a data de coleta: não são estatísticas em tempo real. As linguagens refletem bytes de código dos repositórios públicos próprios, excluindo forks; não representam nível de domínio. O calendário segue os dados retornados pelo GitHub, sem modificar contribuições.

O calendário aparece no início, em verde, junto do volume mensal de contribuições. O histórico de commits lista os quatro mais recentes de minha autoria nas branches padrão dos projetos públicos, com links verificáveis; contribuições e commits são medidas diferentes.

O retrato ASCII se forma linha por linha durante quatro segundos e permanece completo por 3,5 segundos. Para movimento reduzido, o README usa a imagem estática. Os gráficos de atividade são estáticos. Para reconstruir o GIF a partir do retrato existente, use Python com Pillow e Arial ou DejaVu Sans:

```sh
python3 scripts/build-intro.py
```

As ilustrações de avatar foram geradas com IA a partir da foto pública do titular. A foto original não precisa ser incluída neste repositório.
