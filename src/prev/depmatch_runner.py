#!/usr/bin/env python3

import logging
import os
import os.path as os_path
import sys
from typing import List, Literal, Optional

from .nlp import NLPSpacy
from .querier import Querier
from .util import PrevProcedureResult


class DepmatchRunner:
    def __init__(
        self,
        is_pretokenized: bool,
        is_no_query: bool,
        is_visualize: bool,
        is_stdout: bool,
        print_what: str,
        n_process: int = 3,
        pattern_file: Optional[str] = None,
        newline_break: Literal["never", "always", "two"] = "never",
    ) -> None:
        self.is_pretokenized = is_pretokenized
        self.is_no_query = is_no_query
        self.is_visualize = is_visualize
        self.is_stdout = is_stdout
        self.print_what = print_what
        self.newline_break = newline_break

        self.querier = Querier(n_process, pattern_file)

    def draw_tree(self, sent_spacy, ifile: str) -> None:
        from spacy import displacy

        trees_dir = ifile.replace(".tokenized", "").replace(".txt", "") + "_trees"
        svg_file = (
            trees_dir
            + os_path.sep
            + "-".join([w.text for w in sent_spacy if (w.is_alpha or w.is_digit)])[:100]
            + ".svg"
        )
        logging.info(f"Visualizing: {sent_spacy.text}")
        svg = displacy.render(sent_spacy)
        if not os_path.exists(trees_dir):
            os.makedirs(trees_dir)
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg)

    def run_on_text(self, text: str, ifile="cmdline_text", ofile=None) -> PrevProcedureResult:
        match self.newline_break:
            case "never":
                doc_spacy = NLPSpacy.depparse(text, ifile, is_pretokenized=self.is_pretokenized)
            case "always":
                from spacy.tokens import Doc

                doc_spacy = Doc.from_docs(
                    [
                        NLPSpacy.depparse(line, f"{ifile}_{i}", is_pretokenized=self.is_pretokenized)
                        for i, line in enumerate(text.split("\n"), 1)
                        if line.strip()
                    ]
                )
            case "two":
                import re

                from spacy.tokens import Doc

                doc_spacy = Doc.from_docs(
                    [
                        NLPSpacy.depparse(para, f"{ifile}_{i}", is_pretokenized=self.is_pretokenized)
                        for i, para in enumerate(re.split(r"(?:\r\n|\n|\r){2,}", text), 1)
                        if para.strip()
                    ]
                )
            case _ as unknown:
                raise ValueError(f"Unexpected newline_break value: {unknown}. Expect never, always, or two")
        if self.is_visualize:
            for sent in doc_spacy.sents:
                self.draw_tree(sent, ifile)
        if not self.is_no_query:
            try:
                result = self.querier.match(doc_spacy, self.print_what)
            except KeyboardInterrupt:
                return False, "KeyboardInterrupt"

            if not self.is_stdout:
                if ofile is None:
                    ofile = f"cmdline_text.{self.print_what}"
                with open(ofile, "w", encoding="utf-8") as f:
                    f.write(result)
                logging.info(f"Written to {ofile}.")
            else:
                sys.stdout.write(result)
        return True, None

    def run_on_file(self, ifile: str) -> PrevProcedureResult:
        dir_name, file_name = os_path.split(ifile)
        name, _ = os_path.splitext(file_name)
        ofile = os_path.join(dir_name, name + f"_{self.print_what}.txt")

        logging.info(f"Matching against {ifile}...")
        with open(ifile, encoding="utf-8") as f:
            text = f.read()
        return self.run_on_text(text, ifile, ofile)

    def run_on_file_list(self, ifiles: List[str]) -> PrevProcedureResult:
        i = 1
        total = len(ifiles)
        for ifile in ifiles:
            logging.info(f"Depparsing {ifile}...({i}/{total})")
            self.run_on_file(ifile)
            i += 1

        logging.info("Done.")
        return True, None

    def prepare_interact(self):
        self.is_stdout = True
        self.is_no_query = False
