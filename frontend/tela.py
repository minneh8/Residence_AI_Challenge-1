import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

try:
    from PIL import Image, ImageTk
    TEM_PIL = True
except ImportError:
    TEM_PIL = False

# ------------------------------------------------------------
# CONFIGURAÇÕES
# ------------------------------------------------------------
PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_IMAGEM = os.path.join(PASTA, "DUAT.png")

COR_FUNDO = "#0b1b3f"
COR_LARANJA = "#f0883a"
COR_LARANJA_HOVER = "#db7628"
COR_INPUT = "#1a2f67"
COR_TEXTO = "#ffffff"
COR_PLACEHOLDER = "#f0883a"

LARG_INPUT = 420
LARG_BOTAO = 140
ESPACO = 14
ALTURA = 54
RAIO = 8
MARGEM = 3

PLACEHOLDER = "Digite sua notícia para ser avaliada..."

root = tk.Tk()
root.title("DUAT")
root.geometry("1920x1080")
root.minsize(500, 500)
root.configure(bg=COR_FUNDO)


imagens = {}


# ------------------------------------------------------------
# FUNÇÕES
# ------------------------------------------------------------
def carregar_imagem(tamanho=None):
    try:
        if TEM_PIL:
            img = Image.open(CAMINHO_IMAGEM)
            if tamanho:
                img.thumbnail(tamanho)
            return ImageTk.PhotoImage(img)

        return tk.PhotoImage(file=CAMINHO_IMAGEM)

    except Exception as e:
        print("Erro ao carregar imagem:", e)
        return None


def retangulo_arredondado(cv, x1, y1, x2, y2, raio, **opcoes):
    pontos = [
        x1 + raio, y1, x2 - raio, y1, x2, y1, x2, y1 + raio,
        x2, y2 - raio, x2, y2, x2 - raio, y2, x1 + raio, y2,
        x1, y2, x1, y2 - raio, x1, y1 + raio, x1, y1,
    ]
    return cv.create_polygon(pontos, smooth=True, **opcoes)


def limpar_tela():
    """Remove todos os widgets da página atual."""
    for widget in root.winfo_children():
        widget.destroy()


# ------------------------------------------------------------
# TRUNCAR NOTÍCIA PARA EXIBIÇÃO
# ------------------------------------------------------------
def resumir_noticia(texto, limite=50):
    """Exibe no máximo 50 palavras; se ultrapassar, adiciona '...'."""
    palavras = texto.split()

    if len(palavras) > limite:
        return " ".join(palavras[:limite]) + "..."

    return texto


# ------------------------------------------------------------
# PÁGINA 2
# ------------------------------------------------------------
def mostrar_pagina_2(texto_noticia):
    limpar_tela()

    # Logo no canto superior direito
    imagens["logo_voltar"] = carregar_imagem((110, 80))

    if imagens["logo_voltar"]:
        botao_logo = tk.Label(
            root,
            image=imagens["logo_voltar"],
            bg=COR_FUNDO,
            cursor="hand2"
        )
    else:
        botao_logo = tk.Label(
            root,
            text="DUAT",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 18, "bold"),
            cursor="hand2"
        )

    botao_logo.place(relx=0.97, rely=0.04, anchor="ne")
    botao_logo.bind("<Button-1>", lambda event: mostrar_pagina_1())

    # Conteúdo da segunda página
    conteudo = tk.Frame(root, bg=COR_FUNDO)
    conteudo.place(relx=0.5, rely=0.1, anchor="center")

    tk.Label(
        conteudo,
        text="Análise da notícia",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 40, "bold")
    ).pack(pady=(0, 30))

    # --------------------------------------------------------
    # NOTÍCIA ENVIADA
    # Label e caixa ficam lado a lado
    # --------------------------------------------------------
    noticia = tk.Frame(root, bg=COR_FUNDO)
    noticia.place(relx=0.5, rely=0.22, anchor="center")

    tk.Label(
        noticia,
        text="Notícia enviada:",
        bg=COR_FUNDO,
        fg=COR_LARANJA,
        font=("Arial", 16, "bold")
    ).grid(row=0, column=0, padx=(0, 20), sticky="e")

    caixa_noticia = tk.Label(
        noticia,
        text=resumir_noticia(texto_noticia),
        bg=COR_INPUT,
        fg=COR_TEXTO,
        font=("Arial", 15),
        wraplength=700,
        justify="left",
        anchor="w",
        padx=25,
        pady=20
    )
    caixa_noticia.grid(row=0, column=1, sticky="w")

    # --------------------------------------------------------
    # CONTAINER DA TABELA
    # --------------------------------------------------------

    LARGURA_TABELA = 1100
    ALTURA_TABELA = 190

    canvas_tabela = tk.Canvas(
        root,
        width=LARGURA_TABELA,
        height=ALTURA_TABELA,
        bg=COR_FUNDO,
        highlightthickness=0
    )

    canvas_tabela.place(
        relx=0.5,
        rely=0.55,
        anchor="center"
    )

    retangulo_arredondado(
        canvas_tabela,
        5,
        5,
        LARGURA_TABELA - 5,
        ALTURA_TABELA - 5,
        20,
        fill=COR_INPUT,
        outline=COR_LARANJA,
        width=3
    )

    frame_tabela = tk.Frame(
        canvas_tabela,
        bg=COR_INPUT
    )

    canvas_tabela.create_window(
        LARGURA_TABELA/2,
        ALTURA_TABELA/2,
        window=frame_tabela,
        width=LARGURA_TABELA-20,
        height=ALTURA_TABELA-20
    )

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
    "Treeview",
    background=COR_INPUT,
    foreground="white",
    fieldbackground=COR_INPUT,
    bordercolor=COR_LARANJA,
    borderwidth=1,
    rowheight=35,
    font=("Arial", 11)
    )   

    style.configure(
    "Treeview.Heading",
    background=COR_LARANJA,
    foreground="black",
    relief="solid",
    borderwidth=1,
    font=("Arial", 12, "bold")
    )

    colunas = ("Features", "Valor")

    tabela = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=8
    )

    tabela.heading("Features",text="Features")
    tabela.heading("Valor",text="Valor")
    tabela.column("Features",width=750,anchor="center")
    tabela.column("Valor",width=300,anchor="center")
    tabela.pack(fill="both",expand=True,padx=10,pady=10)
    tabela.insert( "","end",values=("Confiabilidade", "85%"))
    tabela.insert("","end",values=("Fonte Verificada", "55%"))
    tabela.insert("","end",values=("Risco Fake News", "15%"))


# ------------------------------------------------------------
# ENVIO DA NOTÍCIA
# ------------------------------------------------------------
def enviar(event=None):
    texto = entrada.get().strip()

    if not texto or texto == PLACEHOLDER:
        messagebox.showwarning("Atenção", "Digite algo antes de enviar.")
        return

    print("Enviado:", texto)

    # Depois do envio, abre a segunda página
    mostrar_pagina_2(texto)


# ------------------------------------------------------------
# INPUT
# ------------------------------------------------------------
def ao_focar(event):
    if entrada.get() == PLACEHOLDER:
        entrada.delete(0, "end")
        entrada.config(fg=COR_TEXTO)


def ao_desfocar(event):
    if not entrada.get():
        entrada.insert(0, PLACEHOLDER)
        entrada.config(fg=COR_PLACEHOLDER)


# ------------------------------------------------------------
# PÁGINA 1
# ------------------------------------------------------------
def mostrar_pagina_1():
    global entrada

    limpar_tela()

    centro = tk.Frame(root, bg=COR_FUNDO)
    centro.place(relx=0.5, rely=0.5, anchor="center")


    imagens["logo"] = carregar_imagem((700, 500))

    if imagens["logo"]:
        tk.Label(centro, image=imagens["logo"], bg=COR_FUNDO).pack(pady=(0, 40))
    else:
        tk.Label(
            centro,
            text=f"(imagem não encontrada: {CAMINHO_IMAGEM})",
            bg=COR_FUNDO,
            fg="#8fa8d6",
            font=("Arial", 11, "italic")
        ).pack(pady=(0, 40))

    largura_total = LARG_INPUT + ESPACO + LARG_BOTAO + 2 * MARGEM
    altura_total = ALTURA + 2 * MARGEM

    linha = tk.Canvas(
        centro,
        width=largura_total,
        height=altura_total,
        bg=COR_FUNDO,
        highlightthickness=0,
        bd=0
    )
    linha.pack()

    x1, y1 = MARGEM, MARGEM
    x2, y2 = MARGEM + LARG_INPUT, MARGEM + ALTURA

    retangulo_arredondado(
        linha, x1, y1, x2, y2, RAIO,
        fill=COR_INPUT,
        outline=COR_LARANJA,
        width=2
    )

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
    entrada.insert(0, PLACEHOLDER)

    linha.create_window(
        (x1 + x2) / 2,
        (y1 + y2) / 2,
        window=entrada,
        width=LARG_INPUT - 2 * RAIO,
        height=ALTURA - 20
    )

    entrada.bind("<FocusIn>", ao_focar)
    entrada.bind("<FocusOut>", ao_desfocar)
    entrada.bind("<Return>", enviar)

    # --------------------------------------------------------
    # BOTÃO ENVIAR
    # --------------------------------------------------------
    bx1 = x2 + ESPACO
    bx2 = bx1 + LARG_BOTAO

    # Guardamos o ID do desenho para o hover.
    # No código original, botao_forma era usado sem ter sido criado.
    botao_forma = retangulo_arredondado(
        linha, bx1, y1, bx2, y2, RAIO,
        fill=COR_LARANJA,
        outline=COR_LARANJA
    )

    botao_texto = linha.create_text(
        (bx1 + bx2) / 2,
        (y1 + y2) / 2,
        text="Enviar",
        fill=COR_TEXTO,
        font=("Arial", 14, "bold")
    )

    linha.tag_bind(botao_forma, "<Button-1>", enviar)
    linha.tag_bind(botao_texto, "<Button-1>", enviar)

    def entrar_botao(event):
        linha.config(cursor="hand2")
        linha.itemconfig(
            botao_forma,
            fill=COR_LARANJA_HOVER,
            outline=COR_LARANJA_HOVER
        )

    def sair_botao(event):
        linha.config(cursor="")
        linha.itemconfig(
            botao_forma,
            fill=COR_LARANJA,
            outline=COR_LARANJA
        )

    linha.tag_bind(botao_forma, "<Enter>", entrar_botao)
    linha.tag_bind(botao_forma, "<Leave>", sair_botao)
    linha.tag_bind(botao_texto, "<Enter>", entrar_botao)
    linha.tag_bind(botao_texto, "<Leave>", sair_botao)

root.bind("<Escape>", lambda event: root.destroy())


mostrar_pagina_1()

root.mainloop()