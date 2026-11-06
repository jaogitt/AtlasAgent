# ATLAS AGENT

Agente de programação para terminal Windows, com interface em tela cheia (Textual) e integração com NVIDIA NIM.

## Requisitos

- Windows 10 ou superior
- Python 3.11 ou superior
- Uma chave de API NVIDIA NIM

## Instalação

No PowerShell do Windows, execute este comando para baixar e instalar a versão pública:

```powershell
irm https://raw.githubusercontent.com/jaogitt/AtlasAgent/main/install.ps1 | iex
```

Depois edite `%LOCALAPPDATA%\Programs\AtlasAgent\.env` e informe sua chave em `NVIDIA_API_KEY`. Para instalar manualmente, baixe ou clone o repositório, execute `instalar.bat`, edite `.env` e execute `iniciar.bat`.

O arquivo `.env.example` documenta as variáveis necessárias. Nunca coloque uma chave real nesse arquivo nem a envie ao Git.

## Usar em outro projeto

No PowerShell, navegue até a pasta que deseja usar como workspace e execute:

```powershell
& 'C:\caminho\AtlasAgent\atlas.ps1'
```

Para criar o comando `atlas` no seu perfil do PowerShell:

```powershell
function atlas { & 'C:\caminho\AtlasAgent\atlas.ps1' }
```

Troque o caminho pelo local onde instalou o agente.

## Recursos

- Interface de terminal com chat, barra lateral e comandos `/help`, `/clear`, `/model` e `/exit`.
- NVIDIA NIM com chamadas de ferramentas, conforme suporte do modelo e da conta.
- Ferramentas para listar, ler e gravar arquivos e executar PowerShell.
- Confirmação antes de gravar arquivos ou executar comandos.
- Limite de 12 ciclos de ferramentas por solicitação.

## Segurança e limitações

- A confirmação de comandos não é um sandbox: um comando PowerShell aprovado pode acessar recursos fora do workspace. Revise cada comando antes de permitir.
- Use projetos de teste e mantenha backups. Não execute como administrador.
- O suporte a chamadas de ferramentas depende do modelo e da conta NVIDIA; não foi validado com uma chave real.
- Esta versão não tem streaming, memória persistente, integração com Git ou busca na web.
- O workspace padrão ao usar `iniciar.bat` é a pasta do agente; ao usar `atlas.ps1`, é a pasta atual do PowerShell.
