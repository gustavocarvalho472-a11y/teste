@echo off
cd /d "%~dp0"
echo Juntando as partes do video...
copy /b video_00.part+video_01.part+video_02.part+video_03.part+video_04.part+video_05.part+video_06.part+video_07.part+video_08.part+video_09.part+video_10.part+video_11.part+video_12.part+video_13.part+video_14.part+video_15.part+video_16.part "The_Night_a_King_Talked_to_the_Dead_1080p.mp4"
echo.
echo Pronto! O arquivo The_Night_a_King_Talked_to_the_Dead_1080p.mp4 esta nesta pasta.
pause
