import pytest
from winamax.utilidades import media


def test_media_valores_conocidos():
    assert media([1, 2, 3]) == 2


def test_media_lista_vacia():
    with pytest.raises(ValueError):
        media([])