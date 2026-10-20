[Setup]
AppId={{D37F2188-5F59-4E15-9CB8-E0B19D5A0231}
AppName=PUSTASUB
AppVersion=1.1.0
AppPublisher=Universitas Terbuka
AppPublisherURL=https://www.ut.ac.id
AppSupportURL=https://www.ut.ac.id
AppUpdatesURL=https://www.ut.ac.id
DefaultDirName={autopf}\PUSTASUB
DefaultGroupName=PUSTASUB
AllowNoIcons=yes
OutputDir=..\dist
OutputBaseFilename=PUSTASUB-v1.1.0-Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\PUSTASUB\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PUSTASUB"; Filename: "{app}\PUSTASUB.vbs"; WorkingDir: "{app}"
Name: "{group}\PUSTASUB (Console Mode)"; Filename: "{app}\run.bat"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,PUSTASUB}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\PUSTASUB"; Filename: "{app}\PUSTASUB.vbs"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\PUSTASUB.vbs"; Description: "{cm:LaunchProgram,PUSTASUB}"; Flags: shellexec postinstall nowait skipifsilent
