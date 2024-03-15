# update_password.ps1
$newPassword = Get-Content "C:\Program Files (x86)\AnyDesk\file.txt"
& 'C:\Program Files (x86)\AnyDesk\AnyDesk.exe' --remove-password
& 'C:\Program Files (x86)\AnyDesk\AnyDesk.exe' --set-password $newPassword
