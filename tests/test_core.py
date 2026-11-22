import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from modules import db, translator, phrasebook, ai


def test_db_roundtrip(tmp_path):
    p = str(tmp_path / "t.db")
    db.init_db(p)
    db.add("translate", "en", "es", "hello", "hola", path=p)
    db.add("grammar", "en", "en", "i has", "I have", path=p)
    assert len(db.fetch(path=p)) == 2
    assert len(db.fetch("hola", path=p)) == 1
    assert len(db.fetch(kind="grammar", path=p)) == 1
    assert db.stats(path=p)["total"] == 2
    assert "hola" in db.to_csv(db.fetch(path=p))
    db.delete(db.fetch(path=p)[0]["id"], path=p)
    db.clear(path=p)
    assert db.fetch(path=p) == []


def test_detect():
    assert translator.detect_language("Hello, how are you doing today my friend?") == "en"
    assert translator.detect_language("Bonjour, comment allez-vous aujourd'hui mon ami ?") == "fr"


def test_translate_empty_and_same():
    with pytest.raises(translator.TranslationError):
        translator.translate("  ", "en", "es")
    assert translator.translate("hi", "en", "en") == "hi"


def test_chunks():
    assert all(len(c) <= 4500 for c in translator._chunks("a" * 10000 + "\nb\n" + "c" * 4000))


def test_phrasebook():
    assert len(phrasebook.PHRASEBOOK) >= 6


def test_ai_requires_key(monkeypatch):
    monkeypatch.setattr(ai, "get_groq_key", lambda: None)
    with pytest.raises(ai.AIError):
        ai.correct_grammar("x", "English")
