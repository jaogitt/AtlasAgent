# Regras de workspace - ATLAS AGENT

## Workspace ativo

O agente deve trabalhar no workspace escolhido pelo usuário ao iniciar a sessão. Ao executar iniciar.bat, o workspace é a pasta do agente. Ao executar tlas.ps1, o workspace é a pasta atual do PowerShell.

## Arquivos e comandos

- Operações de listar, ler e gravar arquivos recebem caminhos relativos ao workspace; caminhos resolvidos fora dele são bloqueados pelo agente.
- Gravar arquivos e executar comandos PowerShell exige confirmação explícita na interface.
- A confirmação do PowerShell não limita o comando ao workspace. Revise o comando antes de aprová-lo, pois ele pode acessar outros caminhos com as permissões do usuário.
- Não execute o agente como administrador e mantenha backups dos projetos.

Estas regras descrevem o comportamento da aplicação e não substituem controles de segurança do sistema operacional.
