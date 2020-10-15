@echo OFF
cls
echo Members Enter
echo ---------------
echo 4 member cars with license nos. MH04FA488, MH04DJ0746, MH46N4312 and MH46AU1589 are entering... Proceed?
pause
python src\mainapp.py -l "MH04FA488" -ent "21-09-2020 09:45:00"
echo ---------------            
python src\mainapp.py -l "MH04DJ0746" -ent "21-09-2020 09:48:00"
echo ---------------
python src\mainapp.py -l "MH46N4312" -ent "21-09-2020 09:50:00"
echo ---------------
python src\mainapp.py -l "MH46AU1589" -ent "21-09-2020 09:55:00"
echo ---------------
echo Outsiders Enter
echo 3 outsider cars with license no. MH439999, MH436666 and MH433333 are entering... Proceed?
pause
python src\mainapp.py -l "MH439999" -ent "21-09-2020 09:58:00"
echo ---------------
python src\mainapp.py -l "MH436666" -ent "21-09-2020 10:10:00"
echo ---------------
python src\mainapp.py -l "MH433333" -ent "21-09-2020 10:20:00"
echo ---------------
echo 4th outsider car with license no. MH431357 is entering... Proceed?
pause
python src\mainapp.py -l "MH431357" -ent "21-09-2020 10:30:00"
echo ---------------
Rem Now license no MH43QT9987 will be entering late after reporttime whose spot is 7 occupied by Outsider
echo A member car with license no. MH43QT9987 is entering... Proceed?
pause
python src\mainapp.py -l "MH43QT9987" -ent "21-09-2020 10:45:00"
echo ---------------
echo A member car with license no. MH43AW2192 is entering... Proceed?
pause
python src\mainapp.py -l "MH43AW2192" -ent "21-09-2020 10:50:00" 
echo ---------------
echo At this point all the spots are filled and the next car will be denied.
echo A member car with license no. MH46W1408 is entering... Proceed?
pause
python src\mainapp.py -l "MH46W1408" -ent "21-09-2020 10:55:00" 
echo ---------------
echo A outsider car with license no. MHPU1111 is entering... Proceed?
pause
python src\mainapp.py -l "MHPU1111" -ent "21-09-2020 11:00:00" 
echo ---------------
Rem We will now exit one of the outsider cars and re-enter the member who was denied earlier which is MH46W1408
echo A outsider car with license no. MH439999 is exiting... Proceed?
pause
python src\mainapp.py -l "MH439999" -ext "21-09-2020 11:05:00" 
echo ---------------
echo A member car with license no. MH46W1408 is entering... Proceed?
pause
python src\mainapp.py -l "MH46W1408" -ent "21-09-2020 11:10:00" 
echo ---------------