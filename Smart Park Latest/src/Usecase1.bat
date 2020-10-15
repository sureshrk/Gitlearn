@echo OFF
cls
echo ---------------
echo A member car with license no. MH04FA488 is entering... Proceed?
pause
python src\mainapp.py -l "MH04FA488"
echo ---------------            
echo A member car with license no. MH04FA488 is exiting... Proceed?
pause
python src\mainapp.py -l "MH04FA488"
echo ---------------
echo ----------------