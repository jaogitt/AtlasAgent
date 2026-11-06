import asyncio
import os
from datetime import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Input, RichLog, Button
from textual.screen import ModalScreen
from textual.binding import Binding
from rich.text import Text
from .agent import Agent

LOGO = r'''    /\\     █████╗ ████████╗██╗      █████╗ ███████╗
   /  \\    ██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔════╝
  / /\\ \\   ███████║   ██║   ██║     ███████║███████╗
 /_/  \\_\\  ██╔══██║   ██║   ██║     ██╔══██║╚════██║
            ██║  ██║   ██║   ███████╗██║  ██║███████║
            ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝'''


CSS = '''
Screen { background: #08090f; color: #ffe6f1; }
Header { background: #160b14; color: #ff529d; }
Footer { background: #160b14; color: #ff529d; }

#main { height: 1fr; }

#left {
    width: 28;
    border: round #ff529d;
    padding: 1;
    background: #130d16;
}

#center {
    width: 1fr;
    padding: 0 1;
}

#right {
    width: 29;
    border: round #ff529d;
    padding: 1;
    background: #130d16;
}

.heading {
    color: #ff529d;
    text-style: bold;
    margin: 1 0;
}

.meta {
    color: #f3a6c9;
    margin: 0 0 1 0;
}

#logo {
    height: 9;
    content-align: center middle;
    color: #ff529d;
    text-style: bold;
}

#chat {
    border: round #ff529d;
    height: 1fr;
    padding: 1;
    background: #130d16;
}

#input {
    margin: 1 0 0 0;
    border: round #ff529d;
    background: #1d1020;
    color: #ffe6f1;
}

#input:focus {
    border: round #ff529d;
}

#status {
    color: #ff529d;
    height: 1;
}

#approval {
    align: center middle;
}

#approval-box {
    background: #1d1020;
    border: round #ff529d;
    width: 75;
    max-width: 95%;
    height: auto;
    padding: 2;
}

#approval-question {
    margin-bottom: 2;
    color: #ffe6f1;
}

Button {
    margin-right: 2;
    background: #ff529d;
    color: #08090f;
}

Button:hover {
    background: #ff80b7;
}
'''


class Approval(ModalScreen[bool]):
    def __init__(self, question):
        super().__init__()
        self.question = question
    def compose(self):
        with Vertical(id='approval-box'):
            yield Static('CONFIRMAR AÇÃO', classes='heading')
            yield Static(self.question, id='approval-question')
            with Horizontal():
                yield Button('Permitir', variant='success', id='yes')
                yield Button('Recusar', variant='error', id='no')
    def on_button_pressed(self, event):
        self.dismiss(event.button.id == 'yes')

class AtlasApp(App):
    CSS = CSS
    TITLE = 'ATLAS AGENT | NVIDIA NIM'
    BINDINGS = [Binding('ctrl+q','quit','Sair'),Binding('ctrl+l','clear_chat','Limpar')]
    def __init__(self, workspace):
        super().__init__()
        self.agent = Agent(workspace)
        self.busy = False
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id='main'):
            with Vertical(id='left'):
                yield Static('▸ SESSÃO',classes='heading')
                yield Static('Workspace:',classes='meta')
                yield Static(str(self.agent.workspace),classes='meta')
                yield Static('▸ MODELO',classes='heading')
                yield Static(self.agent.model,classes='meta')
                yield Static('Provedor: NVIDIA NIM',classes='meta')
                yield Static('▸ COMANDOS',classes='heading')
                yield Static('/help  Ajuda\n/clear Limpar chat\n/model Modelo ativo\n/exit  Sair\nCtrl+Q Sair',classes='meta')
            with Vertical(id='center'):
                yield Static(LOGO,id='logo')
                yield RichLog(id='chat',wrap=True,markup=False,highlight=False,auto_scroll=True)
                yield Input(placeholder='❯ Digite uma mensagem ou /help...',id='input')
                yield Static('ATLAS v0.1.0  •  NVIDIA NIM  •  ações de escrita/shell exigem confirmação',id='status')
            with Vertical(id='right'):
                yield Static('▸ FERRAMENTAS',classes='heading')
                yield Static('● list_files\n● read_file\n● write_file\n● run_shell',classes='meta')
                yield Static('▸ SEGURANÇA',classes='heading')
                yield Static('✓ Escrita com confirmação\n✓ Shell com confirmação\n✓ Arquivos no workspace\n✓ Timeout de comandos',classes='meta')
                yield Static('▸ MOTOR',classes='heading')
                yield Static('NVIDIA NIM\nNemotron 3 Ultra 550B\nTool calling automático',classes='meta')
        yield Footer()
    def on_mount(self):
        log=self.query_one('#chat',RichLog)
        log.write(Text('ATLAS AGENT v0.1.0',style='bold cyan'))
        log.write('Bem-vindo. Digite uma tarefa para começar. Use /help para comandos.')
        if not os.getenv('NVIDIA_API_KEY') or os.getenv('NVIDIA_API_KEY') == 'cole_sua_chave_aqui':
            log.write(Text('ATENÇÃO: Configure NVIDIA_API_KEY no arquivo .env.',style='bold yellow'))
        self.query_one('#input',Input).focus()
    def action_clear_chat(self):
        self.query_one('#chat',RichLog).clear()
        self.agent.messages=self.agent.messages[:1]
    async def on_input_submitted(self,event:Input.Submitted):
        prompt=event.value.strip()
        if not prompt or self.busy:return
        event.input.value=''
        log=self.query_one('#chat',RichLog)
        if prompt in ('/exit','/quit'):
            self.exit();return
        if prompt == '/clear':
            self.action_clear_chat();return
        if prompt == '/help':
            log.write('/help, /clear, /model, /exit | Peça tarefas em linguagem natural.');return
        if prompt == '/model':
            log.write('Modelo: '+self.agent.model);return
        log.write(Text('VOCÊ › '+prompt,style='bold cyan'))
        self.busy=True
        event.input.disabled=True
        self.run_worker(self.respond(prompt),exclusive=True)
    async def respond(self,prompt):
        log=self.query_one('#chat',RichLog)
        status=self.query_one('#status',Static)
        async def notify(msg):
            status.update(str(msg)[:130])
            if not str(msg).startswith('Consultando NVIDIA') and not str(msg).startswith('Analisando resultado'):
                log.write(Text(str(msg),style='dim'))
        async def approve(question):
            return await self.push_screen_wait(Approval(question))
        try:
            answer=await self.agent.run(prompt,notify,approve)
            log.write(Text('ATLAS ›',style='bold bright_cyan'))
            log.write(answer)
            status.update('Pronto  •  /help comandos  •  Ctrl+Q sair')
        except Exception as e:
            log.write(Text('ERRO › '+str(e),style='bold red'))
            status.update('Erro na chamada NVIDIA NIM; verifique chave, modelo e disponibilidade')
        finally:
            self.busy=False
            inp=self.query_one('#input',Input)
            inp.disabled=False
            inp.focus()
