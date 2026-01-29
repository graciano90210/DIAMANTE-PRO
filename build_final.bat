set PATH=%PATH%;C:\src\flutter\bin
cd C:\Proyectodiamantepro\DIAMANTE_PRO\mobile-app
echo Start Build %TIME% > build_final.log
call flutter build apk --release >> build_final.log 2>&1
echo End Build %TIME% >> build_final.log
