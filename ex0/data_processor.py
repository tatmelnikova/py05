#!/usr/bin/env python3


from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._counter = 0
        self._storage: list[tuple[int, str]] = list()

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
            if isinstance(data, list):
                for item in data:
                    self._storage.append((self._counter, str(item)))
                    self._counter += 1
            else:
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
            if isinstance(data, list):
                for item in data:
                    str_val = ": ".join(f"{v}" for v in item.values())
                    self._storage.append((self._counter, str_val))
                    self._counter += 1
            else:
                str_val = ": ".join(f"{v}" for v in data.values())
                self._storage.append((self._counter, str_val))
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
            if isinstance(data, list):
                for item in data:
                    self._storage.append((self._counter, str(item)))
                    self._counter += 1
            else:
                self._storage.append((self._counter, str(data)))
                self._counter += 1
        else:
            raise Exception("Improper numeric data")


def test_numeric() -> None:
    print("Testing Numeric Processor...")
    np = NumericProcessor()
    try:
        print("Trying to validate input '42':", np.validate(42))
        print("Trying to validate input 'Hello':", np.validate('Hello'))
        print("Test invalid ingestion of string" +
              "'foo' without prior validation:")
        np.ingest('foo')  # type: ignore[arg-type]
    except Exception as e:
        print("Got exception:", e)
    try:
        num_list: list[int | float] = [1, 2, 3, 4, 5]
        print(f"Processing data: {num_list}")
        np.ingest(num_list)
        print("Extracting 3 values...")
        for x in range(3):
            out = np.output()
            print(f"Numeric value {out[0]}: {out[1]}")
    except Exception as e:
        print("Got exception processing list", e)


def test_text() -> None:
    print("Testing Text Processor...")
    tp = TextProcessor()
    try:
        print("Trying to validate input '42':", tp.validate(42))
        str_list = ['Hello', 'Nexus', 'World']
        print(f"Processing data: {str_list}")
        tp.ingest(str_list)
        print("Exctracting 1 value...")
        out = tp.output()
        print(f"Text value {out[0]}: {out[1]}")
    except Exception as e:
        print("Got exception in TextProcessor", e)


def test_log() -> None:
    print("Testing Log Processor...")
    lp = LogProcessor()
    try:
        print("Trying to validate input 'Hello':", lp.validate('Hello'))
        list_of_dicts = [{'log_level': 'NOTICE',
                         'log_message': 'Connection to server'},
                         {'log_level': 'ERROR',
                         'log_message': 'Unauthorized access!!'}]
        print("Processing data:", list_of_dicts)
        lp.ingest(list_of_dicts)
        print("Extracting 2 values...")
        for x in range(2):
            out = lp.output()
            print(f"Log entry {out[0]}: {out[1]}")
    except Exception as e:
        print("Got exception in LogProcessor", e)


def main() -> None:
    print("=== Code Nexus - Data Processor ===")
    print()
    test_numeric()
    print()
    test_text()
    print()
    test_log()


if __name__ == "__main__":
    main()
