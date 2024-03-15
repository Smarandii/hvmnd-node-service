# update_password.ps1
$newPassword = Get-Content "C:\Program Files (x86)\AnyDesk\file.txt"
& 'C:\Program Files (x86)\AnyDesk\AnyDesk.exe' --remove-password _unattended_access
& echo $newPassword | 'C:\Program Files (x86)\AnyDesk\AnyDesk.exe' --set-password _unattended_access