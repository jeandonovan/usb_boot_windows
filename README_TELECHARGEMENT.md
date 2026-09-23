# Téléchargement Windows en arrière-plan

Le fichier `telecharger_windows.bat` lance `telecharger_windows.ps1` avec PowerShell et télécharge sans bloquer l'interface grâce à `Start-BitsTransfer`.

- Les outils officiels Microsoft Windows 10/11 sont téléchargés automatiquement.
- Pour une ISO, collez le lien direct généré par Microsoft sur la page de téléchargement. Ces liens sont temporaires et expirent généralement ; il n'existe pas d'URL ISO permanente officielle.
- Les téléchargements sont placés dans `downloads\\`.
- Le script refuse les domaines qui ne sont pas Microsoft ou Windows CDN.

Pages officielles :

- Windows 11 : https://www.microsoft.com/software-download/windows11
- Windows 10 : https://www.microsoft.com/software-download/windows10

Double-cliquez sur `telecharger_windows.bat`. Si PowerShell bloque le script, le BAT utilise déjà `-ExecutionPolicy Bypass` pour ce lancement uniquement.
