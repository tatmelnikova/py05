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

    def get_proc_count(self) -> int:
        return self._counter

    def get_current_count(self) -> int:
        return len(self._storage)


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


class DataStream:
    def __init__(self) -> None:
        self._processors: list[DataProcessor] = list()

    def register_processor(self, proc: DataProcessor) -> None:
        self._processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        for item in stream:
            ingested = False
            for processor in self._processors:
                if (processor.validate(item)):
                    processor.ingest(item)
                    ingested = True
            if not ingested:
                print("DataStream error - Can't process element in stream: " +
                      str(item))

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if len(self._processors):
            for proc in self._processors:
                print(f"{proc.__class__.__name__}:" +
                      f"total {proc.get_proc_count()}" +
                      f", remaining {proc.get_current_count()} on processor")
        else:
            print("No processor found, no data")


def get_stream_data() -> list[Any]:
    return [
        "Hello world",
        [3.14, -1, 2.71],
        [
            {"log_level": "WARNING", "log_message": "Telnet access!" +
             " Use ssh instead"},
            {"log_level": "INFO", "log_message": "User wil isconnected"},
        ],
        42,
        ["Hi", "five"],
    ]


def main() -> None:
    print("=== Code Nexus - Data Stream ===")
    try:
        print("Initialize Data Stream...")
        stream = DataStream()
        stream.print_processors_stats()
        print()
        np = NumericProcessor()
        lp = LogProcessor()
        tp = TextProcessor()
        stream_list: list[Any] = get_stream_data()
        print("Registering Numeric Processor")
        stream.register_processor(np)
        print()
        print("Send first batch of data on stream:", stream_list)
        stream.process_stream(stream_list)
        print()
        stream.print_processors_stats()
        print()
        print("Registering other data processors")
        stream.register_processor(tp)
        stream.register_processor(lp)
        print("Send the same batch again")
        stream.process_stream(stream_list)
        print()
        stream.print_processors_stats()
        print()
        print("Consume some elements from the data processors:" +
              "Numeric 3, Text 2, Log 1")
        for _ in range(3):
            np.output()
        for _ in range(2):
            tp.output()
        lp.output()
        stream.print_processors_stats()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
