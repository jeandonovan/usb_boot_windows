#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""USB Boot Windows - Windows 10/11 USB creator."""
from __future__ import annotations
import ctypes, json, os, subprocess, threading, time, webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "USB Boot Windows"
CATALOG = [
    {"name": "Windows 11 24H2 - ISO officielle", "version": "Windows 11", "url": "https://www.microsoft.com/software-download/windows11"},
    {"name": "Windows 10 22H2 - ISO officielle", "version": "Windows 10", "url": "https://www.microsoft.com/software-download/windows10ISO"},
]
LANGUAGES = ["Français (France)", "English (United States)", "Deutsch (Deutschland)", "Español (España)", "Italiano (Italia)"]


def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False


def ps(command):
    p = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                       text=True, capture_output=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "PowerShell a échoué")
    return p.stdout.strip()


def disks():
    raw = ps("Get-Disk | Select Number,FriendlyName,BusType,Size,PartitionStyle,OperationalStatus,IsBoot | ConvertTo-Json -Compress")
    if not raw: return []
    value = json.loads(raw)
    return value if isinstance(value, list) else [value]


def size_text(value):
    try:
        n = float(value)
        for unit in ("o", "Ko", "Mo", "Go", "To"):
            if n < 1024: return f"{n:.1f} {unit}"
            n /= 1024
    except Exception: pass
    return "?"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE); self.geometry("950x650"); self.minsize(820, 560)
        self.disk_rows = []; self.usb_rows = []; self.download_rows = []
        self.build_ui(); self.refresh_disks()

    def build_ui(self):
        header = ttk.Frame(self, padding=12); header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE, font=("Segoe UI", 18, "bold")).pack(side="left")
        self.admin_label = ttk.Label(header, text="Administrateur requis pour écrire sur une clé", foreground="#b00020"); self.admin_label.pack(side="right")
        if is_admin(): self.admin_label.configure(text="Mode administrateur actif", foreground="#087f23")
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tab_detect = ttk.Frame(nb, padding=12); nb.add(self.tab_detect, text="Clés USB")
        self.tab_boot = ttk.Frame(nb, padding=12); nb.add(self.tab_boot, text="Rendre bootable")
        self.tab_download = ttk.Frame(nb, padding=12); nb.add(self.tab_download, text="Télécharger Windows")
        self.make_detect_tab(); self.make_boot_tab(); self.make_download_tab()

    def make_detect_tab(self):
        top = ttk.Frame(self.tab_detect); top.pack(fill="x")
        ttk.Button(top, text="Actualiser", command=self.refresh_disks).pack(side="left")
        ttk.Label(top, text="Le disque système est protégé.").pack(side="left", padx=12)
        cols = ("num", "name", "bus", "size", "style", "status", "boot")
        self.disk_tree = ttk.Treeview(self.tab_detect, columns=cols, show="headings", height=15)
        labels = {"num":"N°", "name":"Nom", "bus":"Bus", "size":"Taille", "style":"Partition", "status":"État", "boot":"Système"}
        for c in cols: self.disk_tree.heading(c, text=labels[c]); self.disk_tree.column(c, width=120 if c != "name" else 230)
        self.disk_tree.pack(fill="both", expand=True, pady=12)
        self.detect_result = tk.StringVar(value="Sélectionnez une clé puis cliquez sur Analyser.")
        ttk.Label(self.tab_detect, textvariable=self.detect_result, wraplength=850).pack(anchor="w")
        ttk.Button(self.tab_detect, text="Analyser la clé sélectionnée", command=self.analyze).pack(anchor="e", pady=8)

    def make_boot_tab(self):
        ttk.Label(self.tab_boot, text="Création USB UEFI (TOUTES les données seront effacées)", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        row = ttk.Frame(self.tab_boot); row.pack(fill="x", pady=12)
        ttk.Label(row, text="Clé USB :").pack(side="left")
        self.boot_disk = ttk.Combobox(row, state="readonly", width=70); self.boot_disk.pack(side="left", padx=8)
        ttk.Button(row, text="Actualiser", command=self.refresh_disks).pack(side="left")
        iso_row = ttk.Frame(self.tab_boot); iso_row.pack(fill="x", pady=4)
        ttk.Label(iso_row, text="ISO Windows :").pack(side="left")
        self.iso_entry = ttk.Entry(iso_row); self.iso_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(iso_row, text="Parcourir…", command=self.browse_iso).pack(side="left")
        ttk.Button(self.tab_boot, text="Rendre bootable et copier l'ISO", command=self.make_bootable).pack(anchor="e", pady=14)
        self.boot_log = tk.Text(self.tab_boot, height=18, state="disabled", background="#111", foreground="#eee"); self.boot_log.pack(fill="both", expand=True)

    def make_download_tab(self):
        form = ttk.Frame(self.tab_download); form.pack(fill="x")
        ttk.Label(form, text="Version :").pack(side="left")
        self.version = ttk.Combobox(form, values=["Windows 10", "Windows 11"], state="readonly", width=16); self.version.current(1); self.version.pack(side="left", padx=6)
        ttk.Label(form, text="Langue :").pack(side="left")
        self.language = ttk.Combobox(form, values=LANGUAGES, state="readonly", width=25); self.language.current(0); self.language.pack(side="left", padx=6)
        ttk.Button(form, text="Chercher", command=self.search_downloads).pack(side="left", padx=10)
        ttk.Label(self.tab_download, text="Choisissez une ligne puis ouvrez la page Microsoft officielle.").pack(anchor="w", pady=10)
        self.download_list = tk.Listbox(self.tab_download, height=9, exportselection=False); self.download_list.pack(fill="x", pady=4)
        ttk.Button(self.tab_download, text="Ouvrir le téléchargement officiel", command=self.open_download).pack(anchor="e", pady=8)

    def refresh_disks(self):
        try: self.disk_rows = disks()
        except Exception as e: self.disk_rows = []; self.log("Erreur détection disques : " + str(e))
        if hasattr(self, "disk_tree"):
            self.disk_tree.delete(*self.disk_tree.get_children())
            for d in self.disk_rows:
                self.disk_tree.insert("", "end", values=(d.get("Number"), d.get("FriendlyName", ""), d.get("BusType", ""), size_text(d.get("Size")), d.get("PartitionStyle"), d.get("OperationalStatus"), "OUI" if d.get("IsBoot") else "NON"))
        if hasattr(self, "boot_disk"):
            self.usb_rows = [d for d in self.disk_rows if not d.get("IsBoot")]
            values = [f"Disque {d.get('Number')} — {d.get('FriendlyName','')} — {size_text(d.get('Size'))}" for d in self.usb_rows]
            self.boot_disk["values"] = values
            if values: self.boot_disk.current(0)
            else: self.boot_disk.set("")

    def selected_disk(self):
        idx = self.boot_disk.current()
        if idx < 0 or idx >= len(self.usb_rows): raise ValueError("Aucune clé USB sélectionnée. Cliquez sur Actualiser.")
        return self.usb_rows[idx]

    def analyze(self):
        sel = self.disk_tree.selection()
        if not sel: return
        num = self.disk_tree.item(sel[0], "values")[0]
        try:
            raw = ps(f"Get-Partition -DiskNumber {int(num)} | Get-Volume | Select DriveLetter | ConvertTo-Json -Compress")
            parts = json.loads(raw) if raw else []; parts = parts if isinstance(parts, list) else [parts]
            found = []
            for p in parts:
                letter = p.get("DriveLetter")
                if letter:
                    root = f"{letter}:\\"
                    if any(os.path.exists(root + x) for x in ("bootmgr", "efi\\boot\\bootx64.efi", "sources\\install.wim", "sources\\install.esd")): found.append(root)
            self.detect_result.set("Bootable probable : " + ", ".join(found) if found else "Aucun fichier de démarrage détecté.")
        except Exception as e: self.detect_result.set("Analyse impossible : " + str(e))

    def search_downloads(self):
        self.download_list.delete(0, tk.END); self.download_rows = [x for x in CATALOG if x["version"] == self.version.get()]
        for item in self.download_rows: self.download_list.insert(tk.END, f"{item['name']} | Langue : {self.language.get()}")
        if not self.download_rows: self.download_list.insert(tk.END, "Aucun résultat.")

    def open_download(self):
        if not self.download_rows: self.search_downloads()
        if self.download_rows: webbrowser.open(self.download_rows[0]["url"])

    def browse_iso(self):
        p = filedialog.askopenfilename(filetypes=[("Image ISO", "*.iso"), ("Tous les fichiers", "*.*")])
        if p: self.iso_entry.delete(0, tk.END); self.iso_entry.insert(0, p)

    def log(self, text):
        if hasattr(self, "boot_log"):
            self.boot_log.configure(state="normal"); self.boot_log.insert(tk.END, text + "\n"); self.boot_log.see(tk.END); self.boot_log.configure(state="disabled")

    def make_bootable(self):
        if not is_admin(): return messagebox.showerror("Droits administrateur", "Relancez le fichier BAT en tant qu'administrateur.")
        try: d = self.selected_disk(); num = int(d["Number"])
        except Exception as e: return messagebox.showerror("Disque introuvable", str(e))
        iso = self.iso_entry.get().strip()
        if not os.path.isfile(iso): return messagebox.showerror("ISO", "Sélectionnez une image ISO existante.")
        if not messagebox.askyesno("Confirmation", f"Le disque {num} ({size_text(d.get('Size'))}) sera EFFACÉ. Continuer ?"): return
        threading.Thread(target=self.worker_boot, args=(num, iso), daemon=True).start()

    @staticmethod
    def drive_for_disk(num):
        raw = ps(f"Get-Partition -DiskNumber {num} | Get-Volume | Where-Object DriveLetter | Select -Expand DriveLetter")
        letters = [x.strip() for x in raw.splitlines() if x.strip()]
        return (letters[0] + ":\\") if letters else None

    def worker_boot(self, num, iso):
        mounted = False
        try:
            self.log(f"Initialisation du disque {num}…")
            script = f"select disk {num}\nclean\nconvert gpt\ncreate partition primary\nformat fs=fat32 quick label=WINUSB\nassign\nexit\n"
            result = subprocess.run(["diskpart.exe"], input=script, text=True, capture_output=True, encoding="cp850", errors="replace")
            if result.returncode != 0: raise RuntimeError(result.stdout + "\n" + result.stderr)
            self.log("Attribution automatique d'une lettre…")
            destination = None
            for _ in range(10):
                destination = self.drive_for_disk(num)
                if destination: break
                time.sleep(1)
            if not destination: raise RuntimeError("La clé a été formatée mais Windows ne lui a pas attribué de lettre. Ouvrez Gestion des disques et attribuez-en une, puis réessayez.")
            self.log(f"Destination détectée : {destination}")
            self.log("Montage de l'ISO…")
            safe = iso.replace("'", "''")
            ps(f"Mount-DiskImage -ImagePath '{safe}' -StorageType ISO")
            mounted = True; source = None
            for _ in range(15):
                raw = ps(f"Get-DiskImage -ImagePath '{safe}' | Get-Volume | Select -Expand DriveLetter")
                letters = [x.strip() for x in raw.splitlines() if x.strip()]
                if letters: source = letters[0] + ":\\"; break
                time.sleep(1)
            if not source: raise RuntimeError("Impossible de trouver la lettre de lecteur de l'ISO montée.")
            self.log(f"Copie de {source} vers {destination}…")
            r = subprocess.run(["robocopy", source, destination, "/E", "/R:2", "/W:2", "/NFL", "/NDL"], capture_output=True, text=True, encoding="cp850", errors="replace")
            if r.returncode > 7: raise RuntimeError(r.stdout[-1500:])
            self.log("Terminé : la clé est prête."); self.after(0, lambda: messagebox.showinfo("Terminé", "La clé USB a été créée."))
        except Exception as e:
            self.log("ERREUR : " + str(e)); self.after(0, lambda: messagebox.showerror("Échec", str(e)))
        finally:
            if mounted:
                try: ps(f"Dismount-DiskImage -ImagePath '{iso.replace(chr(39), chr(39)*2)}'")
                except Exception: pass

if __name__ == "__main__":
    if os.name != "nt": raise SystemExit("Ce programme fonctionne sous Windows uniquement.")
    App().mainloop()
