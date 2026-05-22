#!/usr/bin/env python3


from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    _storage: list[tuple[int, str]] = list()
    _counter: int = 0

    @abstractmethod
    def validate(self,  data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if len(self._storage):
            return self._storage.pop(0)
        else:
            raise Exception("No data for pop")


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        is_str = isinstance(data, str)
        is_list = isinstance(data, list)
        is_str_list = False
        if is_list:
            is_str_list = all(isinstance(x, str) for x in data)
        return is_str or is_str_list

    def ingest(self, data: str | list[str]) -> None:
        if self.validate(data):
            self._storage.append((self._counter, str(data)))
            self._counter += 1
        else:
            raise Exception("Improper text data")


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        is_dict = self.is_str_dict(data)
        is_list = self.is_list_of_str_dicts(data)
        return is_dict or is_list

    def is_list_of_str_dicts(self, data: Any) -> bool:
        return (
            isinstance(data, list)
            and all(self.is_str_dict(item) for item in data)
        )

    def is_str_dict(self, data: Any) -> bool:
        is_dict = isinstance(data, dict)
        return (
            is_dict
            and all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in data.items()
            )
        )

    def ingest(self, data: list[dict[str, str]] | dict[str, str]) -> None:
        if self.validate(data):
            self._storage.append((self._counter, str(data)))
            self._counter += 1
        else:
            raise Exception("Improper log data")


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        is_int = isinstance(data, int)
        is_float = isinstance(data, float)
        is_list = isinstance(data, list)
        is_num_list = False
        if is_list:
            is_num_list = all(isinstance(item, (int, float)) for item in data)
        return is_int or is_float or is_num_list

    def ingest(self, data: int | float | list[int | float]) -> None:
        if self.validate(data):
            self._storage.append((self._counter, str(data)))
            self._counter += 1
        else:
            raise Exception("Improper numeric data")


def main() -> None:
    np = NumericProcessor()
    lp = LogProcessor()
    tp = TextProcessor()
    try:
        print("Validate int:", np.validate(5))
        print("Validate float:", np.validate(2.1))
        print("Validate list of ints and floats:", np.validate([1, 0, 2.5]))
        print("Validate string:", np.validate("abc"))
        print("Validate list of int and str:", np.validate(["1", "abc"]))
        print("Validate None:", np.validate(None))
        print("========================================================")
        list_of_dicts = [{'log_level': 'NOTICE',
                         'log_message': 'Connection to server'},
                         {'log_level': 'ERROR',
                          'log_message': 'Unauthorized access!!'}]
        str_dict = {'log_level': 'NOTICE',
                    'log_message': 'Connection to server'}
        hello = "Hello"
        print("Validate log list_of_dicts", lp.validate(list_of_dicts))
        print("Validate str_dict", lp.validate(str_dict))
        print("Validate log hello", lp.validate(hello))
        np.ingest("abc")  # type: ignore[arg-type]
        print("=========================================================")
        print("Validate text 42", tp.validate(42))
        str_list = ['Hello', 'Nexus', 'World']
        print("Validate text list", tp.validate(str_list))
        tp.ingest(str_list)
        tp.output()
        tp.output()
    except Exception as e:
        print("Got exception:", e)
    np.ingest(1)
    np.ingest(0.5)
    np.ingest([1, 2, 3, 4])
    try:
        print(np.output())
        print(np.output())
        print(np.output())
        print(np.output())
    except Exception as e:
        print("Got exception in output", e)

    print()


if __name__ == "__main__":
    main()
