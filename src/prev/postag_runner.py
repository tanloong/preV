#!/usr/bin/env python3

from typing import List

from .util import PrevProcedureResult


class PosTagRunner:
    def __init__(
        self,
        is_stdout: bool,
        is_pretokenized: bool,
        n_process: int = 3,
    ) -> None:
        self.is_stdout = is_stdout
        self.is_pretokenized = is_pretokenized

    def run_on_file(self, ifile: str) -> PrevProcedureResult:
        pass

    def run_on_file_list(self, ifiles: List[str]) -> PrevProcedureResult:
        pass

    def interact(self) -> PrevProcedureResult:
        pass
