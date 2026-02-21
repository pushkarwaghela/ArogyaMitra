Write-Host "Fixing all store configurations..." -ForegroundColor Cyan

$storeFiles = @(
    "src/stores/TSAuthStore.ts",
    "src/stores/workoutStore.ts",
    "src/stores/nutritionStore.ts",
    "src/stores/progressStore.ts",
    "src/stores/chatStore.ts"
)

foreach ($file in $storeFiles) {
    if (Test-Path $file) {
        Write-Host "  Processing $file..." -ForegroundColor Yellow
        $content = Get-Content $file -Raw
        
        # Replace getStorage with storage
        $content = $content -replace "getStorage:.*?localStorage,", "storage: localStorage,"
        $content = $content -replace "getStorage:.*?localStorage", "storage: localStorage"
        
        Set-Content $file -Value $content -NoNewline
        Write-Host "  ✅ Fixed $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ File not found: $file" -ForegroundColor Red
    }
}

Write-Host "`n✅ All store configurations fixed!" -ForegroundColor Green
Write-Host "Please also add the /aromi route to App.jsx manually." -ForegroundColor Yellow