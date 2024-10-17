from config import Chains
from models import ContractRaw


class Contracts:
    ARBSWAP_SWAP_FACTORY = ContractRaw(
        address='0xd394e9cc20f43d2651293756f8d320668e850f1b',
        abi_name='arbswap_swap_factory',
        chain=Chains.ARBITRUM_ONE)
    ARBSWAP_UNI_ROUTER = ContractRaw(
        address='0x6947a425453d04305520e612f0cb2952e4d07d62',
        abi_name='arbswap_uni_router',
        chain=Chains.ARBITRUM_ONE)
    ARBSWAP_STABLE_SWAP_FACTORY = ContractRaw(
        address='0x3a52e9200Ed7403D9d21664fDee540C2d02c099d',
        abi_name='arbswap_stable_swap_factory',
        chain=Chains.ARBITRUM_ONE)

