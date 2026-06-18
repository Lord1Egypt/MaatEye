"""
🌐 MaatEye — Multi-Chain EVM Registry
All 24 EVM chains from rpc-radar-bot, with verified public RPC endpoints.
Source: https://github.com/Lord1Egypt/rpc-radar-bot
"""

from dataclasses import dataclass, field


@dataclass
class EVMChain:
    """An EVM-compatible blockchain configuration."""
    key: str
    name: str
    rpc_url: str
    chain_id: int
    symbol: str
    explorer_url: str
    explorer_api: str  # Base URL for the explorer API
    emoji: str
    native_explorer: bool = True  # Has a compatible explorer API
    enabled: bool = True          # Can be toggled off if explorer API is problematic
    scan_limit_rps: float = 5.0   # Rate limit for the explorer API
    scan_top_tokens: int = 20     # Default number of top tokens to scan


# ── EVM Chain Registry ────────────────────────────────────────────────────────
# All RPCs from publicnode.com (free, no API key needed)
# Explorer APIs vary: Etherscan-compatible (most) or Blockscout (some)

EVM_CHAINS: dict[str, EVMChain] = {
    "ethereum": EVMChain(
        key="ethereum", name="Ethereum",
        rpc_url="https://ethereum-rpc.publicnode.com",
        chain_id=1, symbol="ETH",
        explorer_url="https://etherscan.io",
        explorer_api="https://api.etherscan.io/api",
        emoji="🔵", scan_top_tokens=30,
    ),
    "bnb": EVMChain(
        key="bnb", name="BNB Chain",
        rpc_url="https://bsc-rpc.publicnode.com",
        chain_id=56, symbol="BNB",
        explorer_url="https://bscscan.com",
        explorer_api="https://api.bscscan.com/api",
        emoji="🟡", scan_top_tokens=20,
    ),
    "polygon": EVMChain(
        key="polygon", name="Polygon",
        rpc_url="https://polygon-bor-rpc.publicnode.com",
        chain_id=137, symbol="MATIC",
        explorer_url="https://polygonscan.com",
        explorer_api="https://api.polygonscan.com/api",
        emoji="🟣", scan_top_tokens=20,
    ),
    "base": EVMChain(
        key="base", name="Base",
        rpc_url="https://base-rpc.publicnode.com",
        chain_id=8453, symbol="ETH",
        explorer_url="https://basescan.org",
        explorer_api="https://api.basescan.org/api",
        emoji="🔷", scan_top_tokens=20,
    ),
    "arbitrum": EVMChain(
        key="arbitrum", name="Arbitrum One",
        rpc_url="https://arbitrum-one-rpc.publicnode.com",
        chain_id=42161, symbol="ETH",
        explorer_url="https://arbiscan.io",
        explorer_api="https://api.arbiscan.io/api",
        emoji="🌀", scan_top_tokens=20,
    ),
    "optimism": EVMChain(
        key="optimism", name="Optimism",
        rpc_url="https://optimism-rpc.publicnode.com",
        chain_id=10, symbol="ETH",
        explorer_url="https://optimistic.etherscan.io",
        explorer_api="https://api-optimistic.etherscan.io/api",
        emoji="🔴", scan_top_tokens=20,
    ),
    "avalanche": EVMChain(
        key="avalanche", name="Avalanche C-Chain",
        rpc_url="https://avalanche-c-chain-rpc.publicnode.com",
        chain_id=43114, symbol="AVAX",
        explorer_url="https://snowtrace.io",
        explorer_api="https://api.snowtrace.io/api",
        emoji="🔺", scan_top_tokens=20,
    ),
    "linea": EVMChain(
        key="linea", name="Linea",
        rpc_url="https://linea-rpc.publicnode.com",
        chain_id=59144, symbol="ETH",
        explorer_url="https://lineascan.build",
        explorer_api="https://api.lineascan.build/api",
        emoji="⬛", scan_top_tokens=15,
    ),
    "scroll": EVMChain(
        key="scroll", name="Scroll",
        rpc_url="https://scroll-rpc.publicnode.com",
        chain_id=534352, symbol="ETH",
        explorer_url="https://scrollscan.com",
        explorer_api="https://api.scrollscan.com/api",
        emoji="📜", scan_top_tokens=15,
    ),
    "blast": EVMChain(
        key="blast", name="Blast",
        rpc_url="https://blast-rpc.publicnode.com",
        chain_id=81457, symbol="ETH",
        explorer_url="https://blastscan.io",
        explorer_api="https://api.blastscan.io/api",
        emoji="💥", scan_top_tokens=15,
    ),
    "gnosis": EVMChain(
        key="gnosis", name="Gnosis",
        rpc_url="https://gnosis-rpc.publicnode.com",
        chain_id=100, symbol="xDAI",
        explorer_url="https://gnosisscan.io",
        explorer_api="https://api.gnosisscan.io/api",
        emoji="🦉", scan_top_tokens=15,
    ),
    "celo": EVMChain(
        key="celo", name="Celo",
        rpc_url="https://celo-rpc.publicnode.com",
        chain_id=42220, symbol="CELO",
        explorer_url="https://celoscan.io",
        explorer_api="https://api.celoscan.io/api",
        emoji="🌿", scan_top_tokens=15,
    ),
    "moonbeam": EVMChain(
        key="moonbeam", name="Moonbeam",
        rpc_url="https://moonbeam-rpc.publicnode.com",
        chain_id=1284, symbol="GLMR",
        explorer_url="https://moonscan.io",
        explorer_api="https://api.moonscan.io/api",
        emoji="🌕", scan_top_tokens=15,
    ),
    "metis": EVMChain(
        key="metis", name="Metis",
        rpc_url="https://metis-rpc.publicnode.com",
        chain_id=1088, symbol="METIS",
        explorer_url="https://andromeda-explorer.metis.io",
        explorer_api="https://api.andromeda-explorer.metis.io/api",
        emoji="🏛", scan_top_tokens=15,
    ),
    "opbnb": EVMChain(
        key="opbnb", name="opBNB",
        rpc_url="https://opbnb-rpc.publicnode.com",
        chain_id=204, symbol="BNB",
        explorer_url="https://mainnet.opbnbscan.com",
        explorer_api="https://api.opbnbscan.com/api",
        emoji="🟨", scan_top_tokens=10,
    ),
    "pulsechain": EVMChain(
        key="pulsechain", name="PulseChain",
        rpc_url="https://pulsechain-rpc.publicnode.com",
        chain_id=369, symbol="PLS",
        explorer_url="https://scan.pulsechain.com",
        explorer_api="https://api.scan.pulsechain.com/api",
        emoji="💓", scan_top_tokens=10,
    ),
    "mantle": EVMChain(
        key="mantle", name="Mantle",
        rpc_url="https://mantle-rpc.publicnode.com",
        chain_id=5000, symbol="MNT",
        explorer_url="https://explorer.mantle.xyz",
        explorer_api="https://api.explorer.mantle.xyz/api",
        emoji="⚙️", scan_top_tokens=10,
    ),
    "taiko": EVMChain(
        key="taiko", name="Taiko",
        rpc_url="https://taiko-rpc.publicnode.com",
        chain_id=167000, symbol="ETH",
        explorer_url="https://taikoscan.io",
        explorer_api="https://api.taikoscan.io/api",
        emoji="🥁", scan_top_tokens=10,
    ),
    "berachain": EVMChain(
        key="berachain", name="Berachain",
        rpc_url="https://berachain-rpc.publicnode.com",
        chain_id=80094, symbol="BERA",
        explorer_url="https://berascan.com",
        explorer_api="https://api.berascan.com/api",
        emoji="🐻", scan_top_tokens=10,
    ),
    "soneium": EVMChain(
        key="soneium", name="Soneium",
        rpc_url="https://soneium-rpc.publicnode.com",
        chain_id=1868, symbol="ETH",
        explorer_url="https://soneium.blockscout.com",
        explorer_api="https://soneium.blockscout.com/api",
        emoji="🌊", scan_top_tokens=10,
    ),
    "unichain": EVMChain(
        key="unichain", name="Unichain",
        rpc_url="https://unichain-rpc.publicnode.com",
        chain_id=130, symbol="ETH",
        explorer_url="https://unichain.blockscout.com",
        explorer_api="https://unichain.blockscout.com/api",
        emoji="🦄", scan_top_tokens=10,
    ),
    "fraxtal": EVMChain(
        key="fraxtal", name="Fraxtal",
        rpc_url="https://fraxtal-rpc.publicnode.com",
        chain_id=252, symbol="frxETH",
        explorer_url="https://fraxscan.com",
        explorer_api="https://api.fraxscan.com/api",
        emoji="⬜", scan_top_tokens=10,
    ),
    "chiliz": EVMChain(
        key="chiliz", name="Chiliz",
        rpc_url="https://chiliz-rpc.publicnode.com",
        chain_id=88888, symbol="CHZ",
        explorer_url="https://scan.chiliz.com",
        explorer_api="https://scan.chiliz.com/api",
        emoji="🌶", scan_top_tokens=10,
    ),
    "sonic": EVMChain(
        key="sonic", name="Sonic",
        rpc_url="https://sonic-rpc.publicnode.com",
        chain_id=146, symbol="S",
        explorer_url="https://sonicscan.org",
        explorer_api="https://api.sonicscan.org/api",
        emoji="⚡", scan_top_tokens=10,
    ),

    "sepolia": EVMChain(
        key="sepolia", name="Sepolia Testnet",
        rpc_url="https://rpc.sepolia.com",
        chain_id=11155111, symbol="ETH",
        explorer_url="https://sepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=11155111",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "hoodi": EVMChain(
        key="hoodi", name="Hoodi Testnet",
        rpc_url="https://rpc.hoodi.com",
        chain_id=560048, symbol="ETH",
        explorer_url="https://hoodiscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=560048",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "lineasepolia": EVMChain(
        key="lineasepolia", name="Linea Sepolia Testnet",
        rpc_url="https://rpc.lineasepolia.com",
        chain_id=59141, symbol="ETH",
        explorer_url="https://lineasepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=59141",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "blastsepolia": EVMChain(
        key="blastsepolia", name="Blast Sepolia Testnet",
        rpc_url="https://rpc.blastsepolia.com",
        chain_id=168587773, symbol="ETH",
        explorer_url="https://blastsepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=168587773",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "opsepolia": EVMChain(
        key="opsepolia", name="OP Sepolia Testnet",
        rpc_url="https://rpc.opsepolia.com",
        chain_id=11155420, symbol="ETH",
        explorer_url="https://opsepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=11155420",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "bittorrentchain": EVMChain(
        key="bittorrentchain", name="BitTorrent Chain Testnet",
        rpc_url="https://rpc.bittorrentchain.com",
        chain_id=1029, symbol="ETH",
        explorer_url="https://bittorrentchainscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=1029",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "celosepolia": EVMChain(
        key="celosepolia", name="Celo Sepolia Testnet",
        rpc_url="https://rpc.celosepolia.com",
        chain_id=11142220, symbol="ETH",
        explorer_url="https://celosepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=11142220",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "fraxtalhoodi": EVMChain(
        key="fraxtalhoodi", name="Fraxtal Hoodi Testnet",
        rpc_url="https://rpc.fraxtalhoodi.com",
        chain_id=2523, symbol="ETH",
        explorer_url="https://fraxtalhoodiscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=2523",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "mantlesepolia": EVMChain(
        key="mantlesepolia", name="Mantle Sepolia Testnet",
        rpc_url="https://rpc.mantlesepolia.com",
        chain_id=5003, symbol="ETH",
        explorer_url="https://mantlesepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=5003",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "memecore": EVMChain(
        key="memecore", name="Memecore Mainnet",
        rpc_url="https://rpc.memecore.com",
        chain_id=4352, symbol="ETH",
        explorer_url="https://memecorescan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=4352",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "memecoreinsectarium": EVMChain(
        key="memecoreinsectarium", name="Memecore Insectarium Testnet",
        rpc_url="https://rpc.memecoreinsectarium.com",
        chain_id=43522, symbol="ETH",
        explorer_url="https://memecoreinsectariumscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=43522",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "moonriver": EVMChain(
        key="moonriver", name="Moonriver Mainnet",
        rpc_url="https://rpc.moonriver.com",
        chain_id=1285, symbol="ETH",
        explorer_url="https://moonriverscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=1285",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "taikohoodi": EVMChain(
        key="taikohoodi", name="Taiko Hoodi",
        rpc_url="https://rpc.taikohoodi.com",
        chain_id=167013, symbol="ETH",
        explorer_url="https://taikohoodiscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=167013",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "xdc": EVMChain(
        key="xdc", name="XDC Mainnet",
        rpc_url="https://rpc.xdc.com",
        chain_id=50, symbol="ETH",
        explorer_url="https://xdcscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=50",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "xdcapothem": EVMChain(
        key="xdcapothem", name="XDC Apothem Testnet",
        rpc_url="https://rpc.xdcapothem.com",
        chain_id=51, symbol="ETH",
        explorer_url="https://xdcapothemscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=51",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "apechain": EVMChain(
        key="apechain", name="ApeChain Mainnet",
        rpc_url="https://rpc.apechain.com",
        chain_id=33139, symbol="ETH",
        explorer_url="https://apechainscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=33139",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "apechaincurtis": EVMChain(
        key="apechaincurtis", name="ApeChain Curtis Testnet",
        rpc_url="https://rpc.apechaincurtis.com",
        chain_id=33111, symbol="ETH",
        explorer_url="https://apechaincurtisscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=33111",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "world": EVMChain(
        key="world", name="World Mainnet",
        rpc_url="https://rpc.world.com",
        chain_id=480, symbol="ETH",
        explorer_url="https://worldscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=480",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "worldsepolia": EVMChain(
        key="worldsepolia", name="World Sepolia Testnet",
        rpc_url="https://rpc.worldsepolia.com",
        chain_id=4801, symbol="ETH",
        explorer_url="https://worldsepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=4801",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "unichainsepolia": EVMChain(
        key="unichainsepolia", name="Unichain Sepolia Testnet",
        rpc_url="https://rpc.unichainsepolia.com",
        chain_id=1301, symbol="ETH",
        explorer_url="https://unichainsepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=1301",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "abstract": EVMChain(
        key="abstract", name="Abstract Mainnet",
        rpc_url="https://rpc.abstract.com",
        chain_id=2741, symbol="ETH",
        explorer_url="https://abstractscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=2741",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "abstractsepolia": EVMChain(
        key="abstractsepolia", name="Abstract Sepolia Testnet",
        rpc_url="https://rpc.abstractsepolia.com",
        chain_id=11124, symbol="ETH",
        explorer_url="https://abstractsepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=11124",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "berachainbepolia": EVMChain(
        key="berachainbepolia", name="Berachain Bepolia Testnet",
        rpc_url="https://rpc.berachainbepolia.com",
        chain_id=80069, symbol="ETH",
        explorer_url="https://berachainbepoliascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=80069",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "monad": EVMChain(
        key="monad", name="Monad Testnet",
        rpc_url="https://rpc.monad.com",
        chain_id=10143, symbol="ETH",
        explorer_url="https://monadscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=10143",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "hyperevm": EVMChain(
        key="hyperevm", name="HyperEVM Mainnet",
        rpc_url="https://rpc.hyperevm.com",
        chain_id=999, symbol="ETH",
        explorer_url="https://hyperevmscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=999",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "katana": EVMChain(
        key="katana", name="Katana Mainnet",
        rpc_url="https://rpc.katana.com",
        chain_id=747474, symbol="ETH",
        explorer_url="https://katanascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=747474",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "katanabokuto": EVMChain(
        key="katanabokuto", name="Katana Bokuto",
        rpc_url="https://rpc.katanabokuto.com",
        chain_id=737373, symbol="ETH",
        explorer_url="https://katanabokutoscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=737373",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "sei": EVMChain(
        key="sei", name="Sei Testnet",
        rpc_url="https://rpc.sei.com",
        chain_id=1328, symbol="ETH",
        explorer_url="https://seiscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=1328",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "stable": EVMChain(
        key="stable", name="Stable Testnet",
        rpc_url="https://rpc.stable.com",
        chain_id=2201, symbol="ETH",
        explorer_url="https://stablescan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=2201",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "plasma": EVMChain(
        key="plasma", name="Plasma Testnet",
        rpc_url="https://rpc.plasma.com",
        chain_id=9746, symbol="ETH",
        explorer_url="https://plasmascan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=9746",
        emoji="⛓️", scan_top_tokens=10,
    ),
    "megaeth": EVMChain(
        key="megaeth", name="MegaETH Testnet",
        rpc_url="https://rpc.megaeth.com",
        chain_id=6343, symbol="ETH",
        explorer_url="https://megaethscan.com",
        explorer_api="https://api.etherscan.io/v2/api?chainid=6343",
        emoji="⛓️", scan_top_tokens=10,
    ),
}


# ── Chain Aliases ──────────────────────────────────────────────────────────────
ALIASES = {
    "eth": "ethereum", "ether": "ethereum", "mainnet": "ethereum",
    "bsc": "bnb", "binance": "bnb", "bnbchain": "bnb",
    "poly": "polygon", "matic": "polygon",
    "arb": "arbitrum", "arbone": "arbitrum",
    "op": "optimism",
    "avax": "avalanche", "ava": "avalanche",
    "xdai": "gnosis", "gno": "gnosis",
    "opbnb": "opbnb",
    "pulse": "pulsechain", "pls": "pulsechain",
    "mnt": "mantle",
    "bera": "berachain",
    "uni": "unichain",
    "frax": "fraxtal",
    "chz": "chiliz",
}


def get_chain(key: str) -> EVMChain | None:
    """Get chain config by key or alias."""
    key = key.lower().strip()
    if key in EVM_CHAINS:
        return EVM_CHAINS[key]
    if key in ALIASES:
        return EVM_CHAINS.get(ALIASES[key])
    return None


def list_chains() -> list[EVMChain]:
    """Get list of all enabled EVM chains."""
    return [c for c in EVM_CHAINS.values() if c.enabled]


def get_chain_count() -> int:
    """Get number of enabled EVM chains."""
    return len(list_chains())
