# USB Boot Windows

Application Windows avec interface graphique Tkinter pour :

- détecter les disques et les clés USB avec leur numéro réel ;
- repérer les fichiers de démarrage Windows (`bootmgr`, `EFI\\Boot\\bootx64.efi`, `sources`) ;
- ouvrir les pages officielles Microsoft de téléchargement de Windows 10/11 ;
- choisir une version et une langue avant la recherche ;
- effacer une clé, la partitionner en GPT/FAT32 et copier une ISO Windows dessus.

## Lancement

Double-cliquez sur `lancer_usb_boot.bat`. Python 3 doit être installé (Tkinter est inclus dans l'installation officielle Python). Le script demande automatiquement les droits administrateur nécessaires.

Pour créer un vrai `.exe` sans installer Python sur le PC cible :

```bat
py -m pip install pyinstaller
pyinstaller --onefile --windowed --name USB-Boot-Windows usb_boot_windows.py
```

L'exécutable sera dans `dist\\USB-Boot-Windows.exe`.

## Important

1. La création efface entièrement la clé sélectionnée. Vérifiez le numéro, le nom et la taille avant de confirmer.
2. Le disque système est exclu automatiquement grâce à `Get-Disk` et à `IsBoot`; ne forcez jamais une clé inconnue.
3. Microsoft fournit les ISO et demande parfois une validation supplémentaire. L'application ouvre les pages officielles, car les liens ISO directs sont temporaires et varient selon la langue/région.
4. La copie utilise `robocopy`. Une ISO dont `install.wim` dépasse 4 Go peut nécessiter NTFS ou un découpage DISM ; utilisez alors l'outil officiel Microsoft/Rufus si FAT32 refuse ce fichier.
