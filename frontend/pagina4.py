import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import main as mn

try:
    from PIL import Image, ImageTk
    # Pillow está instalada: guardamos essa informação numa flag
    TEM_PIL = True
# Se a Pillow não estiver instalada, o programa continua funcionando sem ela
except ImportError:
    TEM_PIL = False