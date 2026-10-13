# VLC Juxtopposed — Windows x64 preview 1

[Скачать установщик и portable ZIP](https://github.com/dedakraeveda/vlc/releases/tag/juxtopposed-win64-preview-1).

Неофициальная экспериментальная сборка **нативного VLC 4**, не skin и не
веб-обёртка. Основа — `dsojevic/vlc:juxtopposed-redesign`; дизайн Juxtopposed,
CC BY 4.0. Ссылки/лицензии/инструкции: [WINDOWS-REDESIGN.md](WINDOWS-REDESIGN.md).

## Файлы

- `VLC-Juxtopposed-4.0-dev-win64-Setup.exe` — per-user NSIS, **unsigned**.
- `VLC-Juxtopposed-4.0-dev-win64-portable.zip` — полностью распаковать.
- `SHA256SUMS` — хеши обеих поставок.

Установка не заменяет обычный VLC и не меняет ассоциации. Профиль в `portable`.
Деинсталлятор сохраняет созданные пользователем файлы/настройки. Portable
запускать `vlc.exe --no-crashdump`, чтобы не использовать общий crash-handler.

## Проверено на Windows 11 x64

- Реальное H.264-воспроизведение до EOF и exit 0.
- Qt/QML: видимые SVG-иконки, индикатор громкости, Play/Pause, библиотека/Music,
  очередь; настоящий Windows UI, не offscreen/HTML. Close завершает процесс.
- Реальная тихая установка, все **538 файлов** побайтово совпадают с ZIP,
  корректный ярлык/HKCU; воспроизведение установленной копией; удаление с
  сохранением sentinel-файлов. Metadata профиля/основные registry-поля обычного
  VLC не изменились.
- 14 unittest и Python compileall; SHA-256 проверены независимо от runtime.
- Независимое read-only ревью Claude Code (2 круга), открытых визуальных/
  кодовых блокеров базового сценария не найдено.

Compiled source: `41e927845202cf2c6f64a864f2f7037ba336857d`.
[Native CI run](https://github.com/dedakraeveda/vlc/actions/runs/38470541761).
[Проверки и реальные снимки](review/final-verification.md).

## Ограничения

VLC 4 development tree, не официальный стабильный релиз VideoLAN.
Windows 7/ARM64, HiDPI/светлая тема, сеть/DVD/Blu-ray/все кодеки и сохранение
всех параметров отдельно не сертифицированы. Никаких подписывающих ключей нет.

Для устранения подтверждённого loader-lock зависания MinGW frontend после
очистки libVLC/интерфейса и CRT flush завершает **свой** процесс через Windows
TerminateProcess, не выполняя DLL_PROCESS_DETACH. Это не внешнее завершение
при playback; embedded libVLC не затронут. Полнота сторонних global-finalizer
буферов не заявляется. Исходные формы/цвета/иконки сохранены, совместимость
урезанной статической Qt восстановлена локальными backend-компонентами.
