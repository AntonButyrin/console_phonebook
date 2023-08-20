from typing import  Dict, Optional, Union

import pandas as pd


class IDataStorage:
    """
    Интерфейс для работы с хранилищем данных.
    """

    def load(self) -> pd.DataFrame:
        """
        Загружает данные из хранилища.
        Возвращает: DataFrame с данными.
        """
        pass

    def save(self, data: pd.DataFrame) -> None:
        """
        Сохраняет данные в хранилище.
        Параметры: data - DataFrame с данными.
        """
        pass


class CSVDataStorage(IDataStorage):
    """
    Реализация интерфейса IDataStorage для работы с CSV файлами.
    """

    def __init__(self, file_name: str) -> None:
        """
        Конструктор.
        Параметры: file_name - имя файла.
        """

        self.file_name = file_name

    def load(self) -> pd.DataFrame:
        """
        Загружает данные из CSV файла.
        Возвращает: DataFrame с данными.
        """

        try:
            return pd.read_csv(self.file_name)
        except FileNotFoundError:
            return pd.DataFrame(
                columns=[
                    "ID",
                    "Фамилия",
                    "Имя",
                    "Отчество",
                    "Организация",
                    "Рабочий телефон",
                    "Сотовый телефон",
                ]
            )

    def save(self, data: pd.DataFrame) -> None:
        """
        Сохраняет данные в CSV файл.
        Параметры: data - DataFrame с данными.
        """
        data.to_csv(self.file_name, index=False)


class Directory:
    """
    Класс для работы со справочником.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Directory, cls).__new__(cls)
            cls._instance.data_storage = CSVDataStorage("records.csv")
            cls._instance.data = cls._instance.data_storage.load()
            cls._instance.next_id = len(cls._instance.data) + 1
        return cls._instance

    def print_records(self) -> None:
        """
        Печатает все записи.
        """
        print(self.data.to_markdown(index=False))

    def add_record(self, record: Dict[str, str]) -> None:
        """
        Добавляет запись.
        Параметры: record - словарь с данными записи.
        """

        if any(value.strip() == "" for value in record.values()):
            print("Все поля должны быть заполнены. Запись не была добавлена.")
            return

        if not self.validate_phone(
            record["Рабочий телефон"]
        ) or not self.validate_phone(record["Сотовый телефон"]):
            print("Один или оба номера телефонов невалидны. Запись не была добавлена.")
            return

        record_with_id = {"ID": self.next_id, **record}
        new_record_df = pd.DataFrame([record_with_id], columns=self.data.columns)
        self.data = pd.concat([self.data, new_record_df], ignore_index=True)
        self.data_storage.save(self.data)

        self.next_id += 1
        print("Запись успешно добавлена.")

    def validate_phone(self, phone: str) -> bool:
        """
        Проверяет валидность номера телефона.
        Параметры: phone - строка с номером телефона.
        Возвращает: True, если номер валиден, иначе False.
        """
        return phone.isdigit()

    def search_records(self, keyword: str) -> None:
        """
        Поиск записей по ключевому слову.
        Параметры: keyword - ключевое слово для поиска.
        """

        result = self.data[
            self.data.apply(
                lambda row: row.astype(str).str.contains(keyword).any(), axis=1
            )
        ]
        print(result.to_markdown(index=False))

    def edit_record(self, record_id: int) -> None:
        """
        Редактирует запись по ID.
        Параметры: record_id - ID записи.
        """

        index = self.data[self.data["ID"] == record_id].index
        if len(index) == 0:
            print("Запись с таким ID не найдена.")
            return

        index = index[0]
        print("Текущая запись:")
        print(self.data.loc[index].to_markdown())

        record = {
            col: input(f"{col} (оставьте пустым, чтобы не менять): ")
            for col in self.data.columns
            if col != "ID"
        }
        for key, value in record.items():
            if value != "":
                if key in [
                    "Рабочий телефон",
                    "Сотовый телефон",
                ] and not self.validate_phone(value):
                    print(f"{key} невалиден. Изменения не сохранены.")
                    return
                self.data.at[index, key] = value

        self.data_storage.save(self.data)
        print("Запись успешно обновлена.")


def main() -> None:
    """
    Основная функция для интерактивной работы с справочником.
    """

    directory = Directory()
    while True:
        choice = input(
            "1. Просмотреть записи\n2. Добавить запись\n3. Поиск записи\n4. Редактировать запись\n5. Выйти\nВаш выбор: "
        )
        if choice == "1":
            directory.print_records()
        elif choice == "2":
            record = {
                col: input(f"{col}: ") for col in directory.data.columns if col != "ID"
            }
            directory.add_record(record)
        elif choice == "3":
            keyword = input("Поиск по ключевому слову: ")
            directory.search_records(keyword)
        elif choice == "4":
            index = int(input("Введите ID записи для редактирования: "))
            directory.edit_record(index)
        elif choice == "5":
            break
        else:
            print("Неизвестный выбор")


if __name__ == "__main__":
    main()
