set PATH=%PATH%;C:\src\flutter\bin
cd C:\Proyectodiamantepro\DIAMANTE_PRO\mobile-app
echo Running Flutter Doctor... > build_log.txt
call flutter doctor >> build_log.txt 2>&1
echo Running Flutter Build... >> build_log.txt
call flutter build apk --release >> build_log.txt 2>&1
echo Done. >> build_log.txt
