#!/usr/bin/env python3

import json
import logging
import os.path as os_path
from itertools import chain as _chain
from typing import Optional


class NLPSpacy:
    is_initialized: bool = False

    @classmethod
    def initialize(cls, model: str = "en_core_web_trf", exclude: Optional[list[str]] = None) -> None:
        logging.debug("Initializing spaCy...")
        import spacy

        kwargs = {"exclude": exclude} if exclude is not None else {}
        cls.nlp_spacy = spacy.load(model, **kwargs)
        cls.is_initialized = True

    @classmethod
    def _nlp(cls, doc, *, disable: Optional[list[str]] = None):
        # https://spacy.io/usage/processing-pipelines#_title
        if not cls.is_initialized:
            cls.initialize()

        kwargs = {"disable": disable} if disable is not None else {}
        return cls.nlp_spacy(doc, **kwargs)

    @classmethod
    def _pretokenized2doc(cls, text: str):
        if not cls.is_initialized:
            cls.initialize()

        from spacy.tokens import Doc as Doc_spacy

        list_of_words: tuple[list[str], ...] = tuple(line.split() for line in text.split("\n"))
        flatten_words: list[str] = list(_chain.from_iterable(list_of_words))
        sent_starts: list[bool] = [i == 0 for words in list_of_words for i in range(len(words))]
        return Doc_spacy(cls.nlp_spacy.vocab, words=flatten_words, sent_starts=sent_starts)

    @classmethod
    def _json2spacy(cls, json_path: str):
        from spacy.tokens import Doc as Doc_spacy

        if not cls.is_initialized:
            cls.initialize()

        with open(json_path, encoding="utf-8") as f:
            doc_spacy = Doc_spacy(cls.nlp_spacy.vocab).from_json(  # type:ignore
                json.load(f)
            )
        return doc_spacy

    @classmethod
    def _spacy2json(cls, doc_spacy, json_path: str):
        with open(json_path, "w") as f:
            json.dump(doc_spacy.to_json(), f, ensure_ascii=False)

    @classmethod
    def _depparse(cls, text: str, ifile_prefix: str, *, is_pretokenized: bool = False):
        if not is_pretokenized:
            logging.info("Dependency parsing raw text...")
            doc_spacy = cls._nlp(text)
        else:
            doc_spacy = cls._pretokenized2doc(text)
            logging.info("Dependency parsing pretokenized text...")
            doc_spacy = cls._nlp(doc_spacy)

        return doc_spacy

    @classmethod
    def depparse(
        cls,
        text: Optional[str] = None,
        ifile: Optional[str] = None,
        is_pretokenized: bool = False,
    ):
        assert any((text, ifile)), "Neither text nor ifile is valid."
        if ifile is None:
            ifile = "cmdline_text"
        elif text is None:
            with open(ifile, encoding="utf-8") as f:
                text = f.read()

        logging.info(f"Processing {ifile}...")

        ifile_prefix = os_path.splitext(ifile)[0]
        doc_spacy = cls._depparse(text, ifile_prefix, is_pretokenized=is_pretokenized)  # type:ignore
        return doc_spacy

    @classmethod
    def _tokenize(cls, text: str, *, is_pretokenized: bool = False):
        disable = ["ner"]
        if not is_pretokenized:
            logging.info("Tokenizing raw text...")
            doc_spacy = cls._nlp(text, disable=disable)
        else:
            from spacy.tokens import Doc as Doc_spacy

            list_of_words: tuple[list[str], ...] = tuple(line.split() for line in text.split("\n"))
            flatten_words: list[str] = list(_chain.from_iterable(list_of_words))
            sent_starts: list[bool] = [i == 0 for words in list_of_words for i in range(len(words))]
            doc_spacy = Doc_spacy(cls.nlp_spacy.vocab, words=flatten_words, sent_starts=sent_starts)
            logging.info("Tokenizing pretokenized text (that's funny)...")
            doc_spacy = cls._nlp(doc_spacy, disable=disable)
        return doc_spacy

    @classmethod
    def tokenize(
        cls,
        text: Optional[str] = None,
        ifile: Optional[str] = None,
        is_pretokenized: bool = False,
    ):
        assert any((text, ifile)), "Neither text nor ifile is valid."

        if ifile is None:
            ifile = "cmdline_text"
        elif text is None:
            with open(ifile, encoding="utf-8") as f:
                text = f.read()

        logging.info(f"Processing {ifile}...")

        doc_spacy = cls._tokenize(text, is_pretokenized=is_pretokenized)  # type:ignore
        return doc_spacy
