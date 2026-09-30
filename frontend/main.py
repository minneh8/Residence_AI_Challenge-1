
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pagina2 as pg2
import pagina3 as pg3
import pagina4 as pg4

try:
    from PIL import Image, ImageTk
    # Pillow está instalada: guardamos essa informação numa flag
    TEM_PIL = True
# Se a Pillow não estiver instalada, o programa continua funcionando sem ela
except ImportError:
    TEM_PIL = False

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------
# Pasta onde este arquivo .py está salvo (assim a imagem é achada em qualquer computador)
PASTA = os.path.dirname(os.path.abspath(__file__))
# Caminho completo da imagem do logo (DUAT.png deve estar na mesma pasta do script)
CAMINHO_IMAGEM = os.path.join(PASTA, "DUAT.png")

# Cores usadas na interface (formato hexadecimal)
COR_FUNDO = "#0b1b3f"
# Laranja principal (bordas, botão e textos de destaque)
COR_LARANJA = "#f0883a"
# Laranja mais escuro, usado quando o mouse passa sobre o botão
COR_LARANJA_HOVER = "#db7628"
# Azul mais claro usado no fundo do campo de texto e da tabela
COR_INPUT = "#1a2f67"
# Cor do texto principal
COR_TEXTO = "#ffffff"
# Cor do texto de placeholder (a dica dentro do campo)
COR_PLACEHOLDER = "#f0883a"

# Medidas (em pixels) dos elementos da tela inicial
LARG_INPUT = 420
# Largura do botão 'Enviar'
LARG_BOTAO = 140
# Espaço entre o campo de texto e o botão
ESPACO = 14
# Altura do campo de texto e do botão
ALTURA = 54
# Raio do arredondamento dos cantos
RAIO = 8
# Margem ao redor do desenho, para a borda não ser cortada no canvas
MARGEM = 3

# Texto-dica exibido dentro do campo enquanto o usuário não digitou nada
PLACEHOLDER = "Digite sua notícia para ser avaliada..."

# Cria a janela principal da aplicação
root = tk.Tk()
# Título exibido na barra da janela
root.title("DUAT")
# Tamanho inicial da janela (largura x altura)
root.geometry("1920x1080")
# Tamanho mínimo permitido ao redimensionar a janela
root.minsize(500, 500)
# Define a cor de fundo da janela
root.configure(bg=COR_FUNDO)


# Dicionário que guarda as imagens carregadas. É necessário mantê-las numa variável,
# senão o Python as apaga da memória e elas somem da tela
imagens = {}


# ------------------------------------------------------------
# FUNÇÕES
# ------------------------------------------------------------
# Carrega a imagem do logo. Se 'tamanho' for informado, reduz a imagem mantendo a proporção
def carregar_imagem(tamanho=None):
    try:
        # Se a Pillow está disponível, usa ela (permite redimensionar)
        if TEM_PIL:
            # Abre o arquivo de imagem
            img = Image.open(CAMINHO_IMAGEM)
            # Se foi pedido um tamanho máximo, reduz a imagem mantendo a proporção
            if tamanho:
                img.thumbnail(tamanho)
            # Converte para um formato que o Tkinter consegue exibir
            return ImageTk.PhotoImage(img)

        # Sem Pillow, usa o PhotoImage do próprio Tkinter (sem redimensionar)
        return tk.PhotoImage(file=CAMINHO_IMAGEM)

    # Se der qualquer erro (arquivo não existe, formato inválido...), mostra no console
    except Exception as e:
        print("Erro ao carregar imagem:", e)
        # Retorna None para o programa usar um texto no lugar da imagem
        return None


# Desenha um retângulo com cantos arredondados em um Canvas.
# Funciona criando um polígono suavizado (smooth=True) com pontos nos cantos
def retangulo_arredondado(cv, x1, y1, x2, y2, raio, **opcoes):
    # Lista de coordenadas (x, y) do contorno, contornando o retângulo a partir do topo esquerdo
    pontos = [
        x1 + raio, y1, x2 - raio, y1, x2, y1, x2, y1 + raio,
        x2, y2 - raio, x2, y2, x2 - raio, y2, x1 + raio, y2,
        x1, y2, x1, y2 - raio, x1, y1 + raio, x1, y1,
    ]
    # Cria o polígono no canvas e devolve o ID do desenho (usado depois para o hover do botão)
    return cv.create_polygon(pontos, smooth=True, **opcoes)


# Apaga tudo o que está na janela, para poder desenhar uma nova página
def limpar_tela():
    """Remove todos os widgets da página atual."""
    # Percorre todos os widgets filhos da janela e destrói cada um
    for widget in root.winfo_children():
        widget.destroy()


# ------------------------------------------------------------
# TRUNCAR NOTÍCIA PARA EXIBIÇÃO
# ------------------------------------------------------------
# Limita o texto da notícia exibido na tela a um número máximo de palavras
def resumir_noticia(texto, limite=50):
    """Exibe no máximo 50 palavras; se ultrapassar, adiciona '...'."""
    # Separa o texto em palavras
    palavras = texto.split()

    # Se passar do limite, corta nas primeiras 'limite' palavras
    if len(palavras) > limite:
        # Junta as palavras de volta e adiciona reticências no final
        return " ".join(palavras[:limite]) + "..."

    # Se for curto, devolve o texto original
    return texto
# ------------------------------------------------------------
# ENVIO DA NOTÍCIA
# ------------------------------------------------------------
# Chamada ao clicar em 'Enviar' ou apertar Enter (event é passado pelo Tkinter, por isso é opcional)
def enviar(event=None):
    # Lê o texto digitado, removendo espaços no início e no fim
    texto = entrada.get().strip()

    # Se estiver vazio ou ainda for só o placeholder, não deixa enviar
    if not texto or texto == PLACEHOLDER:
        # Mostra um aviso ao usuário
        messagebox.showwarning("Atenção", "Digite algo antes de enviar.")
        # Interrompe a função, sem abrir a próxima página
        return

    # Mostra no console o texto enviado (útil para testes)
    print("Enviado:", texto)

    # Depois do envio, abre a página 3 (tabela de features)
    # Abre a página 3 passando a notícia digitada (ela será repassada à página 2)
    pg3.mostrar_pagina_3(texto)


# ------------------------------------------------------------
# INPUT
# ------------------------------------------------------------
# Quando o campo ganha foco: se ainda tem o placeholder, limpa o campo
def ao_focar(event):
    # Verifica se o conteúdo é o texto-dica
    if entrada.get() == PLACEHOLDER:
        # Apaga o texto-dica
        entrada.delete(0, "end")
        # Muda a cor para branco, para o texto digitado
        entrada.config(fg=COR_TEXTO)


# Quando o campo perde o foco: se ficou vazio, recoloca o placeholder
def ao_desfocar(event):
    # Verifica se o campo está vazio
    if not entrada.get():
        # Reinsere o texto-dica
        entrada.insert(0, PLACEHOLDER)
        # Volta à cor laranja do placeholder
        entrada.config(fg=COR_PLACEHOLDER)


# ------------------------------------------------------------
# PÁGINA 1
# ------------------------------------------------------------
def mostrar_pagina_1():
    # 'entrada' é global para as outras funções (enviar, ao_focar, ao_desfocar) conseguirem ler o campo
    global entrada

    # Limpa a tela antes de montar a página inicial
    limpar_tela()

    # Frame central que agrupa logo e campo de busca
    centro = tk.Frame(root, bg=COR_FUNDO)
    # Centraliza o frame na janela
    centro.place(relx=0.5, rely=0.5, anchor="center")


    # Carrega o logo grande (máx. 700x500) da tela inicial
    imagens["logo"] = carregar_imagem((700, 500))

    # Se a imagem carregou, exibe o logo
    if imagens["logo"]:
        tk.Label(centro, image=imagens["logo"], bg=COR_FUNDO).pack(pady=(0, 40))
    # Se não carregou, mostra um aviso com o caminho esperado da imagem
    else:
        tk.Label(
            centro,
            text=f"(imagem não encontrada: {CAMINHO_IMAGEM})",
            bg=COR_FUNDO,
            fg="#8fa8d6",
            font=("Arial", 11, "italic")
        ).pack(pady=(0, 40))

    # Calcula o tamanho do canvas que contém o campo e o botão lado a lado
    largura_total = LARG_INPUT + ESPACO + LARG_BOTAO + 2 * MARGEM
    altura_total = ALTURA + 2 * MARGEM

    # Canvas onde são desenhados o campo arredondado e o botão 'Enviar'
    linha = tk.Canvas(
        centro,
        width=largura_total,
        height=altura_total,
        bg=COR_FUNDO,
        highlightthickness=0,
        bd=0
    )
    linha.pack()

    # Coordenadas do retângulo do campo de texto (canto superior esquerdo e inferior direito)
    x1, y1 = MARGEM, MARGEM
    x2, y2 = MARGEM + LARG_INPUT, MARGEM + ALTURA

    # Desenha o fundo arredondado do campo de texto
    retangulo_arredondado(
        linha, x1, y1, x2, y2, RAIO,
        fill=COR_INPUT,
        outline=COR_LARANJA,
        width=2
    )

    # Campo de texto (Entry) sem borda, por cima do retângulo arredondado
    entrada = tk.Entry(
        linha,
        font=("Arial", 15),
        justify="center",
        bg=COR_INPUT,
        fg=COR_PLACEHOLDER,
        insertbackground=COR_TEXTO,
        relief="flat",
        bd=0,
        highlightthickness=0
    )
    # Começa exibindo o placeholder
    entrada.insert(0, PLACEHOLDER)

    # Encaixa o campo de texto dentro do retângulo, no centro
    linha.create_window(
        (x1 + x2) / 2,
        (y1 + y2) / 2,
        window=entrada,
        width=LARG_INPUT - 2 * RAIO,
        height=ALTURA - 20
    )

    # Ao clicar no campo: remove o placeholder
    entrada.bind("<FocusIn>", ao_focar)
    # Ao sair do campo: recoloca o placeholder se estiver vazio
    entrada.bind("<FocusOut>", ao_desfocar)
    # Apertar Enter envia a notícia
    entrada.bind("<Return>", enviar)

    # --------------------------------------------------------
    # BOTÃO ENVIAR
    # --------------------------------------------------------
    # Posição horizontal do botão: logo depois do campo, separado por ESPACO
    bx1 = x2 + ESPACO
    bx2 = bx1 + LARG_BOTAO

    # Guardamos o ID do desenho para o hover.
    # No código original, botao_forma era usado sem ter sido criado.
    # Desenha o fundo laranja do botão e guarda o ID para mudar a cor no hover
    botao_forma = retangulo_arredondado(
        linha, bx1, y1, bx2, y2, RAIO,
        fill=COR_LARANJA,
        outline=COR_LARANJA
    )

    # Escreve o texto 'Enviar' no centro do botão
    botao_texto = linha.create_text(
        (bx1 + bx2) / 2,
        (y1 + y2) / 2,
        text="Enviar",
        fill=COR_TEXTO,
        font=("Arial", 14, "bold")
    )

    # Clicar no botão (forma ou texto) chama a função enviar
    linha.tag_bind(botao_forma, "<Button-1>", enviar)
    linha.tag_bind(botao_texto, "<Button-1>", enviar)

    # Quando o mouse entra no botão: muda o cursor para mãozinha e escurece a cor
    def entrar_botao(event):
        linha.config(cursor="hand2")
        linha.itemconfig(
            botao_forma,
            fill=COR_LARANJA_HOVER,
            outline=COR_LARANJA_HOVER
        )

    # Quando o mouse sai do botão: volta o cursor e a cor normais
    def sair_botao(event):
        linha.config(cursor="")
        linha.itemconfig(
            botao_forma,
            fill=COR_LARANJA,
            outline=COR_LARANJA
        )

    # Liga os eventos de entrar/sair do mouse tanto na forma quanto no texto do botão
    linha.tag_bind(botao_forma, "<Enter>", entrar_botao)
    linha.tag_bind(botao_forma, "<Leave>", sair_botao)
    linha.tag_bind(botao_texto, "<Enter>", entrar_botao)
    linha.tag_bind(botao_texto, "<Leave>", sair_botao)

# Apertar ESC fecha o programa
root.bind("<Escape>", lambda event: root.destroy())


# Abre a página inicial ao iniciar o programa
mostrar_pagina_1()

# Inicia o loop principal do Tkinter: mantém a janela aberta e respondendo a eventos
root.mainloop()