# learn-cli

Лёгкий бесплатный CLI для управления личной базой знаний и трекинга обучения.
Хранит обычные Markdown-файлы в git-репозитории. Объединяет три проверенные методики:

- **Zettelkasten** — атомарные заметки с уникальными ID и явными связями `[[id]]`.
- **CODE** (Capture · Organize · Distill · Express) — конвейер от мысли до результата.
- **PARA** (Projects · Areas · Resources · Archive) — навигация по жизни.

Никаких облаков, БД и платных сервисов. Только локальный диск + git (можно
синхронизировать через любой бесплатный хостинг: GitHub, GitLab, Codeberg).

---

## Требования

- **Python 3.10+** — [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Git** — [https://git-scm.com/downloads](https://git-scm.com/downloads)
- (Опционально) **ripgrep** для быстрого поиска — `winget install BurntSushi.ripgrep`

> На Windows после установки Python убедитесь, что в установщике стояла галочка
> *Add Python to PATH*. Перезапустите терминал.

## Установка

```bash
git clone <this-repo> learn-cli
cd learn-cli
python -m pip install -e .
```

После этого в терминале появится команда `learn`.

Проверка:

```bash
learn --version
learn --help
```

### Windows: если `learn` не найден в PowerShell/cmd

Иногда `learn.exe` ставится в папку Python Scripts, которая не попадает в `PATH`.
Добавьте её один раз в пользовательский `PATH`:

```powershell
$scripts = py -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$current = [Environment]::GetEnvironmentVariable("Path", "User")
if ($current -notlike "*$scripts*") {
  [Environment]::SetEnvironmentVariable("Path", "$current;$scripts", "User")
}
```

Перезапустите терминал и проверьте:

```powershell
learn --version
```

## Быстрый старт

```bash
# 1. Создать хранилище (vault) — например, в D:\Knowledge
learn init D:\Knowledge

# 2. Настроить редактор (по желанию)
learn config set editor.command "code --wait"

# 3. Захватить мысль на лету (CODE: Capture)
learn capture "Узнал что Zettelkasten — система Лумана с атомарными заметками"

# 4. Завести постоянную заметку (Zettelkasten)
learn new "Атомарность заметок" --tag zettelkasten,method

# 5. Связать две заметки в обе стороны
learn link 202605061500 202605061430

# 6. Ежедневная заметка обучения
learn daily

# 7. Раз в день — разобрать inbox (CODE: Organize + PARA)
learn process

# 8. Поднять статус, когда заметка дозрела (CODE: Distill)
learn distill 202605061500

# 9. Найти что готово к "выражению" (CODE: Express)
learn express

# 10. Закоммитить всё в git
learn sync -m "evening study session"
```

## Структура vault

```
<vault>/
├── .git/
├── .learn/config.toml        # настройки vault
├── inbox/                    # CODE: Capture — куда летят сырые мысли
├── zettel/                   # атомарные постоянные заметки (Zettelkasten)
├── daily/                    # ежедневные заметки обучения
├── projects/                 # PARA: активные проекты с дедлайном
├── areas/                    # PARA: сферы ответственности
├── resources/                # PARA: справочные материалы
├── archive/                  # PARA: завершённое / неактуальное
└── templates/                # шаблоны для новых заметок
```

## Формат заметки

```markdown
---
id: "202605061430"
title: "Атомарность заметок"
type: zettel
status: fleeting          # fleeting -> literature -> permanent
created: 2026-05-06T14:30:00+03:00
tags: [zettelkasten, method]
links: ["202605061200"]
source: ""
---

# Атомарность заметок

Одна идея — одна заметка. Если вырастает — разрезать.

## Связи
- [[202605061200]] — почему это важно
```

## Команды

| Метод | Команда | Что делает |
| --- | --- | --- |
| Zettelkasten | `learn new "title"` | новая постоянная заметка с уникальным ID |
| Zettelkasten | `learn link <id1> <id2>` | двусторонняя связь между заметками |
| Zettelkasten | `learn open <id\|query>` | открыть заметку в редакторе |
| CODE | `learn capture "..."` | мгновенно в `inbox/` |
| CODE | `learn process` | интерактивно разобрать inbox |
| CODE | `learn distill <id>` | поднять статус (fleeting -> literature -> permanent) |
| CODE | `learn express` | список заметок, готовых к использованию |
| PARA | `learn para list [cat]` | заметки в категории |
| PARA | `learn para move <id> <cat>` | переместить заметку в категорию PARA |
| PARA | `learn archive <id>` | в `archive/` |
| Прочее | `learn init <path>` | создать vault |
| Прочее | `learn daily` | дневник обучения за сегодня |
| Прочее | `learn search "query"` | full-text поиск (rg при наличии) |
| Прочее | `learn tags` | все теги с подсчётом |
| Прочее | `learn status` | статистика заметок + git status |
| Прочее | `learn sync [-m msg]` | git add + commit + push |
| Прочее | `learn config get/set/show/path` | конфигурация |

Полный справочник: `learn --help`, `learn <команда> --help`.

## Конфигурация

Пользовательский конфиг: `~/.config/learn-cli/config.toml`
(на Windows — `%APPDATA%\learn-cli\config.toml`).

```toml
[vault]
path = "D:/Knowledge"

[editor]
command = "code --wait"

[git]
auto_commit = false
remote = "origin"
```

Переменные окружения (имеют приоритет):

- `LEARN_CLI_VAULT` — путь к vault
- `LEARN_CLI_EDITOR` или `EDITOR` — команда редактора
- `LEARN_CLI_CONFIG_HOME` — переопределить каталог конфига

## Поток работы

```
   мысль / источник
        |
        v
   learn capture                          (CODE: Capture)
        |
        v
   inbox/  ----------- learn process ---> zettel / projects / areas / resources / archive
                                                |                          (CODE: Organize, PARA)
                                                v
                                          learn link              (Zettelkasten: связи)
                                                |
                                                v
                                          learn distill                       (CODE: Distill)
                                                |
                                                v
                                          learn express                       (CODE: Express)
                                                |
                                                v
                                          learn sync                         (git commit + push)
```

## Синхронизация между устройствами

`learn` хранит всё в обычном git-репозитории, поэтому подойдёт любой бесплатный
хостинг:

```bash
cd D:\Knowledge
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
# теперь:
learn sync -m "..."   # автоматически делает push
```

## Тесты

```bash
python -m pip install -e ".[dev]"
pytest
```

## Лицензия

MIT
