---
title: "Установка LibreOffice"
description: "Как установить LibreOffice для локального просмотра docx-макетов в PrintWizard без передачи данных во внешние сервисы: инструкции для Windows, macOS и Linux."
sidebar:
  order: 12
---

LibreOffice позволяет PrintWizard конвертировать docx-макеты в PDF **локально**, без выгрузки во внешние сервисы. Это альтернатива онлайн-предпросмотру (см. [Офисный документ](/guide/ch-02-11/)) для случаев, когда передача данных в Интернет недопустима.

:::note[Зачем это нужно]
Онлайн-предпросмотр отправляет макет во временное хранилище и отображает его через `view.officeapps.live.com` — для этого нужен Интернет. Локальный просмотр через LibreOffice работает полностью в вашем контуре: файл никуда не уходит.
:::

## Куда устанавливать

Зависит от того, где выполняется конвертация (настраивается в разделе **PrintWizard → Настройки → Конструктор ПФ**):

- **Конвертация на клиенте** — LibreOffice ставится на **рабочую станцию** пользователя, который открывает макеты.
- **Конвертация на сервере** — LibreOffice ставится на **сервер 1С** (машину, где работает сервер приложений).

Полный дистрибутив LibreOffice уже включает всё необходимое (`soffice` в режиме `--headless`) — отдельный «headless»-пакет не требуется.

## Windows

**Вариант 1 — установщик с сайта:** скачайте LibreOffice со [страницы загрузки](https://www.libreoffice.org/download/download-libreoffice/) и запустите `.msi`.

**Вариант 2 — через winget** (Windows 10/11):

```powershell
winget install -e --id TheDocumentFoundation.LibreOffice
```

## macOS

**Вариант 1 — образ с сайта:** скачайте `.dmg` со [страницы загрузки](https://www.libreoffice.org/download/download-libreoffice/), откройте и перетащите LibreOffice в «Программы».

**Вариант 2 — через Homebrew** (если установлен):

```bash
brew install --cask libreoffice
```

## Linux

**Debian / Ubuntu:**

```bash
sudo apt update && sudo apt install libreoffice
```

**Fedora / RHEL / ALT:**

```bash
sudo dnf install libreoffice
```

Либо скачайте `.deb`/`.rpm` со [страницы загрузки](https://www.libreoffice.org/download/download-libreoffice/).

:::tip[Минимальная установка на сервере]
Для серверной конвертации графическая оболочка не нужна — достаточно пакетов ядра и Writer, например `libreoffice-core` и `libreoffice-writer`.
:::

## Проверка установки

Выполните в терминале / командной строке:

```bash
soffice --version
```

Команда должна вывести версию, например `LibreOffice 24.8.3.2`.

:::caution[Windows: soffice не в PATH]
После стандартной установки на Windows `soffice` может быть недоступен по имени. Исполняемый файл лежит в:

```
C:\Program Files\LibreOffice\program\soffice.exe
```

PrintWizard находит его по этому пути автоматически; для ручной проверки версии запускайте `soffice.exe` из указанной папки.
:::

## После установки

Включите нужный вариант в **PrintWizard → Настройки → Конструктор ПФ**:

- **Разрешить конвертацию на клиенте** — если LibreOffice установлен на рабочей станции;
- **Разрешить конвертацию на сервере** — если LibreOffice установлен на сервере 1С.

После этого при открытии docx-макета PrintWizard построит PDF-предпросмотр локально.
