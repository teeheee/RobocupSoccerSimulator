@echo off
if exist %cd%\config.yml (
SET config = %cd%\config.yml
cd /d %~dp0
@echo on
robotsimul.exe %config%
pause
) else (
cd /d %~dp0
echo Warnung!! config.yml wurde nicht gefunden. Nutze installations Standard.
@echo on
robotsimul.exe
pause
)


