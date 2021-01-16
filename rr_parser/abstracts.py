from abc import ABC, abstractmethod

from .charsets import Gen3Charset


class SectionChecksum(ABC):
    @staticmethod
    @abstractmethod
    def get_checksum(section_data: bytes, section_id: int) -> bytes:
        """Generate expected section checksum.

        Gen3 games and hackroms use section data sub-block and section ID based
        length for generating a 2 byte checksum value.

        Parameters
        ----------
        section_data : bytes
            Section data.
        section_id : int
            Section ID.

        Returns
        -------
        bytes
            Generated checksum using section data and ID.
        """
        pass
    pass


class UpdatableData(ABC):
    @property
    @abstractmethod
    def data(self) -> bytes:
        """Return block data."""
        pass

    @abstractmethod
    def update_from_sub_data(self):
        """Use class edited fields for updating the block data."""
        pass

    @abstractmethod
    def update_from_data(self):
        """Use block data for re-building the object."""
        pass

    def __add__(self, other):
        """For byte concatenating."""
        if isinstance(other, UpdatableData):
            return self.data + other.data
        else:
            return NotImplemented
    pass


class Section(UpdatableData):
    @property
    @abstractmethod
    def section(self) -> bytes:
        """Get section data."""
        pass

    @section.setter
    @abstractmethod
    def section(self, val: bytes):
        """Set section data and update class accordingly."""
        pass

    @property
    @abstractmethod
    def data(self) -> bytes:
        """Get section data sub-block."""
        pass

    @property
    @abstractmethod
    def section_id(self) -> int:
        """Get section footer's section ID value."""
        pass

    @property
    @abstractmethod
    def checksum(self) -> bytes:
        """Get section footer's checksum value."""
        pass

    @property
    @abstractmethod
    def security(self) -> bytes:
        """Get section footer's security value."""
        pass

    @property
    @abstractmethod
    def save_index(self) -> int:
        """Get section footer's save index value."""
        pass

    @property
    @abstractmethod
    def checksum_generator(self):
        """Get expected section's checksum."""
        pass

    @property
    @abstractmethod
    def is_used(self) -> bool:
        """Whether the current section belongs to a valid savegame."""
        pass

    @abstractmethod
    def update_checksum(self):
        """Calculate section checksum and set it on section data."""
        pass

    @abstractmethod
    def update_security(self):
        """Update section security value.

        Radical Red requires a security value of 0x08012025.
        """

    @abstractmethod
    def check_valid(self) -> bool:
        """Verify that checksum matches expected value."""
        pass

    pass


class Pokemon(UpdatableData, Gen3Charset):
    LANGUAGES = {
        0x0201: "Japanese",
        0x0202: "English",
        0x0203: "French",
        0x0204: "Italian",
        0x0205: "German",
        0x0206: "Korean",
        0x0207: "Spanish"
    }

    @abstractmethod
    def check(self) -> bool:
        """Check if Pokemon is valid.

        Returns
        -------
        bool
            Check that Pokemon data checksum matches the correct checksum.
        """
        pass

    pass


class PokemonSubData(UpdatableData, Gen3Charset):
    @property
    @abstractmethod
    def species(self) -> int:
        """Get Pokemon species value."""
        pass

    @species.setter
    @abstractmethod
    def species(self, val: int):
        """Set Pokemon species value."""
        pass

    @property
    @abstractmethod
    def evs(self) -> list[int]:
        """Get Pokemon EVs."""
        pass

    @evs.setter
    @abstractmethod
    def evs(self, val: list[int]):
        """Set Pokemon EVs."""
        pass

    @abstractmethod
    def get_checksum(self) -> bytes:
        """Get expected Pokemon data checksum."""
        pass

    pass


class GameSave(UpdatableData):
    @abstractmethod
    def check_valid(self) -> bool:
        """Check that game save section checksums are valid."""
        pass

    @property
    @abstractmethod
    def is_used(self) -> bool:
        """Check that game save does contain game data."""
        pass

    @abstractmethod
    def clear(self):
        """Clear game save."""
        pass

    @abstractmethod
    def update_pokedex(self):
        """Update savegame from edited Pokedex."""
        """Update the savegame Pokedex entries."""
    pass


class Pokedex(ABC):
    @property
    @abstractmethod
    def data_seen(self) -> bytes:
        """Serialized Seen Pokemon as bytes of length *pokedex_data_length*."""
        pass

    @data_seen.setter
    @abstractmethod
    def data_seen(self, val: bytes):
        """Seen Pokemon setter."""
        pass

    @property
    @abstractmethod
    def data_caught(self) -> bytes:
        """Serialized Caught Pokemon as bytes of len(pokedex_data_length)."""
        pass

    @data_caught.setter
    @abstractmethod
    def data_caught(self, val: bytes):
        """Caught Pokemon setter."""
        pass

    @property
    @abstractmethod
    def pokedex_size_bytes(self) -> int:
        """Number of bytes dedicated to Pokedex entries."""
        pass

    @abstractmethod
    def set_seen(self, species: int):
        """Mark Pokemon species as seen."""
        pass

    @abstractmethod
    def set_caught(self, species: int):
        """Mark Pokemon species as caught."""
        pass

    @abstractmethod
    def unset_seen(self, species: int):
        """Mark Pokemon species as unseen (and uncaught)."""
        pass

    @abstractmethod
    def unset_caught(self, species: int):
        """Mark Pokemon species as uncaught."""
        pass

    pass


__all__ = [
    "SectionChecksum",
    "Section",
    "Pokemon",
    "UpdatableData",
    "PokemonSubData",
    "GameSave",
    "Pokedex"
]
