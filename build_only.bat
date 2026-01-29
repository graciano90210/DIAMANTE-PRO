set PATH=%PATH%;C:\src\flutter\bin
cd C:\Proyectodiamantepro\DIAMANTE_PRO\mobile-app
echo Running Flutter Build Clean... > build_only_log.txt
call flutter clean >> build_only_log.txt 2>&1
echo Running Flutter Build Release... >> build_only_log.txt
call flutter build apk --release >> build_only_log.txt 2>&1
echo Done. >> build_only_log.txt
