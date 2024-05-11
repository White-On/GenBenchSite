import pytest

from pathlib import Path
import genbenchsite.src.ranking as ranking
import numpy as np

# @pytest.mark.parametrize("element_to_rank,expected_rank", [([52.2, 42.1, 39.4],1),([45.2, 12.0, 80.2],2),([34.7, 15.8, 2.42],0)], ids=[f"test_{i}" for i in range(3)])
# def test_lex_max(element_to_rank,expected_rank):
#     assert ranking.LexMax(element_to_rank) == expected_rank

# def test_wrong_input():
#     with pytest.raises(ValueError):
#         print(ranking.LexMax({'a': [1,2], 'b': [2], 'c': [3]}))