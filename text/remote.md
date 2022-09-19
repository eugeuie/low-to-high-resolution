# Remote Development Tips

## Login into Putty using PowerShell

```
[path to putty.exe] -pw [password] [username]@[IP-address]:[port]
D:\Installers\putty.exe -pw [password] root@176.124.192.129:22
```

## OpenSSH Client in PowerShell

```
ssh [username]@[hostname or IP address] -p [port]
ssh root@176.124.192.129 -p 22
```

## Copy, paste in Ubuntu terminal

Copy: `Ctrl + Shift + C`  
Paste: `Shift + Insert` (insert is tapping the touchpad with two fingers)

## Check RAM info in Ubuntu terminal (size in MB)

```
free -m
```

## Check installed apps in Ubuntu terminal

```
apt list --installed
```

## Run process viewer in Ubuntu

```
htop
```