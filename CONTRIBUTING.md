# Руководство для разработчиков

## Установка зависимостей:

```sh
uv sync
```

## Запуск тестов:

```sh
pytest tests/
```

## Структура исходного кода:

```
src/
    interface/
        *код интерфейса*
    interpreter/
        *код интерпертатора*
    cli.py
    main.py
    metadata.py
```

## Структура тестов:

```
tests/
    test_parser/
        *тесты парсера*
    test_vm/
        mocks/
            *заглушки*
        *тесты виртуальной машины*
```

## Установка:

```sh
chmod +x ./linux/install.sh
./linux/install.sh
```
