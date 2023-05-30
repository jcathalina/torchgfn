from abc import ABC, abstractmethod
from typing import Callable, Tuple

from torchtyping import TensorType

from gfn.states import States


class Preprocessor(ABC):
    """
    Base class for Preprocessors. The goal is to transform tensors representing raw states
    to tensors that can be used as input to neural networks.
    """

    def __init__(self, output_shape: Tuple[int]) -> None:
        self.output_shape = output_shape

    @abstractmethod
    def preprocess(self, states: States) -> TensorType["batch_shape", "input_dim"]:
        pass

    def __call__(self, states: States) -> TensorType["batch_shape", "input_dim"]:
        return self.preprocess(states)

    def __repr__(self):
        return f"{self.__class__.__name__}, output_shape={self.output_shape}"


class IdentityPreprocessor(Preprocessor):
    """Simple preprocessor applicable to environments with uni-dimensional states.
    This is the default preprocessor used."""

    def preprocess(self, states: States) -> TensorType["batch_shape", "input_dim"]:
        return states.tensor.float()


class EnumPreprocessor(Preprocessor):
    "Preprocessor applicable to environments with discrete states."

    def __init__(
        self,
        get_states_indices: Callable[[States], TensorType["batch_shape", "input_dim"]],
    ) -> None:
        """Preprocessor for environments with enumerable states (finite number of states).
        Each state is represented by a unique integer (>= 0) index.

        Args:
            get_states_indices (Callable[[States], BatchOutputTensor]): function that returns the unique indices of the states.
        """
        super().__init__(output_shape=(1,))
        self.get_states_indices = get_states_indices

    def preprocess(self, states):
        return self.get_states_indices(states).long().unsqueeze(-1)
