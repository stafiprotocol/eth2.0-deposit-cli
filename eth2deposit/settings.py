from typing import Dict, NamedTuple


DEPOSIT_CLI_VERSION = '2.1.0'


class BaseChainSetting(NamedTuple):
    ETH2_NETWORK_NAME: str
    GENESIS_FORK_VERSION: bytes


MAINNET = 'mainnet'
GOERLI = 'goerli'
ZHEJIANG = 'zhejiang'

# Eth2 Mainnet setting
MainnetSetting = BaseChainSetting(ETH2_NETWORK_NAME=MAINNET, GENESIS_FORK_VERSION=bytes.fromhex('00000000'))
# Goerli setting
GoerliSetting = BaseChainSetting(ETH2_NETWORK_NAME=GOERLI, GENESIS_FORK_VERSION=bytes.fromhex('00001020'))
# Zhejiang setting
ZhejiangSetting = BaseChainSetting(NETWORK_NAME=ZHEJIANG, GENESIS_FORK_VERSION=bytes.fromhex('00000069'))

ALL_CHAINS: Dict[str, BaseChainSetting] = {
    MAINNET: MainnetSetting,
    GOERLI: GoerliSetting,
    ZHEJIANG: ZhejiangSetting,
}


def get_chain_setting(chain_name: str = MAINNET) -> BaseChainSetting:
    return ALL_CHAINS[chain_name]
