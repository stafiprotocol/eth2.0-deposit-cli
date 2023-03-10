import os
import click
from typing import (
    Any,
    Callable,
)

from eth2deposit.credentials import (
    CredentialList,
)
from eth2deposit.exceptions import ValidationError
from eth2deposit.utils.validation import (
    verify_deposit_data_json,
    verify_stake_data_json,
    validate_password_strength,
)
from eth2deposit.utils.constants import (
    ETH2GWEI,
    DEFAULT_VALIDATOR_KEYS_FOLDER_NAME,
)
from eth2deposit.utils.ascii_art import RHINO_0
from eth2deposit.settings import (
    ALL_CHAINS,
    MAINNET,
    get_chain_setting,
)


def get_password(text: str) -> str:
    return click.prompt(text, hide_input=True, show_default=False, type=str)


def validate_password(cts: click.Context, param: Any, password: str) -> str:
    is_valid_password = False

    # The given password has passed confirmation
    try:
        validate_password_strength(password)
    except ValidationError as e:
        click.echo(f'Error: {e} Please retype.')
    else:
        is_valid_password = True

    while not is_valid_password:
        password = get_password(text='Type the password that secures your validator keystore(s)')
        try:
            validate_password_strength(password)
        except ValidationError as e:
            click.echo(f'Error: {e} Please retype.')
        else:
            # Confirm password
            password_confirmation = get_password(text='Repeat for confirmation')
            if password == password_confirmation:
                is_valid_password = True
            else:
                click.echo('Error: the two entered values do not match. Please retype again.')

    return password

def validate_num_eth(cts: click.Context, param: Any, num: int) -> int:
    if num == 1 or num == 12:
        return num

    while True:
        num = click.prompt("Please choose how many eth you wish to deposit (use 1 if you are trust node, otherwise use 12)", hide_input=False, show_default=True, type=int)
        if num == 1 or num == 12:
            return num

def generate_keys_arguments_decorator(function: Callable[..., Any]) -> Callable[..., Any]:
    '''
    This is a decorator that, when applied to a parent-command, implements the
    to obtain the necessary arguments for the generate_keys() subcommand.
    '''
    decorators = [
        click.option(
            '--num_validators',
            prompt='Please choose how many validators you wish to run',
            help='The number of validators keys you want to generate (you can always generate more later)',
            required=True,
            type=click.IntRange(0, 2**32 - 1),
        ),
        click.option(
            '--num_eth',
            default=12,
            prompt='Please choose how many eth you wish to deposit (use 1 if you are trust node, otherwise use 12)',
            help='The number of eth you want to generate (1 or 12 default 412)',
            required=True,
            callback=validate_num_eth,
            type=click.IntRange(1, 12),
        ),
        click.option(
            '--folder',
            default=os.getcwd(),
            help='The folder to place the generated keystores and deposit_data.json in',
            type=click.Path(exists=True, file_okay=False, dir_okay=True),
        ),
        click.option(
            '--chain',
            default=MAINNET,
            help='The version of eth2 you are targeting. use "mainnet" if you are depositing ETH',
            prompt='Please choose the (mainnet or testnet) network/chain name',
            type=click.Choice(ALL_CHAINS.keys(), case_sensitive=False),
        ),
        click.password_option(
            '--keystore_password',
            callback=validate_password,
            help=('The password that will secure your keystores. You will need to re-enter this to decrypt them when '
                  'you setup your eth2 validators. (It is reccomened not to use this argument, and wait for the CLI '
                  'to ask you for your mnemonic as otherwise it will appear in your shell history.)'),
            prompt='Type the password that secures your validator keystore(s)',
        ),
    ]
    for decorator in reversed(decorators):
        function = decorator(function)
    return function


@click.command()
@click.pass_context
def generate_keys(ctx: click.Context, validator_start_index: int,
                  num_validators: int, num_eth: int, folder: str, chain: str, keystore_password: str, **kwargs: Any) -> None:
    mnemonic = ctx.obj['mnemonic']
    mnemonic_password = ctx.obj['mnemonic_password']
    if num_eth!=12 and num_eth!=1:
        raise ValidationError("num_eth only support 1 or 12")
    deposit_amounts = [num_eth*ETH2GWEI] * num_validators
    stake_amounts = [(32-num_eth)*ETH2GWEI] * num_validators
    folder = os.path.join(folder, DEFAULT_VALIDATOR_KEYS_FOLDER_NAME)
    chain_setting = get_chain_setting(chain)
    if not os.path.exists(folder):
        os.mkdir(folder)
    click.clear()
    click.echo(RHINO_0)
    click.echo('Creating your keys(v2).')
    deposit_credentials = CredentialList.from_mnemonic(
        mnemonic=mnemonic,
        mnemonic_password=mnemonic_password,
        num_keys=num_validators,
        amounts=deposit_amounts,
        chain_setting=chain_setting,
        start_index=validator_start_index,
    )
    stake_credentials = CredentialList.from_mnemonic(
        mnemonic=mnemonic,
        mnemonic_password=mnemonic_password,
        num_keys=num_validators,
        amounts=stake_amounts,
        chain_setting=chain_setting,
        start_index=validator_start_index,
    )
    keystore_filefolders = deposit_credentials.export_keystores(password=keystore_password, folder=folder)
    deposits_file = deposit_credentials.export_deposit_data_json(folder=folder)
    stakes_file = stake_credentials.export_stake_data_json(folder=folder)

    if not deposit_credentials.verify_keystores(keystore_filefolders=keystore_filefolders, password=keystore_password):
        raise ValidationError("Failed to verify the keystores.")
    if not verify_deposit_data_json(deposits_file):
        raise ValidationError("Failed to verify the deposit data JSON files.")
    if not verify_stake_data_json(stakes_file):
        raise ValidationError("Failed to verify the stake data JSON files.")
    click.echo('\nSuccess!\nYour keys can be found at: %s' % folder)
    click.pause('\n\nPress any key.')
