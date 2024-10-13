del *.svg 
del *.png 
del *.wav
del *.mp3
ren project.json project.bak
del *.json 
ren project.bak project.json
rd /s /q build dist