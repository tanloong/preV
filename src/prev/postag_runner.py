#!/usr/bin/env python3

import logging
import os.path as os_path
import sys
from typing import Callable, List

from .nlp import NLP_Spacy
from .util import Prev_Procedure_Result


class PosTag_Runner:
    def __init__(
        self,
        is_stdout: bool,
        is_pretokenized: bool,
        n_process: int = 3,
    ) -> None:
        self.is_stdout = is_stdout
        self.is_pretokenized = is_pretokenized

    def run_on_file(self, ifile: str) -> Prev_Procedure_Result:
        pass

    def run_on_file_list(self, ifiles: List[str]) -> Prev_Procedure_Result:
        pass

    def interact(self) -> Prev_Procedure_Result:
        pass
