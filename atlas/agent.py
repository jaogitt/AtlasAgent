import json
import os
import subprocess
from pathlib import Path
from openai import AsyncOpenAI

SYSTEM = """Você é ATLAS AGENT, um agente de programação no terminal Windows. Responda em português. Você tem ferramentas para inspecionar, criar e editar arquivos e executar comandos PowerShell. Use ferramentas quando necessário, nunca afirme ter feito algo sem executar. Não execute operações destrutivas sem confirmação. Trabalhe dentro da pasta de projeto escolhida. Seja conciso e útil."""

TOOLS = [
 {"type":"function","function":{"name":"list_files","description":"Lista arquivos e pastas de um diretório no workspace.","parameters":{"type":"object","properties":{"path":{"type":"string","description":"Caminho relativo ao workspace"}},"required":[]}}},
 {"type":"function","function":{"name":"read_file","description":"Lê arquivo texto do workspace.","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
 {"type":"function","function":{"name":"write_file","description":"Cria ou substitui arquivo texto no workspace. Requer aprovação do usuário.","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
 {"type":"function","function":{"name":"run_shell","description":"Executa comando PowerShell no workspace. Requer aprovação do usuário.","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}}
]

class Agent:
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.model = os.getenv('NVIDIA_MODEL', 'nvidia/nemotron-3-ultra-550b-a55b')
        self.client = AsyncOpenAI(api_key=os.getenv('NVIDIA_API_KEY', ''), base_url=os.getenv('NVIDIA_BASE_URL', 'https://integrate.api.nvidia.com/v1'), timeout=180, max_retries=1)
        self.messages = [{"role":"system","content":SYSTEM + f"\nWorkspace: {self.workspace}"}]

    def resolve(self, path):
        p = (self.workspace / (path or '.')).resolve()
        if not p.is_relative_to(self.workspace):
            raise ValueError('Caminho fora do workspace bloqueado')
        return p

    async def tool(self, name, args, approve):
        if name == 'list_files':
            p = self.resolve(args.get('path', '.'))
            return '\n'.join(('DIR  ' if f.is_dir() else 'FILE ') + f.name for f in sorted(p.iterdir())[:150]) or '(vazio)'
        if name == 'read_file':
            p = self.resolve(args['path'])
            if p.stat().st_size > 200_000: return 'Arquivo muito grande (limite 200 KB)'
            return p.read_text(encoding='utf-8')[:40000]
        if name == 'write_file':
            p = self.resolve(args['path'])
            if not await approve(f'Gravar arquivo: {p.relative_to(self.workspace)}?'):
                return 'Operação recusada pelo usuário'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args['content'], encoding='utf-8')
            return f'Arquivo gravado: {p.relative_to(self.workspace)}'
        if name == 'run_shell':
            command = args['command']
            if not await approve(f'Executar PowerShell: {command[:400]}?'):
                return 'Operação recusada pelo usuário'
            try:
                r = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],cwd=self.workspace,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
                return f'Exit code: {r.returncode}\nSTDOUT:\n{r.stdout[-9000:]}\nSTDERR:\n{r.stderr[-3000:]}'
            except subprocess.TimeoutExpired:
                return 'Comando excedeu 45 segundos'
        return 'Ferramenta desconhecida'

    async def run(self, prompt, notify, approve):
        self.messages.append({'role':'user','content':prompt})
        for step in range(12):
            await notify('Consultando NVIDIA NIM...' if step == 0 else 'Analisando resultado das ferramentas...')
            response = await self.client.chat.completions.create(model=self.model,messages=self.messages,tools=TOOLS,tool_choice='auto',max_tokens=4096,temperature=0.2)
            msg = response.choices[0].message
            if msg.tool_calls:
                self.messages.append(msg.model_dump(exclude_none=True))
                if msg.content:
                    await notify(msg.content)
                for call in msg.tool_calls:
                    await notify(f'[Ferramenta] {call.function.name}')
                    try:
                        args = json.loads(call.function.arguments)
                        result = await self.tool(call.function.name,args,approve)
                    except Exception as e:
                        result = f'Erro: {e}'
                    await notify(result[:1200])
                    self.messages.append({'role':'tool','tool_call_id':call.id,'content':result[:12000]})
            else:
                answer = msg.content or '(resposta vazia)'
                self.messages.append({'role':'assistant','content':answer})
                return answer
        return 'Limite de 12 ciclos de ferramentas atingido. Continue com outra mensagem.'
