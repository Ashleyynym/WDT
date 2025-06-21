# SQLite Helper Script
# Usage: . .\sqlite_helper.ps1
# Then use: sqlite wdt_aircargo.db

function sqlite {
    param(
        [string]$database,
        [string]$query
    )
    
    $sqlitePath = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\SQLite.SQLite_Microsoft.Winget.Source_8wekyb3d8bbwe\sqlite3.exe"
    
    if ($query) {
        & $sqlitePath $database $query
    } else {
        & $sqlitePath $database
    }
}

Write-Host "SQLite helper loaded! Use 'sqlite wdt_aircargo.db' to open the database."
Write-Host "Or use 'sqlite wdt_aircargo.db SELECT * FROM user;' to run a query." 