from functools import cached_property

from ..timeit import timeit
from ..view.render import render
from ..view.types import Derived
from .types import State


class DeepState(State):
    @cached_property
    def derived(self) -> Derived:
        with timeit("render"):
            return render(
                self.root,
                settings=self.settings,
                index=self.index,
                selection=self.selection,
                filter_pattern=self.filter_pattern,
                markers=self.markers,
                diagnostics=self.diagnostics,
                vc=self.vc,
                follow_links=self.follow_links,
                show_hidden=self.show_hidden,
                current=self.current,
            )
