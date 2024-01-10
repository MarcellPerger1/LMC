from __future__ import annotations


class Data:
    def __init__(self, data: int):
        self.data = data

    __match_args__ = ('data',)
