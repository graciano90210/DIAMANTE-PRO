$env:Path += ";C:\src\flutter\bin"
$projectDir = "C:\Proyectodiamantepro\DIAMANTE_PRO\mobile-app"
$androidDir = "$projectDir\android"

Set-Location $projectDir

Write-Host "Stopping Gradle Daemons..."
if (Test-Path $androidDir) {
    Set-Location $androidDir
    cmd /c "gradlew.bat --stop"
    Set-Location $projectDir
}

Write-Host "Cleaning Project..."
cmd /c "flutter clean"

Write-Host "Retrying Build..."
cmd /c "flutter build apk --release"
