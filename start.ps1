Write-Host "==============================="
Write-Host "China University Admission System"
Write-Host "==============================="
Write-Host ""

Write-Host "Checking environment..."
try {
    $nodeVersion = node --version
    Write-Host "OK: Node.js installed ($nodeVersion)"
} catch {
    Write-Host "ERROR: Node.js not found, please install Node.js 18+"
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Checking dependencies..."

# Check backend dependencies
if (-not (Test-Path "backend\node_modules")) {
    Write-Host "WARNING: Backend dependencies not installed, installing..."
    Set-Location backend
    npm install
    Set-Location ..
} else {
    Write-Host "OK: Backend dependencies installed"
}

# Check frontend dependencies
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "WARNING: Frontend dependencies not installed, installing..."
    Set-Location frontend
    npm install
    Set-Location ..
} else {
    Write-Host "OK: Frontend dependencies installed"
}

Write-Host ""
Write-Host "Starting development servers..."
Write-Host ""

Write-Host "Starting backend API server..."
Start-Process cmd -ArgumentList "/k cd /d backend && npm run dev" -WindowStyle Normal -WorkingDirectory $PWD

# Wait for backend to start
Start-Sleep -Seconds 3

Write-Host "Starting frontend development server..."
Start-Process cmd -ArgumentList "/k cd /d frontend && npm run dev" -WindowStyle Normal -WorkingDirectory $PWD

# Wait for frontend to start
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==============================="
Write-Host "Server started successfully!"
Write-Host ""
Write-Host "Backend API: http://localhost:3000"
Write-Host "API Documentation: http://localhost:3000/api"
Write-Host "Frontend App: http://localhost:5173"
Write-Host "Health Check: http://localhost:3000/health"
Write-Host ""
Write-Host "Tips:"
Write-Host "- Keep both command windows open"
Write-Host "- Press Ctrl+C to stop servers"
Write-Host "- Visit the URLs above to use the system"
Write-Host "==============================="
Write-Host ""

Read-Host -Prompt "Press Enter to exit"
