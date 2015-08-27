import pytest

from utilery import core
from utilery.models import Layer, Recipe
from .utils import copy


def pytest_configure(config):
    core.app.config['DATABASE'] = ':memory:'
    core.app.config['TESTING'] = True
    core.app.config['RECIPES'] = []
    core.RECIPES['default'] = Recipe({
        'name': 'default',
        'layers': [{
            'name': 'mylayer',
            'queries': [
                {
                    'sql': 'SELECT geometry AS way, type, name FROM osm_landusages_gen0',  # noqa
                    'maxzoom': 9
                }
            ]
        }]
    })


@pytest.fixture
def fetchall(monkeypatch):

    def _(result, check=None):
        def func(*args, **kwargs):
            if check:
                check(*args, **kwargs)
            return result
        monkeypatch.setattr('utilery.core.DB.fetchall', func)

    return _


@pytest.fixture
def app():
    return core.app


class MonkeyPatchWrapper(object):
    def __init__(self, monkeypatch, wrapped_object):
        super().__setattr__('monkeypatch', monkeypatch)
        super().__setattr__('wrapped_object', wrapped_object)

    def __getattr__(self, attr):
        return getattr(self.wrapped_object, attr)

    def __getitem__(self, item):
        return self.wrapped_object.get(item)

    def __setattr__(self, attr, value):
        self.monkeypatch.setattr(self.wrapped_object, attr, value,
                                 raising=False)

    def __setitem__(self, item, value):
        self.monkeypatch.setitem(self.wrapped_object, item, value)

    def __delattr__(self, attr):
        self.monkeypatch.delattr(self.wrapped_object, attr)

    def __delitem__(self, item):
        self.monkeypatch.delitem(self.wrapped_object, item)


@pytest.fixture
def recipes(request, monkeypatch):

    return MonkeyPatchWrapper(monkeypatch, core.RECIPES)


@pytest.fixture
def layer(recipes):
    recipe = Recipe(copy(recipes['default']))
    recipes['default'] = recipe
    layer = recipe.layers['mylayer']
    return layer