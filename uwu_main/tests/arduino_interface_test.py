from import_context import arduino_interface as interface
import pytest

def test_connection_init():
    assert(interface.wait_for_connection(30))
