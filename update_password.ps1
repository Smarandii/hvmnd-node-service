echo $newPassword | 'C:\Program Files (x86)\AnyDesk\AnyDesk.exe' --set-password;
>> Start-Sleep -Seconds 1;
>> $serviceName="AnyDesk";
>> if((Get-Service -Name $serviceName).Status -eq "Running")
>> {Restart-Service -Name $serviceName;}