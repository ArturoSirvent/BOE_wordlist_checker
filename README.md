# BOE_wordlist_checker
I made this small code for looking automatically search words in a list (like: scholarships...) on the BOE.
Using UBUNTU is possible to automatically run a command in the shell when the system starts up. In this way it writes a report about what it has found and pops up a notification. However there're other ways such as `/etc/rc.local`, `/home/user/.bashrc`, or even cron.

The file structure from where it reads may not be clear...sorry about that.  

Main Folder  
|  
|_ BOE Folder   
|_ wordlist  
|_ python_script.py  


Note: This can be easily interpolated to other daily-uploaded file by simply changing the URL, but if it is not workdays-daily, you may have some trouble with the days and the set up for the dowload.
