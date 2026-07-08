#!/usr/bin/env bash
# Старт-скрипт Keenetic VPN бота.
#
# Что делает:
#   1. Проверяет, что есть подходящий Python (3.10+).
#   2. Создаёт виртуальное окружение ./venv, если его ещё нет.
#   3. Активирует venv.
#   4. Устанавливает/обновляет зависимости из requirements.txt — но только
#      если файл изменился с прошлого запуска (хэш сравнивается с
#      venv/.requirements.hash), чтобы не тратить время на pip при каждом
#      перезапуске без изменений.
#   5. Накатывает миграции БД через `alembic upgrade head` (создаёт bot.db,
#      если его ещё нет, либо доводит схему до актуальной версии).
#   6. Запускает telegrambot.py.
#
# Использование:
#   ./start.sh            — обычный запуск
#   ./start.sh --check    — только проверить зависимости/окружение, не запускать
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[ok]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
fail()  { echo -e "${RED}[ошибка]${NC} $1"; exit 1; }

CHECK_ONLY=false
if [[ "${1:-}" == "--check" ]]; then
  CHECK_ONLY=true
fi

# ---------- 1. Проверка Python ----------
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON_BIN="$candidate"
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  fail "Python 3 не найден. Установите Python 3.10 или новее (например: sudo apt install python3 python3-venv)."
fi

PY_VERSION=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]]; then
  fail "Найден Python $PY_VERSION, но нужен 3.10+. Установите более новую версию."
fi
info "Python $PY_VERSION ($PYTHON_BIN)"

# ---------- 2. venv ----------
if [[ ! -d venv ]]; then
  info "Создаю виртуальное окружение в ./venv..."
  "$PYTHON_BIN" -m venv venv || fail "Не удалось создать venv. На Debian/Ubuntu может потребоваться: sudo apt install python3-venv"
else
  info "Виртуальное окружение venv уже есть"
fi

# shellcheck disable=SC1091
if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
elif [[ -f venv/Scripts/activate ]]; then
  source venv/Scripts/activate
else
  fail "Не найден скрипт активации venv (venv/bin/activate или venv/Scripts/activate)."
fi

# ---------- 3. Зависимости ----------
HASH_FILE="venv/.requirements.hash"
if command -v sha256sum >/dev/null 2>&1; then
  CURRENT_HASH=$(sha256sum requirements.txt | awk '{print $1}')
else
  CURRENT_HASH=$(shasum -a 256 requirements.txt | awk '{print $1}')
fi
STORED_HASH=""
[[ -f "$HASH_FILE" ]] && STORED_HASH=$(cat "$HASH_FILE")

if [[ "$CURRENT_HASH" != "$STORED_HASH" ]]; then
  info "Устанавливаю/обновляю зависимости из requirements.txt..."
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet || fail "Не удалось установить зависимости. Смотрите вывод pip выше."
  echo "$CURRENT_HASH" > "$HASH_FILE"
  info "Зависимости установлены"
else
  info "Зависимости уже актуальны (requirements.txt не менялся)"
fi

# Точечная проверка, что критичные пакеты реально импортируются — если
# venv был создан вручную или после сбоя установки, лучше явно сказать,
# чего не хватает, чем упасть с длинным traceback при запуске telegrambot.py.
IMPORT_ERR_FILE="$(mktemp)"
if python -c "import telebot, requests, dotenv, socks, alembic, sqlalchemy" 2>"$IMPORT_ERR_FILE"; then
  info "Все ключевые зависимости импортируются успешно"
else
  warn "Часть зависимостей не импортируется, переустанавливаю requirements.txt..."
  pip install -r requirements.txt --quiet --force-reinstall || fail "$(cat "$IMPORT_ERR_FILE")"
  echo "$CURRENT_HASH" > "$HASH_FILE"
fi
rm -f "$IMPORT_ERR_FILE"

# ---------- 4. .env ----------
if [[ ! -f .env ]]; then
  cp .env.example .env
  warn ".env не найден — создан из .env.example."
  warn "Откройте .env и заполните: BOT_TOKEN"
  exit 1
fi

if grep -q '^BOT_TOKEN=123456789:AAAA-your-bot-token-from-BotFather$' .env; then
  fail "В .env не задан BOT_TOKEN. Получите токен у @BotFather в Telegram и впишите его в .env."
fi

info ".env найден и содержит BOT_TOKEN"

# ---------- 5. Миграции БД ----------
info "Накатываю миграции БД (alembic upgrade head)..."
alembic upgrade head || fail "Не удалось применить миграции. Смотрите вывод alembic выше."
info "БД готова (bot.db)"

if $CHECK_ONLY; then
  info "Проверка окружения завершена (--check). Для запуска используйте ./start.sh без флага."
  exit 0
fi

# ---------- 6. Запуск ----------
info "Запускаю telegrambot.py..."
exec python telegrambot.py
