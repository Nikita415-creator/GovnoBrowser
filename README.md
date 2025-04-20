# GovnoSBrowser
A great browser written in python using the PyQt5 library.

Отличный браузер написанный на python с использованием библиотеки PyQt5.

I-------------------------------------------------------------------------

RUSSIAN-РУССКИЙ: Хей! Здесь я опубликовал свое творение - ГовноСБраузер, сделанный на Python! Он максимально простой(200 строк кода, с учетом пропущенных строк), но с очень крутым дизайном. Дизайн: современный и темный, пока что этот браузер не настраивается, но вскором времени я сделаю меню настроек и все интегрирую. Программа а данном этапе может содержать ошибки.

УСТАНОВКА: Пока что браузер находится в стадии разработки и не имеет прямго установочного файла, поэтому устанавливается он файлом с расширением .py и запускается через редактор кода (например VS Code).

Для запуска: 

            1. скачайте новейшую версию программы (browserG-PyQt6.py) т.к все дальнейшие действия будут выполнятся именно в ней!
        
            2. Скачайте и установите VS Code [https://code.visualstudio.com/download] с официального сайтa
            
            3. Откройте скачаный файл браузера через VS Code и там же откройте терминал

            4. Выполните установку необходимых пакетов через терминал: py -m pip install PyQt6 PyQt6-WebEngine

            5. После окончания установки убеждаемся в отсутствии ошибок и запускаем файл browserG-PyQt6.py

Если вы хотите пользоваться браузером полноценно выполните сборку проекта самостоятельно:
     
‼️ Наличие библиотеки PyQt6 и компонента PyQt6-WebEngine обязательно ↑ ‼️

            1. Выполните установку необходимых пакетов через терминал: py -m pip install pyinstaller
            
            2. Откройте папку с файлом программы через VS Code
            
            3. Введите это в терминал: python -c "import os, PyQt6.QtWebEngineWidgets as w; print(os.path.join(os.path.dirname(w.__file__), '..', 'Qt6', 'resources'))"
            
            4.Введите это в терминал pyinstaller --name=GovnoBrowser --windowed --onefile --add-data "Замените это на путь который выдала прошлая команда" browserG-PyQt6.py
            
            5. Прямой установочный файл появится в папке ./dist в той же папке что и файл browserG-PyQt6.py
ㅤ            
ㅤ

ㅤㅤДенежная поддержка: https://www.donationalerts.com/r/karmishev415

ㅤ

ВАЖНО: Данная программа создана исключительно в развлекательных целяй, для тестирования оборудования и навыков! 

I--------------------------------------------------------------------------

ENGLISH-АНГЛИЙСКИЙ: Hey! Here I have published my creation - a GovnoSBrowser made in Python! It is as simple as possible (200 lines of code, including missing lines), but with a very cool design. Design: modern and dark, so far this browser is not configurable, but soon I will make a settings menu and integrate everything. The program at this stage may contain errors.

installation: So far, the browser is under development and does not have a direct installation file, so it is installed as a file with the extension.py and runs through a code editor (for example VS Code).

To launch: 

         1. Download the latest version of the program (browserG-PyQt6.py ) because all further actions will be performed in it!

         2. Download and install VS Code [https://code .visualstudio.com/download ] from the official website

         3. Open the downloaded browser file via VS Code and open the terminal there.

         4. Install the necessary packages via the terminal: py -m pip install PyQt6 PyQt6-WebEngine

         5. After the installation is complete, make sure that there are no errors and run the file. browserG-PyQt6.py

If you want to use the browser fully, build the project yourself:

‼️ The PyQt6 library and the PyQt6-WebEngine component are required ↑ ‼️

          1. Install the necessary packages via the terminal: py -m pip install pyinstaller

          2. Open the folder with the program file via VS Code

          3. Enter this into the terminal: python -c "import os, PyQt6.QtWebEngineWidgets as w; print(os.path.join(os.path.dirname(w.__file__), '..', 'Qt6', 'resources'))"

          4.Enter this into the terminal pyinstaller --name=GovnoBrowser --windowed --onefile --add-data "Replace this with the path given by the previous command" browserG-PyQt6.py

          5. The direct installation file will appear in the folder ./dist in the same folder as the file browserG-PyQt6.py
          

IMPORTANT: This program was created exclusively for entertainment purposes, for testing equipment and skills!


