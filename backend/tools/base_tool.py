"""
base_tool.py – Abstract base class for all Cloud Identity Security Assistant tools.

Every concrete tool must subclass ``BaseTool`` and implement:
    * ``name``             – short snake_case identifier used by the LLM
    * ``description``      – natural-language description shown to the LLM
    * ``parameters_schema`` – JSON Schema dict describing accepted parameters
    * ``execute(**kwargs)`` – async method that performs the actual work

The helper ``to_bedrock_spec()`` converts the tool metadata into the dict
format required by the **Amazon Bedrock Converse API** ``toolSpec``.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Abstract base class that every CISA tool must inherit from."""

    # ------------------------------------------------------------------ #
    #  Subclasses MUST set these three class-level / instance attributes  #
    # ------------------------------------------------------------------ #

    @property
    @abstractmethod
    def name(self) -> str:
        """Short, unique, snake_case name for the tool (e.g. ``list_iam_users``)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human / LLM-readable description of what the tool does."""
        ...

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON Schema (as a Python dict) for the tool's input parameters."""
        ...

    # ------------------------------------------------------------------ #
    #  Abstract execute – every tool must implement this                  #
    # ------------------------------------------------------------------ #

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool with the given keyword arguments.

        Returns
        -------
        dict
            A structured result dictionary.  The exact shape is
            tool-specific, but it should always be JSON-serialisable.

        Raises
        ------
        Exception
            Implementations should catch AWS / parsing errors and
            return an ``{"error": "..."}`` dict rather than letting
            raw exceptions propagate, but callers should still be
            prepared for unexpected errors.
        """
        ...

    # ------------------------------------------------------------------ #
    #  Bedrock Converse API helper                                        #
    # ------------------------------------------------------------------ #

    def to_bedrock_spec(self) -> Dict[str, Any]:
        """Convert this tool's metadata to the Bedrock Converse API ``toolSpec`` format.

        Returns
        -------
        dict
            A dict matching the shape expected by ``ConverseRequest.tools``:

            .. code-block:: python

                {
                    "toolSpec": {
                        "name": "<tool_name>",
                        "description": "<tool_description>",
                        "inputSchema": {
                            "json": { ... JSON Schema ... }
                        }
                    }
                }
        """
        return {
            "toolSpec": {
                "name": self.name,
                "description": self.description,
                "inputSchema": {
                    "json": self.parameters_schema,
                },
            }
        }

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                     #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} name={self.name!r}>"
