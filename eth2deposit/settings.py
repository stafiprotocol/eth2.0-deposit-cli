from typing import Dict, NamedTuple


DEPOSIT_CLI_VERSION = '2.0.1'


class BaseChainSetting(NamedTuple):
    ETH2_NETWORK_NAME: str
    GENESIS_FORK_VERSION: bytes


MAINNET = 'mainnet'


# Eth2 Mainnet setting
MainnetSetting = BaseChainSetting(ETH2_NETWORK_NAME=MAINNET, GENESIS_FORK_VERSION=bytes.fromhex('00000000'))


ALL_CHAINS: Dict[str, BaseChainSetting] = {
    MAINNET: MainnetSetting,
}


def get_chain_setting(chain_name: str = MAINNET) -> BaseChainSetting:
    return ALL_CHAINS[chain_name]
