@echo off
echo =======================================================
echo   Menjalankan Backend (Laravel) & Frontend (Vue.js 3)
echo =======================================================
start "Backend Laravel" cmd /k "cd backend && php artisan serve"
start "Frontend Vue 3 Vite" cmd /k "cd frontend && npm run dev"
echo Backend dan Frontend telah dijalankan di jendela terpisah!
echo.
echo Akses Web di: http://localhost:5173
echo Backend API di: http://127.0.0.1:8000
pause

