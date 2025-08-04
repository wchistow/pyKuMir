#!/bin/bash
check_python_version() {
  py_v=$(python -c "import sys; print('OK' if sys.version_info >= (3, 10) else '')") || exit 1
  if [[ "$py_v" != "OK" ]]; then
    echo "Версия Python должна быть >= 3.10"
    exit 1
  fi
}

install_dependencies() {
  if which apt > /dev/null 2>&1; then
    sudo apt install qt6-base-dev python3-pyqt6 python3-pygments || exit 1
  elif which dnf > /dev/null 2>&1; then
    sudo dnf install qt6-qtbase-devel python3-pyqt6 python3-pygments || exit 1
  elif which pacman > /dev/null 2>&1; then
    sudo pacman -S qt6-base python-pyqt6 python-pygments || exit 1
  else
    echo "Извините, ваш дистрибутив пока не поддерживается"
    exit 1
  fi
}

clear_old() {
  if [[ -e /usr/lib/pykumir ]]; then
    sudo rm -r /usr/lib/pykumir
  fi
  if [[ -e /usr/bin/pykumir ]]; then
    sudo rm /usr/bin/pykumir
  fi
  if [[ -e /usr/share/applications/pykumir.desktop ]]; then
    sudo rm /usr/share/applications/pykumir.desktop
  fi
}

copy_code() {
  sudo mkdir /usr/lib/pykumir || exit 1
  sudo cp -r ./src /usr/lib/pykumir || exit 1
  sudo cp -r ./docs /usr/lib/pykumir || exit 1
}

copy_launcher() {
  sudo cp ./linux/pykumir /usr/bin/ || exit 1
  sudo chmod +x /usr/bin/pykumir || exit 1
}

copy_desktop() {
  sudo cp ./linux/pykumir.desktop /usr/share/applications/ || exit 1
  sudo chmod +x /usr/share/applications/pykumir.desktop || exit 1
}

copy_mime() {
  sudo cp ./linux/pykumir-mimetypes.xml /usr/share/mime/packages/ || exit 1
  sudo chmod +x /usr/share/mime/packages/pykumir-mimetypes.xml || exit 1
}

printf "Проверка версии Python... "
check_python_version
echo OK

echo "Установка зависимостей..."
install_dependencies
echo OK

printf "Копирование исходного кода... "
clear_old
copy_code
echo OK

printf "Копирование лаунчера... "
copy_launcher
echo OK

printf "Копирование файла .desktop... "
copy_desktop
echo OK

printf "Создание типа файла... "
copy_mime
echo OK

echo "Установка успешно завершена"
