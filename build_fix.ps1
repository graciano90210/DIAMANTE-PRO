$env:Path += ";C:\src\flutter\bin"
$projectDir = "C:\Proyectodiamantepro\DIAMANTE_PRO\mobile-app"

if (!(Test-Path $projectDir)) {
    Write-Error "Directory not found: $projectDir"
    exit 1
}

Set-Location $projectDir
Write-Host "Current Directory: $PWD"

Write-Host "Running flutter clean..."
cmd /c "flutter clean"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running flutter pub get..."
cmd /c "flutter pub get"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running flutter build apk --release..."
cmd /c "flutter build apk --release"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Build Complete!"
