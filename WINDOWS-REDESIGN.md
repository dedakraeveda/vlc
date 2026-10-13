# VLC Juxtopposed — Windows x64

Неофициальный preview нативного VLC 4 с Qt/QML-редизайном Juxtopposed.
Это не Electron-обёртка и не skin для VLC 3. Основная цель — Windows 11 x64;
Windows 7, ARM64, DVD/Blu-ray, сетевые потоки и все разновидности кодеков
отдельно не проверялись. Не заменяет стабильный официальный VLC.

- Fork: https://github.com/dedakraeveda/vlc/tree/juxtopposed-redesign
- Upstream: https://github.com/dsojevic/vlc/tree/juxtopposed-redesign
- Исходная ревизия: `43283e42a811e8b87ac95420eecd8947f60eb4a2`
- Дизайн: Juxtopposed, **CC BY 4.0**; изменения реализации описаны ниже.
- Видео: https://www.youtube.com/watch?v=ERFeOgqk324
- Figma: https://www.figma.com/community/file/1691465999134370980/vlc-redesign
- Код VLC: GPLv2-or-later, libVLC: LGPLv2-or-later; некоторые зависимости
  делают конкретную сборку де-факто GPLv3. `COPYING`, `COPYING.LIB`, исходный
  `README.md` и сведения о runtime GCC сохраняются.

## Пользователю

Установщик `VLC-Juxtopposed-4.0-dev-win64-Setup.exe` устанавливает приложение
для текущего пользователя в `%LOCALAPPDATA%\Programs\VLC Juxtopposed`.
Путь можно изменить в мастере. Ярлык — **VLC Juxtopposed** в меню «Пуск».
Права администратора не запрашиваются; обычный VLC, его ключи реестра и
ассоциации файлов не заменяются. Установщик **не подписан**.

Настройки и медиатека изолированы в `portable` рядом с `vlc.exe`.
Ярлык явно выбирает этот профиль и отключает upstream crash-handler,
который иначе использует общий `%APPDATA%\vlc\crashdump`.
Для portable ZIP распакуйте **всю папку**, а не только EXE, и запускайте:

```text
vlc.exe --no-crashdump
```

`--no-crashdump` важен для полной изоляции диагностических дампов.
Не удаляйте папку `portable`: её наличие переключает штатный механизм
путей VLC. Не запускайте из ZIP без распаковки. На этой машине проектный
`launch.py` также отключает общий crash-handler.

Удаление приложения удаляет только файлы поставки и его собственный ярлык/
регистрацию. Созданные после установки настройки, медиатека и посторонние
файлы сохраняются: оставшийся каталог может требовать ручного удаления.
Сетевое разрешение брандмауэра не выдаётся автоматически.

## Воспроизводимая сборка

Основной путь — GitHub Actions **Windows x64 redesign** на ветке
`juxtopposed-redesign`, workflow `.github/workflows/windows-redesign.yml`.
После успешного run скачайте `vlc-juxtopposed-win64`.

Используется pinned upstream image
`registry.videolan.org/vlc-debian-win64-posix:20260611225331`, официальный
`extras/package/win32/build.sh`, prebuilt contribs по SHA из дерева и
MinGW-w64 x64. Затем `packaging/finish-build.sh` добавляет runtime **того же
компилятора**, лицензии, профиль и создаёт отдельный безопасный per-user
NSIS-установщик и portable ZIP. Профиль пользователя не включается в пакет.

```text
python agent_cli.py capabilities --json
python agent_cli.py status --json
python agent_cli.py preflight --json
python agent_cli.py plan --json
python agent_cli.py apply --authorized --json
python agent_cli.py verify --json
```

`apply` запускает CI, но **не доказывает** готовность. Он блокирует
неверную GitHub identity, грязное дерево и параллельную сборку; submission
нельзя слепо повторять после timeout. `verify` проверяет SHA-256 артефактов,
но runtime проверяется отдельно. GitHub CLI должен быть авторизован владельцем.

Локальный альтернативный путь: `bash build-local.sh` внутри Linux/WSL с
Docker. На машине автора Ubuntu VHDX находится на D:, образы/сборки тоже там.
Локальная полная сборка не была завершена: использовался CI. Образ около
2.4 GB compressed; нужно ориентировочно 25–40 GB свободного места с запасом
на распаковку, contribs, компиляцию и временные файлы. Проверяйте физическое
расположение VHDX; не переносите сборку/кэши на системный C:.

Повторно упаковать неизменённый готовый payload можно на Linux с NSIS:

```sh
python3 packaging/build_installer.py --payload <payload> --output <new-Setup.exe> --work <scratch>
python3 packaging/portable_archive.py --payload <payload> --output <new-portable.zip>
sha256sum <new-Setup.exe> <new-portable.zip>
```

Выходные файлы не перезаписываются. `portable` упаковывается только с
`README.txt`; созданные при запуске настройки/базы не экспортируются.

## Исправления совместимости без замены дизайна

- Controls импортируются как `QtQuick.Controls.Basic`: generic plugin
  отсутствует в статической Qt-поставке VLC.
- Qt Labs FolderListModel заменён на `RedesignFolderModel` с QDir,
  QFileSystemWatcher и теми же ролями/get/count.
- Qt Quick Canvas отключён в contribs: форма, градиент и заполнение индикатора
  громкости воспроизводятся через SVG с сохранением исходных цветов.
- `data:` изображения требуют `qml_network`, отключённого в Qt VLC.
  Иконки/индикатор обслуживаются локальным `RedesignSvgImageProvider`
  через существующий native SVG handler, без сети и без замены SVG-путей.
- Загрузка plugin DLL учитывает runtime из **каталога EXE и System32**,
  не CWD/PATH. GCC DLL взяты из того же CI-компилятора.

## Приёмочные проверки

Живые результаты и точные ревизии: `TASK-STATE.md`. Успех компиляции сам
по себе не является успехом GUI. Проверки выполняются на настоящей Windows:

```text
python -m unittest discover -s packaging -p "test_*.py" -v
python verify_runtime.py
python verify_runtime.py --gui
python verify_runtime.py --visible
python verify_installer.py --authorized
```

Нужны Python, pywin32 для проверки `.lnk` и реальное тестовое H.264-видео
`smoke/test-video.mp4`. Его можно создать с установленным FFmpeg:

```text
ffmpeg -f lavfi -i testsrc2=size=640x360:rate=24 -t 4 -an -c:v libx264 -pix_fmt yuv420p smoke/test-video.mp4
```

Ожидаются: EOF/exit0 без ошибок plugin/QML, реальное окно с иконками и
работающей навигацией, нормальное завершение Qt. Installer smoke сравнивает
все файлы поставки, target/arguments/working-directory ярлыка, собственные
HKCU-ключи, сохранение пользовательских файлов при удалении и неизменность
metadata профиля/основных registry-полей обычного VLC.

Smoke-каталог установки — строго `D:\projects\temp\vlc-juxtopposed-installer-smoke`;
если он или регистрация/ярлык уже существуют, тест отказывается их заменять.
TEMP/TMP smoke-процессов направлены на D:. Ни существующие пользовательские
профили, ни другие приложения не очищаются. GUI проверяется native UIA/
оконным снимком, а не Playwright/offscreen: у приложения нет браузерного DOM.

## Откат

Source-изменения доступны как Git commits поверх оригинальной ветки.
Установленную отдельную сборку удаляйте её собственным деинсталлятором.
Не удаляйте обычный VLC и не мигрируйте профиль автоматически. Очищать
разрешается только доказанно созданные этой задачей временные файлы после
закрытия их процессов. Локальные dashboard/WSL настройки не переносятся
между устройствами автоматически.
