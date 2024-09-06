# pyright: reportMissingModuleSource=false
from algopy import ARC4Contract, String
from algopy.arc4 import abimethod

class Store(ARC4Contract):
    def __init__(self) -> None:  # Add the return type annotation
        # Initialize the storage variable directly without calling super().__init__()
        self.stored_value = String("")  # Initialize the storage variable

    @abimethod()
    def set_value(self, value: String) -> None:
        """
        Store the provided value in the contract's storage.
        """
        self.stored_value = value  # Store the value

    @abimethod()
    def get_value(self) -> String:
        """
        Retrieve the stored value.
        """
        return self.stored_value  # Return the stored value
