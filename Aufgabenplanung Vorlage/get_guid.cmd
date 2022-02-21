@ECHO OFF
SET SearchString="'Name'^^^>DitingerWLAN"
FOR /f "delims=" %%i IN ('wevtutil qe Microsoft-Windows-NetworkProfile/Operational /q:"Event[System[(EventID=10000)]]" /c:100 /rd:true /f:xml ^| FINDSTR /R "%SearchString%"') DO (
ECHO %%i
)