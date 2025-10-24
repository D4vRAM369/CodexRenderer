#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import sys, argparse

__version__ = "0.1.0"

def main():
    print("DEBUG: entrando a main()")
    import tkinter as tk
    root = tk.Tk()
    root.title("CodexRenderer — Smoke Test")
    tk.Label(root, text="Hola 👋 — Si ves esta ventana, Tkinter está OK").pack(padx=16, pady=16)
    root.mainloop()

if __name__ == "__main__":
    print("DEBUG: argv =", sys.argv)
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--version", "-version", "-v", action="store_true")
    args, _ = ap.parse_known_args()
    if args.version:
        print(f"CodexRenderer GUI {__version__}")
        sys.exit(0)
    main()

