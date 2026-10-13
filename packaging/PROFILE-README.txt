VLC Juxtopposed isolated profile

The existence of this 'portable' folder makes VLC use it for configuration,
cache and media-library storage (native src/win32/dirs.c behavior). This keeps
this unofficial development build separate from an existing VLC installation.

The uninstaller removes only files that were included in the installer. Your
preferences, media-library database and any other files created later are kept.
Do not copy an existing VLC profile here unless you deliberately want to migrate it.
