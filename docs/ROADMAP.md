# 🗺️ MaatEye — Full Vulnerability Scanner Roadmap

> *"The Eye of Ma'at sees all — nothing escapes the feather of truth."*
> 
> **Vision:** From 20 regex patterns → 100+ AST-powered detectors across EVM + non-EVM
> 
> **Current:** v0.4 — Multi-Chain Token Discovery Complete ✅

---

## 🏛️ Architecture Overview (Target)

```
User Input (address / chain / batch)
       │
       ▼
┌─────────────────────────────────────┐
│        ScanEngine Orchestrator      │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │   Layer 1: Regex Scanner    │    │  ← Quick scan, broad coverage
│  │   (20 existing patterns)    │    │
│  └─────────────────────────────┘    │
│            │                        │
│  ┌─────────────────────────────┐    │
│  │   Layer 2: AST Analyzer     │    │  ← Deep analysis, low false positives
│  │   (Slither + custom IR)     │    │
│  └─────────────────────────────┘    │
│            │                        │
│  ┌─────────────────────────────┐    │
│  │ Layer 3: Exploitability     │    │  ← Is it actually exploitable?
│  │   Scoring Engine            │    │
│  └─────────────────────────────┘    │
│            │                        │
│  ┌─────────────────────────────┐    │
│  │ Layer 4: Economic Sim       │    │  ← Flash loan simulation
│  │   (Agent-based modeling)    │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Report + Alert             │
│  (Markdown / JSON / GitHub Issues  │
│   / Telegram / Dashboard)          │
└─────────────────────────────────────┘
```

---

## ✅ COMPLETED — Foundation (v0.1 → v0.4)

### ✅ v0.1 — Core Patterns
- [x] 20 Plagues patterns (P01-P20) — solidity regex-based
- [x] CI/CD with GitHub Actions
- [x] Pattern submission via Issues
- [x] Community contribution templates

### ✅ v0.2 — Multi-Chain Engine
- [x] **24 EVM chains** (Ethereum, BNB, Polygon, Arbitrum, etc.)
- [x] Chain registry from rpc-radar-bot
- [x] Multi-chain source fetcher (Etherscan + Blockscout APIs + RPC bytecode fallback)
- [x] Token discovery per chain (Explorer APIs)
- [x] Chain-aware vulnerability reporting
- [x] Cross-chain scan results with chain context

### ✅ v0.3 — Daily Guardian
- [x] **Daily automated cross-chain scan** (08:00 UTC)
- [x] Per-chain summary reports
- [x] Red Flag issues with chain info
- [x] Cross-chain dashboard
- [x] 350+ tokens scanned daily across 24 chains

### ✅ v0.4 — Mass Token Discovery
- [x] **CoinGecko API integration** (10k+ tokens across 100+ chains)
- [x] **RPC event-log discovery** (eth_getLogs Transfer events)
- [x] Explorer API top token lists (Etherscan/Blockscout)
- [x] Known token lists (curated defaults)
- [x] **Persistent Token Store** (`data/token_registry.json`)
- [x] Incremental discovery + dedup
- [x] Token metadata enrichment (symbol, name, decimals via eth_call)
- [x] `tokens` CLI command (import, stats, new, export, list)

---

## 🚧 NEXT: v0.5 — Pattern Explosion (60+ Patterns) 🔥

### 🎯 Goal: Expand from 20 → 60+ vulnerability patterns with better detection

#### 📦 Pattern Categories (New Classification System)

```
PATTERN_TAXONOMY/
├── ACCESS_CONTROL/          # P01, P05, P18 + new
│   ├── Unprotected Mint ✓
│   ├── Tx.origin Auth ✓
│   ├── Missing Access Control ✓
│   └── ✨ NEW: Unprotected Initializer
│   └── ✨ NEW: Role Admin Hijack
│   └── ✨ NEW: Ownership Transfer Without Two-Step
│   └── ✨ NEW: Pausable Without Unpause Guard
│
├── REENTRANCY/              # P03 expanded
│   ├── Classic Reentrancy ✓
│   └── ✨ NEW: Cross-Function Reentrancy
│   └── ✨ NEW: Read-Only Reentrancy
│   └── ✨ NEW: Cross-Contract Reentrancy
│   └── ✨ NEW: ERC721 Callback Reentrancy (onERC721Received)
│   └── ✨ NEW: ERC1155 Batch Reentrancy
│   └── ✨ NEW: Reentrancy Via Fallback
│   └── ✨ NEW:闪电贷 Reentrancy Bridge
│
├── ARITHMETIC/              # P04 expanded
│   ├── Integer Overflow ✓
│   └── ✨ NEW: Precision Loss (Division Before Multiplication)
│   └── ✨ NEW: Rounding in Favor of Wrong Party
│   └── ✨ NEW: Fee Calculation Exploit
│   └── ✨ NEW: Share Price Manipulation (EIP-4626)
│   └── ✨ NEW: Rebasing Token Accounting Mismatch
│   └── ✨ NEW: Batch Transfer Overflow
│
├── PROXY_UPGRADEABLE/       # P08, P16 expanded
│   ├── Storage Collision ✓
│   ├── Uninitialized Proxy ✓
│   └── ✨ NEW: Metamorphic Contract (selfdestruct + CREATE2)
│   └── ✨ NEW: Implementation Selfdestruct
│   └── ✨ NEW: Constructor in Implementation (not initializer)
│   └── ✨ NEW: Function Clashing (malicious implementation)
│   └── ✨ NEW: UUPS Without Upgrade Guard
│   └── ✨ NEW: Beacon Proxy Without Upgrade Auth
│   └── ✨ NEW: Proxy Admin Takeover
│
├── EXTERNAL_CALLS/          # P07, P17 expanded
│   ├── Arbitrary Delegatecall ✓
│   ├── Arbitrary External Call ✓
│   └── ✨ NEW: Unchecked Low-Level Call Return
│   └── ✨ NEW: Contract Existence Check Missing
│   └── ✨ NEW: Gas Stipend Dependency
│   └── ✨ NEW: Delegatecall to Untrusted Library
│   └── ✨ NEW: Staticcall With Side Effects
│   └── ✨ NEW: CREATE2 Address Collision
│
├── TOKEN_ECONOMICS/         # P11 expanded + new
│   ├── Flash Loan Vector ✓
│   ├── Oracle Manipulation ✓
│   └── ✨ NEW: Honeypot Detection (can't sell)
│   └── ✨ NEW: Fee-On-Transfer Accounting Mismatch
│   └── ✨ NEW: Deflationary Token Balance Change
│   └── ✨ NEW: ERC4626 Vault Share Manipulation
│   └── ✨ NEW: Liquidity Pool Imbalance (Curve-style)
│   └── ✨ NEW: MEV Sandwich Vulnerability
│   └── ✨ NEW: Slippage Protection Missing
│   └── ✨ NEW: Deadline Missing in Swaps
│   └── ✨ NEW: AMM Constant Product Invariant Break
│
├── GOVERNANCE/              # P13 expanded
│   ├── Governance Attack ✓
│   └── ✨ NEW: Flash Loan Governance Takeover
│   └── ✨ NEW: Low Quorum / Low Proposal Threshold
│   └── ✨ NEW: Timelock Bypass
│   └── ✨ NEW: Voter Delegation Attack
│   └── ✨ NEW: Proposal Front-Running
│   └── ✨ NEW: Cancel/Execute Race Condition
│
├── SIGNATURE_CRYPTO/        # P12 expanded + new
│   ├── Signature Replay ✓
│   └── ✨ NEW: EIP-2612 Permit Front-Running
│   └── ✨ NEW: EIP-712 Domain Separator Mismatch
│   └── ✨ NEW: Signature Malleability (ecrecover)
│   └── ✨ NEW: Missing Nonce Increment
│   └── ✨ NEW: Cross-Chain Replay (missing chainId)
│   └── ✨ NEW: Weak PRNG (block.timestamp, blockhash, etc.)
│   └── ✨ NEW: Predictable Randomness in Gambling
│
├── DOS_GAS/                 # New category
│   └── ✨ NEW: Gas Griefing (unbounded loop)
│   └── ✨ NEW: Block Gas Limit (array iteration)
│   └── ✨ NEW: DoS via Selfdestruct
│   └── ✨ NEW: DoS via Block Stuffing
│   └── ✨ NEW: Unexpected Revert in Pull-Over-Push
│   └── ✨ NEW: Fallback Function Gas Exhaustion
│   └── ✨ NEW: Large Array Deletion (O(n) cost)
│
├── LIQUIDATION_CDP/         # New category
│   └── ✨ NEW: Liquidation Threshold Manipulation
│   └── ✨ NEW: Health Factor Miscalculation
│   └── ✨ NEW: Oracle-Based Liquidation Trigger
│   └── ✨ NEW: Bad Debt Accumulation
│   └── ✨ NEW: Insolvency Due To Exchange Rate Manipulation
│   └── ✨ NEW: Liquidation Bounty Theft
│
├── ERC_STANDARDS/           # New category
│   ├── ERC20: approve race ✓ (mentioned)
│   └── ✨ NEW: ERC20: Missing Return Value
│   └── ✨ NEW: ERC20: Double Approval Race
│   └── ✨ NEW: ERC721: Missing safeTransferFrom Check
│   └── ✨ NEW: ERC1155: Unsafe Batch Operation
│   └── ✨ NEW: ERC4626: Inflation Attack (Vault share)
│   └── ✨ NEW: ERC4626: Preview Functions Mismatch
│   └── ✨ NEW: ERC777: Reentrancy Via Callback
│   └── ✨ NEW: ERC165: Interface Detection Bypass
│
├── BRIDGE_CROSSCHAIN/       # New category
│   └── ✨ NEW: Bridge Message Replay
│   └── ✨ NEW: Validator Set Manipulation
│   └── ✨ NEW: Light Client Verification Bypass
│   └── ✨ NEW: Relayer Front-Running
│   └── ✨ NEW: Wrapped Asset Double-Mint
│   └── ✨ NEW: Oracle Price Discrepancy Across Chains
│
├── YUL_ASSEMBLY/            # New category
│   └── ✨ NEW: Inline Assembly Memory Safety
│   └── ✨ NEW: MStore Overwrite
│   └── ✨ NEW: SLoad/SStore From Unchecked Index
│   └── ✨ NEW: Return Data Buffer Overread
│   └── ✨ NEW: Calldata Validation in Assembly
│   └── ✨ NEW: Free Memory Pointer Corruption
│
├── DEFI_PROTOCOLS/                    # Expanded — protocol-specific
│   ├── Lending Pool Reserve Manipulation ✓
│   ├── Borrow Cap Bypass ✓
│   ├── Liquidation Bonus Theft ✓
│   ├── Staking Reward Manipulation ✓
│   ├── Yield Aggregator Share Calculation ✓
│   ├── Vesting Schedule Bypass ✓
│   ├── Token Sale / ICO Manipulation ✓
│   ├── ✨ Aave: Borrow Cap Bypass via Flash Loan
│   ├── ✨ Aave: Reserve Factor Exploit
│   ├── ✨ Aave: Liquidation Threshold Manipulation (LT changes)
│   ├── ✨ Compound: seizeToken Bug (wrong asset seized)
│   ├── ✨ Compound: Interest Rate Model Manipulation
│   ├── ✨ Compound: COMP Distribution Exploit
│   ├── ✨ Uniswap V2: Donation Attack on LP Shares
│   ├── ✨ Uniswap V2: Sync Function Exploit (reserve manipulation)
│   ├── ✨ Uniswap V3: TWAP Oracle Manipulation (low liquidity ticks)
│   ├── ✨ Uniswap V3: Liquidity NFT Reentrancy
│   ├── ✨ Curve: Pool Imbalance Attack (EMA oracle lag)
│   ├── ✨ Curve: Amplification Coefficient Manipulation
│   ├── ✨ Curve: Base Pool Swap Price Deviation
│   ├── ✨ Balancer: Pool Weight Manipulation
│   ├── ✨ Balancer: Boosted Pool Share Calculation
│   ├── ✨ Balancer: Flash Loan Within Batch
│   ├── ✨ MakerDAO: Liquidation Auction Manipulation
│   ├── ✨ MakerDAO: Oracle Price Manipulation (OSM delay)
│   ├── ✨ MakerDAO: Surplus Auction Buyout
│   ├── ✨ Lido: stETH Depeg Cascading (curve pool drained)
│   ├── ✨ Lido: Withdrawal Queue Front-Running
│   ├── ✨ Euler: Bad Debt Via Liquidation Bug
│   ├── ✨ Euler: Donation Attack on Reserve
│   ├── ✨ Yearn: Strategy Switch Manipulation
│   ├── ✨ Yearn: Debt Allocation Exploit
│   ├── ✨ Convex: Reward Distribution Manipulation
│   ├── ✨ Convex: vlCVX Lock Manipulation
│   ├── ✨ Morpho: P2P Matching Rate Manipulation
│   └── ✨ Gearbox: Credit Account Reentrancy
│
├── BUSINESS_LOGIC/                    # Hardest category
│   ├── Timelock Order Manipulation ✓
│   ├── Emergency Stop Bypass ✓
│   ├── Blacklist/Whitelist Bypass ✓
│   ├── Fee Calculation Bypass ✓
│   ├── Rate Limiting Missing ✓
│   ├── Pausable Race Condition ✓
│   ├── ✨ Wrong Comparison Operator (>= vs >, <= vs <)
│   ├── ✨ Off-By-One Error in Array Bounds
│   ├── ✨ Wrong Variable Used in Condition (copy-paste bug)
│   ├── ✨ Uninitialized Return Value
│   ├── ✨ Missing Return Statement in Non-Void Function
│   ├── ✨ Wrong Constructor Name (Solidity <0.4.22 typo)
│   ├── ✨ Using tx.origin Instead of msg.sender
│   ├── ✨ Missing Zero-Address Validation on Critical Setters
│   ├── ✨ Missing Zero-Amount Validation
│   ├── ✨ Incorrect Inheritance Order Affecting Storage
│   ├── ✨ Missing Event Emission for Critical State Changes
│   ├── ✨ Function Parameter Not Validated
│   ├── ✨ Wrong Visibility (public vs external vs internal)
│   ├── ✨ Shadow Variable Declaration (local overrides state)
│   ├── ✨ Naming Collision Between Functions
│   ├── ✨ Incorrect Function Overloading Resolution
│   ├── ✨ State Variable Default Value Exploited
│   ├── ✨ Constant/Immutable Not Used for Fixed Values
│   ├── ✨ Unused State Variables (confusion + waste)
│   ├── ✨ Initial Supply Minted to Wrong Address
│   ├── ✨ Fee Destination Set to Zero Address
│   └── ✨ Token Recovery Function Missing (stuck funds)
│
├── NFT_SPECIFIC/                      # New category
│   ├── ✨ Floor Price Oracle Manipulation (NFT lending)
│   ├── ✨ Rarity Sniping / Trait Manipulation
│   ├── ✨ NFT Collateralization Ratio Exploit
│   ├── ✨ NFT Lending Liquidation Manipulation
│   ├── ✨ ERC721 safeTransferFrom Not Used (NFT stuck)
│   ├── ✨ ERC721 Reentrancy via onERC721Received
│   ├── ✨ ERC1155 Batch Transfer Reentrancy
│   ├── ✨ NFT Royalties Not Enforced on Secondary
│   ├── ✨ Metadata URL Centralization (rug risk)
│   ├── ✨ Token URI Manipulation (change after mint)
│   ├── ✨ Batch Mint Out-of-Gas Attack
│   ├── ✨ ERC721 Permit-Based Theft
│   ├── ✨ NFT Whitelist Bypass (presale mint)
│   ├── ✨ NFT Reveal Manipulation (see before others)
│   ├── ✨ Merkle Proof Bypass in Whitelist
│   ├── ✨ Signature-Based Mint Replay
│   ├── ✨ NFT Fractionalization Exploit
│   ├── ✨ Lazy Minting Exploit (mint after reveal)
│   └── ✨ NFT Airdrop Claim Front-Running
│
├── MEV_MEMPOOL/                       # New category
│   ├── ✨ Sandwich Attack on AMM Swap
│   ├── ✨ Front-Running on Auction Mechanism
│   ├── ✨ Back-Running on Liquidation
│   ├── ✨ JIT Liquidity Attack on AMM (just-in-time LP)
│   ├── ✨ Sniper Bot on Token Launch
│   ├── ✨ Gas Bidding War (priority gas auction)
│   ├── ✨ Bundle Ordering Manipulation
│   ├── ✨ Private Mempool Bypass (flashbots leak)
│   ├── ✨ Time-Bandit Attack (reorg to steal profit)
│   ├── ✨ On-Chain MEV Extraction (back-running own tx)
│   ├── ✨ Cross-Domain MEV (L1 → L2 arbitrage)
│   ├── ✨ Censorship Resistance Bypass
│   ├── ✨ DEX Slippage Protection Front-Run
│   └── ✨ Liquidation Sniper Bot Competition
│
├── COMPILER_DEPLOYMENT/              # New category
│   ├── ✨ Using Known Vulnerable Compiler Version
│   ├── ✨ Using Experimental Pragma
│   ├── ✨ abi.encodePacked with Variable-Length Types (hash collision)
│   ├── ✨ Unlocked Pragma (floating pragma ^0.8.0)
│   ├── ✨ Missing SPDX License Identifier
│   ├── ✨ Incompatible Compiler Versions Between Contracts
│   ├── ✨ Bytecode Verification Mismatch (deployed ≠ source)
│   ├── ✨ Constructor Arguments Not on Explorer
│   ├── ✨ Metadata Hash Mismatch (IPFS pinning)
│   ├── ✨ IR-Based Compilation Bugs (via-ir)
│   ├── ✨ Yul Optimizer Bug (known optimizer issues)
│   ├── ✨ Legacy Codegen vs New Codegen Differences
│   └── ✨ Solidity <=0.7.0 Named Return Parameter Bug
│
├── INFORMATION_DISCLOSURE/           # New category
│   ├── ✨ Private Data in Smart Contract (public storage)
│   ├── ✨ Unencrypted Secret on-Chain (password, key)
│   ├── ✨ Front-Running on Commit-Reveal (exposed secret)
│   ├── ✨ tx.origin Leak (phishing attack surface)
│   ├── ✨ Gas Estimation Leak (detect user params)
│   ├── ✨ Error Message Information Leak
│   ├── ✨ Event Emission of Sensitive Data
│   ├── ✨ Oracle Request/Response Exposure
│   └── ✨ Storage Collision Leaking Proxy Data
│
├── LAYER2_SCALING/                   # New category
│   ├── ✨ L2 → L1 Message Passing Vulnerabilities
│   ├── ✨ L1 → L2 Message Queue Manipulation
│   ├── ✨ Forced Transaction Inclusion on L2
│   ├── ✨ Sequencer Censorship / MEV on L2
│   ├── ✨ Rollup Fraud Proof Bypass
│   ├── ✨ Validium Data Availability Attack
│   ├── ✨ zk-Rollup Validity Proof Forgery
│   ├── ✨ Optimistic Rollup Challenge Period Manipulation
│   ├── ✨ L2 State Root Dispute Exploit
│   ├── ✨ Bridge Contract on L2 Not Upgradable
│   ├── ✨ Cross-L2 Bridge Vulnerabilities
│   ├── ✨ Blob/Bundle Transaction Ordering
│   ├── ✨ L2 Gas Price Manipulation
│   └── ✨ L2 Reorg Safety (finality delay)
│
├── ACCOUNT_ABSTRACTION/              # New category
│   ├── ✨ ERC-4337: UserOp Validation Bypass
│   ├── ✨ ERC-4337: Paymaster Reentrancy
│   ├── ✨ ERC-4337: Account Recovery Social Engineering
│   ├── ✨ ERC-4337: Signature Validation in EntryPoint
│   ├── ✨ ERC-4337: Nonce Management Exploit
│   ├── ✨ ERC-4337: Bundler Censorship
│   ├── ✨ ERC-4337: Aggregator Verification Bypass
│   ├── ✨ WalletConnect Session Manipulation
│   ├── ✨ Smart Wallet Upgrade Hijack
│   ├── ✨ Module-Based Wallet Vulnerability
│   ├── ✨ Social Recovery Backdoor
│   └── ✨ Multi-Sig Threshold Manipulation
│
├── WRAPPED_ASSETS_SYNTHETICS/        # New category
│   ├── ✨ Wrapped Asset Double-Spend
│   ├── ✨ Synthetic Asset Price Deviation
│   ├── ✨ Collateral Ratio Manipulation (synthetic)
│   ├── ✨ Liquidation of Synthetic Positions (manipulated)
│   ├── ✨ Mint/Burn Authorization Bypass
│   ├── ✨ Oracle Manipulation for Synth Price
│   ├── ✨ Wrapping/Unwrapping Race Condition
│   ├── ✨ Cross-Chain Wrapped Asset Depeg
│   ├── ✨ Wrapped Token Bridge Double-Mint
│   ├── ✨ Synthetix: sUSD Minting Exploit
│   └── ✨ Synthetic Asset Frozen/Blacklisted
│
├── INSURANCE_RISK/                   # New category
│   ├── ✨ Insurance Claim Manipulation
│   ├── ✨ Oracle Price for Claim Payout Exploit
│   ├── ✨ Cover Purchase Front-Running (buy before crash)
│   ├── ✨ Insurance Pool Depletion
│   ├── ✨ Claim Assessment Voting Manipulation
│   ├── ✨ Capital Provider Withdrawal Griefing
│   └── ✨ Coverage Period Manipulation
│
├── STAKING_VALIDATORS/              # New category
│   ├── ✨ Slashing Conditions Bypass
│   ├── ✨ Validator Key Management Vulnerability
│   ├── ✨ Delegation Power Concentration (centralization)
│   ├── ✨ Unbonding Period Manipulation
│   ├── ✨ Reward Calculation Error
│   ├── ✨ Commission Rate Manipulation
│   ├── ✨ Staking Derivatives Depeg (LSD)
│   ├── ✨ Staking Pool Withdrawal Queue Delay
│   ├── ✨ Liquid Staking Front-Running
│   ├── ✨ Validator Set Collusion
│   ├── ✨ MEV on Staked Assets
│   └── ✨ Re-staking (EigenLayer) Slashing Risk
│
├── GAS_ECONOMICS/                    # New category
│   ├── ✨ Block Gas Limit Manipulation
│   ├── ✨ Dynamic Fee Calculation Bypass (EIP-1559)
│   ├── ✨ Gas Token Minting/Burning Manipulation
│   ├── ✨ Storage Rent Attack (state bloat)
│   ├── ✨ State Size Inflation (DoS via storage)
│   ├── ✨ SELFDESTRUCT Gas Discrepancy (pre-EIP-6780)
│   ├── ✨ Difficulty Bomb Interaction
│   ├── ✨ Gas Estimation Manipulation (simulated vs real)
│   ├── ✨ Refund Manipulation (SSTORE clear + SELFDESTRUCT)
│   └── ✨ Base Fee Manipulation via Blob Gas
│
├── CROSS_CHAIN_EXPANDED/             # Expanded from BRIDGE_CROSSCHAIN
│   ├── ✨ Wormhole: Guardian Set Manipulation
│   ├── ✨ LayerZero: Endpoint Configuration Error
│   ├── ✨ LayerZero: Adapter Validation Bypass
│   ├── ✨ Axelar: Gateway Manipulation
│   ├── ✨ Axelar: Amplifier Verification Exploit
│   ├── ✨ CCMP: Message Ordering Manipulation
│   ├── ✨ Chain Reorg Attack on Bridge
│   ├── ✨ Validator Set Takeover on Bridge
│   ├── ✨ Light Client Spoofing (fraud proof)
│   ├── ✨ Merkle Proof Verification Bypass
│   ├── ✨ Relayer Collusion / Censorship
│   ├── ✨ Cross-Chain Flash Loan (multi-chain)
│   ├── ✨ Delayed Message Execution Exploit
│   ├── ✨ Cross-Chain Governance Attack
│   ├── ✨ Token Bridge Fee Manipulation
│   ├── ✨ Wrapped Asset Upgrade Discrepancy
│   └── ✨ Cross-Chain Replay Attack (CREATE2 same address)
│
├── EMERGING_THREATS/                 # New — bleeding edge
│   ├── ✨ ZK-Proof Verification Bypass (invalid proof accepted)
│   ├── ✨ ZK Circuit Vulnerability (under-constrained)
│   ├── ✨ ZK Nullifier Reuse
│   ├── ✨ TTF (Transfer Through Flash) Attack
│   ├── ✨ ERC-721/1155 ABI Encoding Attack
│   ├── ✨ ERC-2612 Permit Phishing (sign blind)
│   ├── ✨ Permit2 Infinite Approval Abuse
│   ├── ✨ EIP-2612 Flash Loan Permit
│   ├── ✨ Intent-Based Protocol Exploit (Anoma)
│   ├── ✨ Cross-Domain Intent Mismatch
│   ├── ✨ Blob Transaction Ordering Manipulation
│   ├── ✨ EOF (Ethereum Object Format) Contract Exploit
│   ├── ✨ ERC-6900 Modular Account Exploit
│   ├── ✨ ERC-7579 Modular Wallet Exploit
│   └── ✨ AI-Generated Contract Vulnerability
│
├── DEPENDENCY_SUPPLY_CHAIN/          # New category
│   ├── ✨ Malicious Dependency Injection
│   ├── ✨ Typosquatting Package (npm/PackageName)
│   ├── ✨ Compromised Dependency Upgrade
│   ├── ✨ Outdated Dependency with Known CVE
│   ├── ✨ Dependency Pin vs Floating Version
│   ├── ✨ Subgraph Dependency Tampering
│   ├── ✨ Hardhat/Foundry Plugin Vulnerability
│   ├── ✨ Contract Dependency on Unverified Imports
│   ├── ✨ Multiple Versions of Same Library
│   └── ✨ Unused Import (waste + attack surface)
│
├── FRONTEND_INTEGRATION/             # New category
│   ├── ✨ Incorrect Decimal Handling (18 vs 6 decimals)
│   ├── ✨ Token Address Mismatch (wrong token used)
│   ├── ✨ Swap Without Minimum Return (slippage = 0)
│   ├── ✨ Transaction Simulation Mismatch
│   ├── ✨ Off-Chain Signature Reuse Across dApps
│   ├── ✨ Domain Hash Collision Across Chains
│   ├── ✨ RPC endpoint manipulation (phishing RPC)
│   ├── ✨ Wallet Fingerprinting / Privacy Leak
│   ├── ✨ Permit Data Mismatch (front-end vs contract)
│   ├── ✨ Rate Limit Bypass (spam transactions)
│   └── ✨ Error Message Not Handled (silent fail)
│
└── PREDICTIVE_ANOMALY/               # New — ML-based (v3.0)
    ├── ✨ ML: Unusual External Call Frequency
    ├── ✨ ML: Abnormal Assembly Usage Pattern
    ├── ✨ ML: Suspicious Modifier Structure
    ├── ✨ ML: Inheritance Depth Anomaly
    ├── ✨ ML: State Variable Access Pattern
    ├── ✨ ML: Function Naming Similarity to Scams
    ├── ✨ ML: Honeypot Classification Model
    ├── ✨ ML: Rug Pull Predictor (liquidity lock, owner actions)
    ├── ✨ ML: Flash Loan Vulnerability Predictor
    └── ✨ ML: Zero-Day Exploit Precursor Detection
```

**Total target: 90+ pattern variants** (20 existing + 70+ new)

### 🗓️ Tasks
- [ ] Create `scanner/patterns/TAXONOMY.md` with full hierarchy
- [ ] Migrate existing 20 patterns into new category structure
- [ ] Write P21-P30 (first batch of new patterns: Reentrancy variants, Proxy attacks, DOS)
- [ ] Write P31-P40 (Token Economics: Honeypot, Fee-on-Transfer, EIP-4626)
- [ ] Write P41-P50 (Governance, Signatures, Crypto)
- [ ] Write P51-P60 (DeFi Protocols, CDP/Liquidation)
- [ ] Write P61-P70 (Assembly, Bridges, ERC Standards)
- [ ] Write P71-P80 (Business Logic, MEV)
- [ ] Add `category` and `subcategory` fields to YAML frontmatter
- [ ] Add `difficulty` field to each pattern (easy/medium/hard/expert)
- [ ] Add `requires_ast` boolean (true = needs AST analysis)
- [ ] Add `exploitability_estimate` (0.0-1.0)

---

## 🚧 v0.6 — AST-Based Analysis Engine 🧠

### 🎯 Goal: Move beyond regex — understand code structure

#### 🔧 Two-Phase Detection Architecture

```
┌──────────────────────────────────────┐
│        ScanEngine v2                 │
├──────────────────────────────────────┤
│                                      │
│  Phase 1: Regex (Quick)             │
│  ├── Scans source code with regex   │
│  ├── Covers all 90+ patterns        │
│  ├── Fast: 1000 contracts/min       │
│  └── Flags: ALL matches             │
│                                      │
│  Phase 2: AST (Deep)                │
│  ├── Parse Solidity → AST           │
│  ├── Build Control Flow Graph       │
│  ├── Build Call Graph               │
│  ├── Inheritance Chain Resolution   │
│  ├── Storage Layout Analysis        │
│  ├── Data Flow Analysis             │
│  └── Output: verified vulns only    │
│                                      │
│  Scoring: Regex flags × AST confirm │
│  = Confidence boost!                 │
└──────────────────────────────────────┘
```

#### 🛠️ Implementation Path

**Option A: Integrate Slither (Recommended)**
```python
from slither import Slither
from slither.core.declarations import FunctionContract

slither = Slither("contract.sol")
for contract in slither.contracts:
    for function in contract.functions:
        if function.is_constructor:
            # Check for missing initializer
        # etc.
```

**Why Slither:**
- ✅ Mature, maintained by Trail of Bits
- ✅ Full AST + CFG + inheritance resolution
- ✅ Built-in detectors we can call directly
- ✅ Python API (native integration)
- ✅ Supports Solidity 0.4.0 → 0.8.x

**Option B: Custom AST Parser (via py-solc-ast)**
```python
import solc_ast_parse
ast = solc_ast_parse.parse("contract.sol")
# Analyze AST nodes manually
```

**Why Custom:**
- ✅ No external dependency on Slither
- ✅ Lighter weight
- ✅ Can be optimized for batch scanning
- ❌ Need to rebuild wheel for every analysis type

**Decision:** Start with Slither integration, fallback to custom AST for chains where solc isn't available.

#### 🤖 New Pattern Types (AST-Only)

| Pattern | What AST gives us |
|---------|-------------------|
| Cross-function reentrancy | Call graph + state variable write analysis |
| Read-only reentrancy | View function → external call detection |
| Storage collision | Storage slot layout comparison across versions |
| Uninitialized state variables | Constructor analysis + default values |
| Inheritance poisoning | C3 linearization + override analysis |
| Access control on all paths | Control flow graph with require() analysis |
| Fee-on-transfer accounting | Balance check vs internal accounting comparison |
| Metamorphic contracts | selfdestruct + CREATE2 in same contract |

### 🗓️ Tasks
- [ ] Install & configure Slither (or solc-ast-parse)
- [ ] Create `scanner/ast_engine.py` — wraps Slither API
- [ ] Create `scanner/ast_detectors/` directory with AST-specific patterns
- [ ] Build call graph extractor (functions → external calls)
- [ ] Build storage layout analyzer (variable → slot mapping)
- [ ] Build inheritance chain resolver
- [ ] Build control flow graph (especially for reentrancy analysis)
- [ ] Create `_matches_ast()` method in pattern YAML for AST rules
- [ ] Phase 1 → Phase 2 confidence boost algorithm
- [ ] Test: Compare regex-only vs AST results on 100 real contracts
- [ ] Report: AST-detected vulnerabilities marked with 🧠 badge

---

## 🚧 v0.7 — Exploitability Scoring Engine 🎯

### 🎯 Goal: Not all vulns are equal — classify real risk

#### 🔥 Scoring Dimensions

```
EXPLOITABILITY SCORE = w₁·Access + w₂·Impact + w₃·Capital + w₄·Publicness
```

| Dimension | Weight | Values |
|-----------|--------|--------|
| **Access** | 0.35 | Public (1.0) / OnlyOwner (0.3) / OnlyRole (0.2) / Private (0.0) |
| **Impact** | 0.35 | Drain Funds (1.0) / Mint Tokens (0.9) / Freeze (0.7) / Revert (0.5) / Info (0.2) |
| **Capital** | 0.15 | None (1.0) / Small tx fee (0.8) / Flash loan (0.6) / Large capital (0.2) |
| **Publicness** | 0.15 | Known exploit (1.0) / Similar to known (0.7) / Theoretical (0.4) / Novel (0.1) |

#### 🏷️ Risk Classification

| Label | Score | Response |
|-------|-------|----------|
| 🔴 **CRITICAL_ACTIVE** | ≥ 0.85 | **IMMEDIATE:** Funds at risk, public exploit |
| 🟠 **CRITICAL_DORMANT** | ≥ 0.70 | **URGENT:** Exploitable but no funds or hard |
| 🟡 **HIGH_RESTRICTED** | ≥ 0.50 | **WARNING:** Requires owner or capital |
| 🔵 **MEDIUM_THEORETICAL** | ≥ 0.30 | **ADVISORY:** Complex path, low probability |
| ⚪ **LOW_INFO** | < 0.30 | **INFO:** Good practice issue |

#### 🧪 Scoring Pipeline

```
Raw Vuln (from regex/AST)
       │
       ▼
┌────────────────────┐
│ Access Analysis    │ ← Is function public? Read modifiers
├────────────────────┤
│ Impact Assessment  │ ← Can it drain? Mint? Freeze?
├────────────────────┤
│ Capital Estimate   │ ← How much ETH needed?
├────────────────────┤
│ Public Knowledge   │ ← Check known exploit DB
├────────────────────┤
│ FINAL SCORE        │ ← 0.0 - 1.0
└────────────────────┘
       │
       ▼
Risk Label + Actionable Recommendation
```

### 🗓️ Tasks
- [ ] Create `scanner/scoring/` package
- [ ] Implement `exploitability_score()` function
- [ ] Implement `access_analyzer()` (parse modifiers)
- [ ] Implement `impact_analyzer()` (parse function effects)
- [ ] Implement `capital_estimator()` (analyze call value)
- [ ] Implement `risk_classify()` (label assignment)
- [ ] Add `exploit_score` to Vulnerability dataclass
- [ ] Add `risk_label` field to Vulnerability
- [ ] Add "Why this score?" explanation in report
- [ ] Create scoring test suite (test against known CVEs)
- [ ] Add scoring to markdown/text report output

---

## 🚧 v0.8 — Economic Attack Simulator 🏦

### 🎯 Goal: Simulate flash loan + price manipulation attacks

This is **bleeding edge** — most scanners don't do this.

#### 🏗️ Architecture

```
Contract Source
       │
       ▼
┌─────────────────────────────┐
│ Extract Economic Parameters │
├─────────────────────────────┤
│ • AMM pool addresses        │
│ • Oracle price feeds        │
│ • Liquidity amounts         │
│ • Collateral ratios         │
│ • Swap fees                 │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   Agent-Based Simulator     │
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │ Attacker Agent        │  │ ← Flash loan + swap + exploit
│  └───────────────────────┘  │
│  ┌───────────────────────┐  │
│  │ Market Agent          │  │ ← AMM pool behavior
│  └───────────────────────┘  │
│  ┌───────────────────────┐  │
│  │ Oracle Agent          │  │ ← Price feed (TWAP/spot)
│  └───────────────────────┘  │
│  ┌───────────────────────┐  │
│  │ Contract Agent        │  │ ← Target contract behavior
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Simulation Result           │
├─────────────────────────────┤
│ • Profit if exploited?      │
│ • Capital required          │
│ • Steps to exploit          │
│ • Is it profitable? (gas+)  │
│ • Can it be mitigated?      │
└─────────────────────────────┘
```

#### 🧪 Simulation Scenarios

| Scenario | What It Tests |
|----------|---------------|
| **Flash Loan + Price Pump** | Borrow → swap → inflate price → use inflated price in target |
| **Flash Loan + Dump** | Borrow → swap → crash price → liquidate / profit from crash |
| **Multi-hop Arbitrage** | Route through 3+ pools to drain a protocol |
| **Oracle Stale Price** | Use old TWAP when current price differs |
| **Sandwich Attack** | Front-run a large swap, profit from slippage |
| **Liquidation Cascade** | Trigger multiple liquidations in sequence |
| **Donation Attack** | Inflate share price via direct transfer (EIP-4626) |

### 🗓️ Tasks
- [ ] Create `scanner/simulator/` package
- [ ] Implement `AMMSimulator` (Uniswap V2/V3, Curve, Balancer)
- [ ] Implement `FlashLoanSimulator` (borrow → do → repay)
- [ ] Implement `OracleSimulator` (TWAP, spot, Chainlink)
- [ ] Implement `ExploitAgent` (attacker behavior model)
- [ ] Create simulation config in YAML
- [ ] Implement profitability calculation (profit − gas − capital cost)
- [ ] Add simulation results to Vulnerability report
- [ ] Create: "This attack would profit ~$X, requiring ~$Y capital"
- [ ] Test against known exploits (use historical on-chain data)

---

## 🚧 v0.9 — ALL-Token Scanning Pipeline 🔄

### 🎯 Goal: Scan ALL tokens in registry efficiently

#### 📊 Priority Queue Architecture

```
Token Registry (10k+ tokens)
       │
       ▼
┌────────────────────────────┐
│    Scan Scheduler          │
├────────────────────────────┤
│                            │
│  🆕 NEW (Priority 1)       │ ← Never scanned before
│  │  └── Scan NOW           │
│  │                         │
│  🔴 VULNERABLE (P2)        │ ← Previously had vulns
│  │  └── Scan daily         │
│  │                         │
│  🔵 STABLE (P3)            │ ← Clean last 3 scans
│  │  └── Scan weekly        │
│  │                         │
│  ⚪ STALE (P4)             │ ← Old, no activity
│     └── Scan monthly       │
│                            │
└────────────────────────────┘
       │
       ▼
Per-Chain Rate Limiter
       │
       ▼
Batch Executor (50 contracts / batch)
```

#### ⚡ Optimizations

| Optimization | Speedup | Details |
|-------------|---------|---------|
| **Skip unverified** | 5x | 80% of tokens have no source code |
| **Codehash cache** | 10x | Don't re-fetch if bytecode hasn't changed |
| **Parallel chains** | 24x | Scan all chains simultaneously |
| **Parallel contracts** | 5x | Scan 5 contracts per chain in parallel |
| **Batch Ethereum RPC** | 3x | Batch eth_call requests |
| **Token metadata cache** | 2x | Don't re-fetch symbol/name if known |

**Total estimated speedup: 36,000x** (from 350 tokens/day → 12,600 tokens/day)

#### 📈 Daily Capacity

| Chain | Contracts/Day | Notes |
|-------|--------------|-------|
| Ethereum | 3,600 | 5 req/s, 86% unverified → 504 verified/day |
| BNB | 5,400 | 7.5 req/s, 80% unverified → 1,080 verified/day |
| Polygon | 5,400 | Same as BNB |
| Base | 3,600 | Same as Ethereum |
| Other (20 chains) | 2,000 each | 4-8 req/s, 60-90% unverified |
| **Total** | **~60,000/day** | **30,000-50,000 verified sources scanned daily** |

### 🗓️ Tasks
- [ ] Implement priority-based scheduler
- [ ] Implement codehash comparison (skip unchanged)
- [ ] Implement parallel chain scanning
- [ ] Implement per-chain rate limiter (auto-adjusting)
- [ ] Implement scan state persistence (SQLite or JSON)
- [ ] Implement incremental daily scan (new tokens first)
- [ ] Add daily summary: "Scanned X new, found Y vulns, Z still vulnerable"
- [ ] Add health metrics to dashboard (scans/day, avg time, error rate)

---

## 🚧 v1.0 — Alerting & Intelligence Hub 📡

### 🎯 Goal: Real-time alerts + public API

#### 🚨 Alert Channels

| Channel | Critical | High | Medium | Daily Digest |
|---------|----------|------|--------|-------------|
| **GitHub Issues** | ✅ Red Flag | ✅ Advisory | ❌ | ✅ Weekly |
| **Telegram** | ✅ Instant | ✅ Instant | ❌ | ✅ Daily |
| **Discord** | ✅ Instant | ✅ Instant | ❌ | ✅ Daily |
| **Email** | ✅ | ❌ | ❌ | ✅ Weekly |
| **Webhook** | ✅ | ✅ | ❌ | ❌ |

#### 🌐 Public API

```
GET /v1/scan/{chain}/{address}
  → { vulns, score, timestamp, chain }

GET /v1/chain/{chain}/vulns
  → { total, critical, high, tokens: [...] }

GET /v1/stats
  → { total_scanned, total_vulns, chains, timeline }

GET /v1/token/{chain}/{address}/history
  → { scans: [{timestamp, vulns, score}] }
```

#### 🤖 Telegram Bot Features

- `/scan <address>` — Instant scan of any contract
- `/chain <chain>` — Chain health report
- `/alert <address>` — Subscribe to vuln alerts
- `/top` — Top 10 riskiest contracts right now
- `/stats` — Global scanner statistics

### 🗓️ Tasks
- [ ] Create Telegram bot integration (async)
- [ ] Create Discord webhook integration
- [ ] Create `scanner/alerts/` package
- [ ] Implement alert filtering (by severity, chain, pattern)
- [ ] Implement digest generation (daily/weekly)
- [ ] Create FastAPI-based REST API
- [ ] Add API key authentication
- [ ] Deploy API to Vercel/Railway
- [ ] Add API documentation (OpenAPI)

---

## 🚧 v1.5 — GitHub Pages Dashboard 🚀

### 🎯 Goal: Display scan results on GitHub Pages

> Like Kesra's web-deploy.yml — auto-deploy static dashboard

#### 🖥️ Dashboard Features

| Feature | Data Source | Tech |
|---------|------------|------|
| Vulnerability stats | scan results JSON | HTML/CSS (static) |
| Per-chain breakdown | chain registry | Chart.js or pure CSS |
| Token search | token_registry.json | JavaScript filter |
| Risk leaderboard | scored results | Table + color coding |
| Trend chart | historical results | Chart.js |
| Badge generator | live SVG | Server-side or shields.io |
| Map view | chain explorer | Leaflet.js (geo map) |

#### 📁 Files

```
docs/
├── index.html              ← Main dashboard
├── dashboard.json          ← Live data (auto-generated)
├── chains/
│   ├── ethereum.md         ← Per-chain reports
│   ├── bnb.md
│   └── ...                 ← 24 chain reports
├── tokens/
│   └── 0x1234...5678.md    ← Per-token reports (high vulns only)
└── assets/
    ├── style.css
    └── script.js
```

### 🗓️ Tasks
- [ ] Create interactive HTML dashboard with filtering
- [ ] Add chain explorer cards (24 chains with status)
- [ ] Add token search bar with autocomplete
- [ ] Add trend chart (vulns discovered over time)
- [ ] Add risk leaderboard (top 20 riskiest contracts)
- [ ] Generate dashboard as part of daily scan
- [ ] Deploy via GitHub Pages (Actions)
- [ ] Add dashboard badge to README

---

## 🚧 v2.0 — Non-EVM Support 🌍

### 🎯 Goal: Beyond Ethereum — scan ALL chains

#### 🔗 Chain Support Matrix

| Chain Type | Status | Notes |
|-----------|--------|-------|
| **EVM (24 chains)** | ✅ v0.2 | Ethereum, BNB, Polygon, etc. |
| **Solana** | ❌ v2.0 | BPF bytecode, Anchor framework |
| **Bitcoin** | ❌ v2.0 | Script analysis, ordinals, BRC-20 |
| **TON** | ❌ v2.0 | FunC, TVM bytecode |
| **StarkNet** | ❌ v2.0 | Cairo, Sierra |
| **zkSync** | ❌ v2.0 | EraVM, LLVM IR |
| **Aptos/Sui** | ❌ v2.0 | Move language, different VM |
| **Cosmos** | ❌ v2.0 | CosmWasm, Go SDK |
| **Polkadot** | ❌ v2.0 | Ink!, WASM |
| **Near** | ❌ v2.0 | Rust/AssemblyScript |

#### 🏛️ Abstract Scanner Architecture

```
┌──────────────────────────────────────┐
│           ScanEngine v3              │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐    │
│  │   Source Fetcher (Abstract)  │    │
│  ├──────────────────────────────┤    │
│  │ EVM: Etherscan / Blockscout  │    │
│  │ Solana: Solscan / SolanaFM   │    │
│  │ TON: TonViewer / TonAPI      │    │
│  │ Cosmos: MintScan / PingPub   │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │   Pattern Engine (Abstract)  │    │
│  ├──────────────────────────────┤    │
│  │ EVM: Solidity regex + AST    │    │
│  │ Solana: Rust/Anchor patterns │    │
│  │ TON: FunC patterns           │    │
│  │ Cosmos: Go/Rust patterns     │    │
│  └──────────────────────────────┘    │
│                                      │
│  ┌──────────────────────────────┐    │
│  │   Vulnerability Taxonomy     │    │
│  │   (Chain-Agnostic)           │    │
│  ├──────────────────────────────┤    │
│  │ Reentrancy → All chains      │    │
│  │ Overflow → All chains        │    │
│  │ Access Control → All chains  │    │
│  │ Economic → EVM + Solana      │    │
│  └──────────────────────────────┘    │
│                                      │
└──────────────────────────────────────┘
```

### 🗓️ Tasks
- [ ] Define chain-agnostic vulnerability taxonomy
- [ ] Create abstract `SourceFetcher` base class
- [ ] Create abstract `PatternEngine` base class
- [ ] Implement Solana scanner (Rust/Anchor analysis)
- [ ] Implement TON scanner (FunC analysis)
- [ ] Implement Cosmos scanner (CosmWasm analysis)
- [ ] Create unified reporting format chain-agnostic
- [ ] Map chain-specific vulns to universal taxonomy
- [ ] Add cross-chain vulnerability correlation

---

## 🚧 v3.0 — Guardian Network 👁️🌐

### 🎯 Goal: Decentralized, community-driven vulnerability detection

#### 🤝 Community Pattern Marketplace

```
Community Members
       │
       ├── Submit Pattern (YAML + test)
       │       │
       │       ▼
       │   Pattern Review (automated + community)
       │       │
       │       ├── ✅ Approved → registry
       │       └── ❌ Rejected → feedback
       │
       └── Submit Contract for Scanning
               │
               ▼
           Queue → Scan → Report
```

#### 🏛️ DAO Governance (Optional)

| Feature | Description |
|---------|-------------|
| Pattern voting | Community votes on new patterns |
| Severity calibration | Community sets severity levels |
| Bounty pool | Rewards for finding new vulns |
| Guardian staking | Stake MAAT tokens to run a node |

#### 🧠 ML-Powered Anomaly Detection

```
Historical Scan Data (100k+ contracts)
       │
       ▼
┌──────────────────────────────┐
│    Feature Extraction        │
├──────────────────────────────┤
│ • Function count vs avg      │
│ • External call density      │
│ • Modifier-to-function ratio │
│ • Storage variable count     │
│ • Inheritance depth          │
│ • Comment-to-code ratio      │
│ • Assembly block frequency   │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│    Isolation Forest / AE     │
├──────────────────────────────┤
│  Anomaly Score > threshold   │
│       → "This contract looks │
│          suspicious"         │
└──────────────────────────────┘
       │
       ▼
Manual Review Recommended
```

#### 🚀 v3.0 Features

- [ ] Community pattern marketplace
- [ ] Pattern review workflow (CI + community)
- [ ] Guardian node software (Docker image)
- [ ] Distributed scanning network
- [ ] Real-time mempool monitoring
- [ ] ML anomaly detection pipeline
- [ ] ZK-proof verification analysis
- [ ] Formal verification integration (certora, scribble)
- [ ] Cross-chain bridge vulnerability scanner
- [ ] MEV attack vector detection
- [ ] DeFi composability risk analysis
- [ ] Zero-day exploit prediction

---

## 📊 Milestone Summary Timeline

| Version | Focus | Patterns | Detection | Chains | Timeline |
|---------|-------|----------|-----------|--------|----------|
| ✅ v0.1 | Foundation | 20 | Regex | 1 | Done |
| ✅ v0.2 | Multi-Chain | 20 | Regex | 24 | Done |
| ✅ v0.3 | Daily Scan | 20 | Regex | 24 | Done |
| ✅ v0.4 | Token Discovery | 20 | Regex | 24 | Done |
| 🔥 **v0.5** | **Pattern Explosion** | **60+** | **Regex+** | **24** | **Current** |
| 🔥 **v0.6** | **AST Analysis** | **60+** | **Regex+AST** | **24** | **Next** |
| 🚧 v0.7 | Exploitability Scoring | 70+ | R+AST | 24 | Soon |
| 🚧 v0.8 | Economic Simulator | 80+ | R+AST+Econ | 7 | Soon |
| 🚧 v0.9 | All-Token Pipeline | 80+ | R+AST+Econ | 24 | Soon |
| 🚧 v1.0 | Alerts & API | 90+ | Full | 24 | Future |
| 🚧 v1.5 | Dashboard | 90+ | Full | 24 | Future |
| 🚧 v2.0 | Non-EVM | 100+ | Full | 7+ | Future |
| 🚧 v3.0 | Guardian Network | 150+ | ML+Full | All | Future |

---

## 📋 Priority Matrix (What To Do First)

| Priority | What | Effort | Impact | Why Now |
|----------|------|--------|--------|---------|
| **🔴 P0** | 10 new patterns (P21-P30) | Medium | 🚀🚀🚀 | Builds on existing regex infra |
| **🔴 P0** | Reentrancy variants (cross-function, read-only) | Medium | 🚀🚀🚀 | Most critical vuln class |
| **🟡 P1** | Slither integration | High | 🚀🚀🚀🚀 | Unlocks AST-based analysis |
| **🟡 P1** | Exploitability scoring | Medium | 🚀🚀🚀 | Filters noise, shows real risk |
| **🟡 P1** | Codehash + skip unchanged | Medium | 🚀🚀 | 10x speedup |
| **🔵 P2** | Priority-based scan scheduler | Medium | 🚀🚀 | Scale to 10k+ tokens |
| **🔵 P2** | Token economics patterns (P31-P40) | Medium | 🚀🚀🚀 | Honeypot, fee-on-transfer |
| **🔵 P2** | Governance + crypto patterns (P41-P50) | Medium | 🚀🚀 | DAO attacks |
| **🟢 P3** | Economic simulator | High | 🚀🚀🚀🚀 | Differentiator |
| **🟢 P3** | Telegram alerts | Low | 🚀🚀 | User engagement |
| **🟢 P3** | GitHub Pages dashboard | Low | 🚀🚀 | Visibility |
| **⚪ P4** | Non-EVM chains | Huge | 🚀🚀🚀🚀🚀 | Market expansion |
| **⚪ P4** | ML anomaly detection | Huge | 🚀🚀🚀🚀 | Next-gen |

---

## 🧠 Key Technical Decisions

### ✅ YES: Slither Integration (v0.6)
- Battle-tested by Trail of Bits
- Full AST + CFG + inheritance
- Easy Python API
- 100+ existing detectors we can leverage

### ❌ NO: Mythril/Manticore (for now)
- Symbolic execution is SLOW (minutes per contract)
- We need speed for 10k+ contracts
- Revisit in v2.0 for targeted deep analysis

### ✅ YES: YAML Pattern Format (extend existing)
- Add `category`, `subcategory` fields
- Add `requires_ast` boolean
- Add `exploit_estimate` float
- Keep backward compatibility

### ✅ YES: Score-Based Report Filtering
- Critical/Active ≥ 0.85 → Red Flag Issue
- Critical/Dormant ≥ 0.70 → Alert
- Everything else → Report only
- User can set custom threshold

### ❌ NO: Full-Time Mempool Monitoring (v3.0)
- Too expensive for solo dev
- Revisit when we have community nodes

---

<p align="center">
  <i>حرية فلسطين — فلسطين حرة عربية</i> 🇵🇸
</p>
