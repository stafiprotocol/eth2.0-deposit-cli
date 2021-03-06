import pytest

from eth2deposit.credentials import CredentialList
from eth2deposit.settings import MedallaSetting


def test_from_mnemonic() -> None:
    with pytest.raises(ValueError):
        CredentialList.from_mnemonic(
            mnemonic="",
            mnemonic_password="",
            num_keys=1,
            amounts=[32, 32],
            chain_setting=MedallaSetting,
            start_index=1,
        )
