# 🏛️ MaatEye — Vulnerability Pattern Taxonomy

> *"The Eye of Ma'at sees all — nothing escapes the feather of truth."*

## 📋 Overview

This document defines the full hierarchical taxonomy for all vulnerability patterns in MaatEye. Each pattern belongs to exactly one category and one subcategory. Pattern IDs are allocated in ranges to allow growth without renumbering.

---

## 🗂️ Category Summary

| Category | Existing Patterns | New (Planned) | Total |
|----------|-------------------|---------------|-------|
| `ACCESS_CONTROL` | P01, P02, P05, P14, P18 | +4 | 9 |
| `REENTRANCY` | P03 | +8 | 9 |
| `ARITHMETIC` | P04 | +6 | 7 |
| `PROXY_UPGRADEABLE` | P08, P16 | +7 | 9 |
| `EXTERNAL_CALLS` | P06, P07, P17 | +6 | 9 |
| `TOKEN_ECONOMICS` | P10, P11 | +8 | 10 |
| `GOVERNANCE` | P13 | +6 | 7 |
| `SIGNATURE_CRYPTO` | P12 | +7 | 8 |
| `DOS_GAS` | — | +7 | 7 |
| `LIQUIDATION_CDP` | — | +6 | 6 |
| `ERC_STANDARDS` | P19 | +7 | 8 |
| `BRIDGE_CROSSCHAIN` | — | +6 | 6 |
| `YUL_ASSEMBLY` | — | +6 | 6 |
| `DEFI_PROTOCOLS` | — | +34 | 34 |
| `BUSINESS_LOGIC` | P09, P15, P20 | +28 | 31 |
| `NFT_SPECIFIC` | — | +19 | 19 |
| `MEV_MEMPOOL` | — | +14 | 14 |
| `COMPILER_DEPLOYMENT` | — | +13 | 13 |
| `INFORMATION_DISCLOSURE` | — | +9 | 9 |
| `LAYER2_SCALING` | — | +14 | 14 |
| `ACCOUNT_ABSTRACTION` | — | +12 | 12 |
| `WRAPPED_ASSETS_SYNTHETICS` | — | +11 | 11 |
| `INSURANCE_RISK` | — | +7 | 7 |
| `STAKING_VALIDATORS` | — | +12 | 12 |
| `GAS_ECONOMICS` | — | +10 | 10 |
| `CROSS_CHAIN_EXPANDED` | — | +17 | 17 |
| `EMERGING_THREATS` | — | +15 | 15 |
| `DEPENDENCY_SUPPLY_CHAIN` | — | +10 | 10 |
| `FRONTEND_INTEGRATION` | — | +11 | 11 |
| `PREDICTIVE_ANOMALY` | — | +10 | 10 |

---

## 🌳 Full Hierarchy

### 1️⃣ ACCESS_CONTROL (ID: P01–P09)
*Unauthorized access to critical functions*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Unprotected Mint** | P01 | — |
| **tx.origin Auth** | P05 | — |
| **Missing Access Control** | P02, P18 | — |
| **Unsafe Ownership Renounce** | P14 | — |
| **Unprotected Initializer** | — | ✨ P21 |
| **Role Admin Hijack** | — | ✨ P22 |
| **Ownership Transfer Without Two-Step** | — | ✨ P23 |
| **Pausable Without Unpause Guard** | — | ✨ P24 |

### 2️⃣ REENTRANCY (ID: P10–P19)
*Reentrant call attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Classic Reentrancy** | P03 | — |
| **Cross-Function Reentrancy** | — | ✨ P10 |
| **Read-Only Reentrancy** | — | ✨ P11 |
| **Cross-Contract Reentrancy** | — | ✨ P12 |
| **ERC721 Callback Reentrancy** | — | ✨ P13 |
| **ERC1155 Batch Reentrancy** | — | ✨ P14 |
| **Reentrancy Via Fallback** | — | ✨ P15 |
| **Flash Loan Reentrancy Bridge** | — | ✨ P16 |

### 3️⃣ ARITHMETIC (ID: P20–P29)
*Integer overflow, underflow, and precision bugs*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Integer Overflow** | P04 | — |
| **Precision Loss (Division Before Multiplication)** | — | ✨ P20 |
| **Rounding in Favor of Wrong Party** | — | ✨ P21 |
| **Fee Calculation Exploit** | — | ✨ P22 |
| **Share Price Manipulation (EIP-4626)** | — | ✨ P23 |
| **Rebasing Token Accounting Mismatch** | — | ✨ P24 |
| **Batch Transfer Overflow** | — | ✨ P25 |

### 4️⃣ PROXY_UPGRADEABLE (ID: P30–P39)
*Proxy and upgradeable contract vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Storage Collision** | P08 | — |
| **Uninitialized Proxy** | P16 | — |
| **Metamorphic Contract (selfdestruct + CREATE2)** | — | ✨ P30 |
| **Implementation Selfdestruct** | — | ✨ P31 |
| **Constructor in Implementation** | — | ✨ P32 |
| **Function Clashing** | — | ✨ P33 |
| **UUPS Without Upgrade Guard** | — | ✨ P34 |
| **Beacon Proxy Without Upgrade Auth** | — | ✨ P35 |
| **Proxy Admin Takeover** | — | ✨ P36 |

### 5️⃣ EXTERNAL_CALLS (ID: P40–P49)
*Unsafe external call handling*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Arbitrary Delegatecall** | P07 | — |
| **Arbitrary External Call** | P17 | — |
| **Unchecked Call Return** | P06 | — |
| **Contract Existence Check Missing** | — | ✨ P40 |
| **Gas Stipend Dependency** | — | ✨ P41 |
| **Delegatecall to Untrusted Library** | — | ✨ P42 |
| **Staticcall With Side Effects** | — | ✨ P43 |
| **CREATE2 Address Collision** | — | ✨ P44 |

### 6️⃣ TOKEN_ECONOMICS (ID: P50–P59)
*Token-level economic attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Flash Loan Vector** | P11 | — |
| **Oracle Manipulation** | P10 | — |
| **Honeypot Detection** | — | ✨ P50 |
| **Fee-On-Transfer Accounting Mismatch** | — | ✨ P51 |
| **Deflationary Token Balance Change** | — | ✨ P52 |
| **ERC4626 Vault Share Manipulation** | — | ✨ P53 |
| **Liquidity Pool Imbalance** | — | ✨ P54 |
| **MEV Sandwich Vulnerability** | — | ✨ P55 |
| **Slippage Protection Missing** | — | ✨ P56 |
| **Deadline Missing in Swaps** | — | ✨ P57 |

### 7️⃣ GOVERNANCE (ID: P60–P69)
*DAO and governance system attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Governance Attack** | P13 | — |
| **Flash Loan Governance Takeover** | — | ✨ P60 |
| **Low Quorum / Low Proposal Threshold** | — | ✨ P61 |
| **Timelock Bypass** | — | ✨ P62 |
| **Voter Delegation Attack** | — | ✨ P63 |
| **Proposal Front-Running** | — | ✨ P64 |
| **Cancel/Execute Race Condition** | — | ✨ P65 |

### 8️⃣ SIGNATURE_CRYPTO (ID: P70–P79)
*Signature and cryptographic vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Signature Replay** | P12 | — |
| **EIP-2612 Permit Front-Running** | — | ✨ P70 |
| **EIP-712 Domain Separator Mismatch** | — | ✨ P71 |
| **Signature Malleability (ecrecover)** | — | ✨ P72 |
| **Missing Nonce Increment** | — | ✨ P73 |
| **Cross-Chain Replay (missing chainId)** | — | ✨ P74 |
| **Weak PRNG** | — | ✨ P75 |
| **Predictable Randomness in Gambling** | — | ✨ P76 |

### 9️⃣ DOS_GAS (ID: P80–P89)
*Denial of Service and gas-related attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Gas Griefing (unbounded loop)** | — | ✨ P80 |
| **Block Gas Limit (array iteration)** | — | ✨ P81 |
| **DoS via Selfdestruct** | — | ✨ P82 |
| **DoS via Block Stuffing** | — | ✨ P83 |
| **Unexpected Revert in Pull-Over-Push** | — | ✨ P84 |
| **Fallback Function Gas Exhaustion** | — | ✨ P85 |
| **Large Array Deletion** | — | ✨ P86 |

### 🔟 LIQUIDATION_CDP (ID: P90–P99)
*Lending and CDP liquidation attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Liquidation Threshold Manipulation** | — | ✨ P90 |
| **Health Factor Miscalculation** | — | ✨ P91 |
| **Oracle-Based Liquidation Trigger** | — | ✨ P92 |
| **Bad Debt Accumulation** | — | ✨ P93 |
| **Insolvency Due To Exchange Rate Manipulation** | — | ✨ P94 |
| **Liquidation Bounty Theft** | — | ✨ P95 |

### 1️⃣1️⃣ ERC_STANDARDS (ID: P100–P109)
*ERC token standard compliance issues*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Missing SafeERC20** | P19 | — |
| **ERC20: Missing Return Value** | — | ✨ P100 |
| **ERC20: Double Approval Race** | — | ✨ P101 |
| **ERC721: Missing safeTransferFrom Check** | — | ✨ P102 |
| **ERC1155: Unsafe Batch Operation** | — | ✨ P103 |
| **ERC4626: Inflation Attack** | — | ✨ P104 |
| **ERC4626: Preview Functions Mismatch** | — | ✨ P105 |
| **ERC777: Reentrancy Via Callback** | — | ✨ P106 |
| **ERC165: Interface Detection Bypass** | — | ✨ P107 |

### 1️⃣2️⃣ BRIDGE_CROSSCHAIN (ID: P110–P119)
*Cross-chain bridge vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Bridge Message Replay** | — | ✨ P110 |
| **Validator Set Manipulation** | — | ✨ P111 |
| **Light Client Verification Bypass** | — | ✨ P112 |
| **Relayer Front-Running** | — | ✨ P113 |
| **Wrapped Asset Double-Mint** | — | ✨ P114 |
| **Oracle Price Discrepancy Across Chains** | — | ✨ P115 |

### 1️⃣3️⃣ YUL_ASSEMBLY (ID: P120–P129)
*Inline assembly and low-level vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Inline Assembly Memory Safety** | — | ✨ P120 |
| **MStore Overwrite** | — | ✨ P121 |
| **SLoad/SStore From Unchecked Index** | — | ✨ P122 |
| **Return Data Buffer Overread** | — | ✨ P123 |
| **Calldata Validation in Assembly** | — | ✨ P124 |
| **Free Memory Pointer Corruption** | — | ✨ P125 |

### 1️⃣4️⃣ DEFI_PROTOCOLS (ID: P130–P169)
*Protocol-specific vulnerability patterns*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Lending Pool Reserve Manipulation** | — | ✨ P130 |
| **Borrow Cap Bypass** | — | ✨ P131 |
| **Liquidation Bonus Theft** | — | ✨ P132 |
| **Staking Reward Manipulation** | — | ✨ P133 |
| **Yield Aggregator Share Calculation** | — | ✨ P134 |
| **Vesting Schedule Bypass** | — | ✨ P135 |
| **Token Sale / ICO Manipulation** | — | ✨ P136 |
| **Aave-specific** | — | ✨ P137–P139 |
| **Compound-specific** | — | ✨ P140–P142 |
| **Uniswap V2/V3-specific** | — | ✨ P143–P145 |
| **Curve-specific** | — | ✨ P146–P148 |
| **Balancer-specific** | — | ✨ P149–P151 |
| **MakerDAO-specific** | — | ✨ P152–P154 |
| **Lido-specific** | — | ✨ P155–P156 |
| **Euler-specific** | — | ✨ P157–P158 |
| **Yearn-specific** | — | ✨ P159–P160 |
| **Convex-specific** | — | ✨ P161–P162 |
| **Morpho-specific** | — | ✨ P163 |
| **Gearbox-specific** | — | ✨ P164 |

### 1️⃣5️⃣ BUSINESS_LOGIC (ID: P170–P199)
*General business logic flaws*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Missing Input Validation** | P09 | — |
| **Wrong Visibility** | P15 | — |
| **Timestamp Dependence** | P20 | — |
| **Timelock Order Manipulation** | — | ✨ P170 |
| **Emergency Stop Bypass** | — | ✨ P171 |
| **Blacklist/Whitelist Bypass** | — | ✨ P172 |
| **Fee Calculation Bypass** | — | ✨ P173 |
| **Rate Limiting Missing** | — | ✨ P174 |
| **Pausable Race Condition** | — | ✨ P175 |
| **Wrong Comparison Operator** | — | ✨ P176 |
| **Off-By-One Error** | — | ✨ P177 |
| **Wrong Variable in Condition** | — | ✨ P178 |
| **Uninitialized Return Value** | — | ✨ P179 |
| **Missing Return Statement** | — | ✨ P180 |
| **Wrong Constructor Name** | — | ✨ P181 |
| **Missing Zero-Address Validation** | — | ✨ P182 |
| **Missing Zero-Amount Validation** | — | ✨ P183 |
| **Incorrect Inheritance Order** | — | ✨ P184 |
| **Missing Event Emission** | — | ✨ P185 |
| **Function Parameter Not Validated** | — | ✨ P186 |
| **Shadow Variable Declaration** | — | ✨ P187 |
| **Naming Collision Between Functions** | — | ✨ P188 |
| **Incorrect Function Overloading** | — | ✨ P189 |
| **State Variable Default Value Exploit** | — | ✨ P190 |
| **Constant/Immutable Not Used** | — | ✨ P191 |
| **Unused State Variables** | — | ✨ P192 |
| **Initial Supply Wrong Address** | — | ✨ P193 |
| **Fee Destination Zero Address** | — | ✨ P194 |
| **Token Recovery Function Missing** | — | ✨ P195 |

### 1️⃣6️⃣ NFT_SPECIFIC (ID: P200–P219)
*NFT-specific vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Floor Price Oracle Manipulation** | — | ✨ P200 |
| **Rarity Sniping / Trait Manipulation** | — | ✨ P201 |
| **NFT Collateralization Ratio Exploit** | — | ✨ P202 |
| **NFT Lending Liquidation Manipulation** | — | ✨ P203 |
| **ERC721 safeTransferFrom Not Used** | — | ✨ P204 |
| **ERC721 Reentrancy via onERC721Received** | — | ✨ P205 |
| **ERC1155 Batch Transfer Reentrancy** | — | ✨ P206 |
| **NFT Royalties Not Enforced** | — | ✨ P207 |
| **Metadata URL Centralization** | — | ✨ P208 |
| **Token URI Manipulation** | — | ✨ P209 |
| **Batch Mint Out-of-Gas Attack** | — | ✨ P210 |
| **ERC721 Permit-Based Theft** | — | ✨ P211 |
| **NFT Whitelist Bypass** | — | ✨ P212 |
| **NFT Reveal Manipulation** | — | ✨ P213 |
| **Merkle Proof Bypass** | — | ✨ P214 |
| **Signature-Based Mint Replay** | — | ✨ P215 |
| **NFT Fractionalization Exploit** | — | ✨ P216 |
| **Lazy Minting Exploit** | — | ✨ P217 |
| **NFT Airdrop Claim Front-Running** | — | ✨ P218 |

### 1️⃣7️⃣ MEV_MEMPOOL (ID: P220–P229)
*Mempool and MEV attack vectors*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Sandwich Attack on AMM Swap** | — | ✨ P220 |
| **Front-Running on Auction** | — | ✨ P221 |
| **Back-Running on Liquidation** | — | ✨ P222 |
| **JIT Liquidity Attack** | — | ✨ P223 |
| **Sniper Bot on Token Launch** | — | ✨ P224 |
| **Gas Bidding War** | — | ✨ P225 |
| **Bundle Ordering Manipulation** | — | ✨ P226 |
| **Private Mempool Bypass** | — | ✨ P227 |
| **Time-Bandit Attack** | — | ✨ P228 |
| **On-Chain MEV Extraction** | — | ✨ P229 |

### 1️⃣8️⃣ COMPILER_DEPLOYMENT (ID: P230–P239)
*Compiler and deployment configuration issues*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Vulnerable Compiler Version** | — | ✨ P230 |
| **Experimental Pragma** | — | ✨ P231 |
| **abi.encodePacked Hash Collision** | — | ✨ P232 |
| **Unlocked Pragma** | — | ✨ P233 |
| **Missing SPDX License** | — | ✨ P234 |
| **Incompatible Compiler Versions** | — | ✨ P235 |
| **Bytecode Verification Mismatch** | — | ✨ P236 |
| **Constructor Arguments Not on Explorer** | — | ✨ P237 |
| **Metadata Hash Mismatch** | — | ✨ P238 |
| **IR-Based Compilation Bugs** | — | ✨ P239 |

### 1️⃣9️⃣ INFORMATION_DISCLOSURE (ID: P240–P249)
*Information leakage vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Private Data in Contract** | — | ✨ P240 |
| **Unencrypted Secret On-Chain** | — | ✨ P241 |
| **Front-Running on Commit-Reveal** | — | ✨ P242 |
| **tx.origin Leak** | — | ✨ P243 |
| **Gas Estimation Leak** | — | ✨ P244 |
| **Error Message Information Leak** | — | ✨ P245 |
| **Event Emission of Sensitive Data** | — | ✨ P246 |
| **Oracle Request/Response Exposure** | — | ✨ P247 |
| **Storage Collision Leaking Proxy Data** | — | ✨ P248 |

### 2️⃣0️⃣ LAYER2_SCALING (ID: P250–P259)
*L2-specific vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **L2 → L1 Message Passing** | — | ✨ P250 |
| **L1 → L2 Message Queue Manipulation** | — | ✨ P251 |
| **Forced Transaction Inclusion** | — | ✨ P252 |
| **Sequencer Censorship / MEV** | — | ✨ P253 |
| **Rollup Fraud Proof Bypass** | — | ✨ P254 |
| **Validium Data Availability Attack** | — | ✨ P255 |
| **zk-Rollup Validity Proof Forgery** | — | ✨ P256 |
| **Optimistic Rollup Challenge Manipulation** | — | ✨ P257 |
| **L2 State Root Dispute** | — | ✨ P258 |
| **Cross-L2 Bridge Vulnerabilities** | — | ✨ P259 |

### 2️⃣1️⃣ ACCOUNT_ABSTRACTION (ID: P260–P269)
*ERC-4337 and account abstraction vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **UserOp Validation Bypass** | — | ✨ P260 |
| **Paymaster Reentrancy** | — | ✨ P261 |
| **Account Recovery Social Engineering** | — | ✨ P262 |
| **Signature Validation in EntryPoint** | — | ✨ P263 |
| **Nonce Management Exploit** | — | ✨ P264 |
| **Bundler Censorship** | — | ✨ P265 |
| **Aggregator Verification Bypass** | — | ✨ P266 |
| **WalletConnect Session Manipulation** | — | ✨ P267 |
| **Smart Wallet Upgrade Hijack** | — | ✨ P268 |
| **Multi-Sig Threshold Manipulation** | — | ✨ P269 |

### 2️⃣2️⃣ WRAPPED_ASSETS_SYNTHETICS (ID: P270–P279)
*Wrapped and synthetic asset vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Wrapped Asset Double-Spend** | — | ✨ P270 |
| **Synthetic Asset Price Deviation** | — | ✨ P271 |
| **Collateral Ratio Manipulation** | — | ✨ P272 |
| **Liquidation of Synthetic Positions** | — | ✨ P273 |
| **Mint/Burn Authorization Bypass** | — | ✨ P274 |
| **Oracle Manipulation for Synth Price** | — | ✨ P275 |
| **Wrapping/Unwrapping Race Condition** | — | ✨ P276 |
| **Cross-Chain Wrapped Asset Depeg** | — | ✨ P277 |
| **Wrapped Token Bridge Double-Mint** | — | ✨ P278 |
| **Synthetix sUSD Minting Exploit** | — | ✨ P279 |

### 2️⃣3️⃣ INSURANCE_RISK (ID: P280–P289)
*Insurance protocol vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Insurance Claim Manipulation** | — | ✨ P280 |
| **Oracle Price for Claim Payout Exploit** | — | ✨ P281 |
| **Cover Purchase Front-Running** | — | ✨ P282 |
| **Insurance Pool Depletion** | — | ✨ P283 |
| **Claim Assessment Voting Manipulation** | — | ✨ P284 |
| **Capital Provider Withdrawal Griefing** | — | ✨ P285 |
| **Coverage Period Manipulation** | — | ✨ P286 |

### 2️⃣4️⃣ STAKING_VALIDATORS (ID: P290–P299)
*Staking and validator vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Slashing Conditions Bypass** | — | ✨ P290 |
| **Validator Key Management** | — | ✨ P291 |
| **Delegation Power Concentration** | — | ✨ P292 |
| **Unbonding Period Manipulation** | — | ✨ P293 |
| **Reward Calculation Error** | — | ✨ P294 |
| **Commission Rate Manipulation** | — | ✨ P295 |
| **Staking Derivatives Depeg** | — | ✨ P296 |
| **Staking Pool Withdrawal Queue Delay** | — | ✨ P297 |
| **Liquid Staking Front-Running** | — | ✨ P298 |
| **Re-staking (EigenLayer) Slashing Risk** | — | ✨ P299 |

### 2️⃣5️⃣ GAS_ECONOMICS (ID: P300–P309)
*Gas manipulation and economics attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Block Gas Limit Manipulation** | — | ✨ P300 |
| **Dynamic Fee Calculation Bypass** | — | ✨ P301 |
| **Gas Token Minting/Burning Manipulation** | — | ✨ P302 |
| **Storage Rent Attack** | — | ✨ P303 |
| **State Size Inflation** | — | ✨ P304 |
| **SELFDESTRUCT Gas Discrepancy** | — | ✨ P305 |
| **Difficulty Bomb Interaction** | — | ✨ P306 |
| **Gas Estimation Manipulation** | — | ✨ P307 |
| **Refund Manipulation** | — | ✨ P308 |
| **Base Fee Manipulation via Blob Gas** | — | ✨ P309 |

### 2️⃣6️⃣ CROSS_CHAIN_EXPANDED (ID: P310–P329)
*Cross-chain protocol-specific exploits*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Wormhole: Guardian Set Manipulation** | — | ✨ P310 |
| **LayerZero: Endpoint Configuration Error** | — | ✨ P311 |
| **LayerZero: Adapter Validation Bypass** | — | ✨ P312 |
| **Axelar: Gateway Manipulation** | — | ✨ P313 |
| **Chain Reorg Attack on Bridge** | — | ✨ P314 |
| **Validator Set Takeover on Bridge** | — | ✨ P315 |
| **Light Client Spoofing** | — | ✨ P316 |
| **Merkle Proof Verification Bypass** | — | ✨ P317 |
| **Relayer Collusion / Censorship** | — | ✨ P318 |
| **Cross-Chain Flash Loan** | — | ✨ P319 |
| **Delayed Message Execution Exploit** | — | ✨ P320 |
| **Cross-Chain Governance Attack** | — | ✨ P321 |
| **Token Bridge Fee Manipulation** | — | ✨ P322 |
| **Cross-Chain Replay Attack** | — | ✨ P323 |

### 2️⃣7️⃣ EMERGING_THREATS (ID: P330–P339)
*Bleeding-edge attack vectors*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **ZK-Proof Verification Bypass** | — | ✨ P330 |
| **ZK Circuit Vulnerability** | — | ✨ P331 |
| **ZK Nullifier Reuse** | — | ✨ P332 |
| **ERC-2612 Permit Phishing** | — | ✨ P333 |
| **Permit2 Infinite Approval Abuse** | — | ✨ P334 |
| **Intent-Based Protocol Exploit** | — | ✨ P335 |
| **Blob Transaction Ordering Manipulation** | — | ✨ P336 |
| **ERC-6900 Modular Account Exploit** | — | ✨ P337 |
| **ERC-7579 Modular Wallet Exploit** | — | ✨ P338 |
| **AI-Generated Contract Vulnerability** | — | ✨ P339 |

### 2️⃣8️⃣ DEPENDENCY_SUPPLY_CHAIN (ID: P340–P349)
*Dependency and supply chain attacks*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Malicious Dependency Injection** | — | ✨ P340 |
| **Typosquatting Package** | — | ✨ P341 |
| **Compromised Dependency Upgrade** | — | ✨ P342 |
| **Outdated Dependency with Known CVE** | — | ✨ P343 |
| **Dependency Pin vs Floating Version** | — | ✨ P344 |
| **Subgraph Dependency Tampering** | — | ✨ P345 |
| **Hardhat/Foundry Plugin Vulnerability** | — | ✨ P346 |
| **Contract Dependency on Unverified Imports** | — | ✨ P347 |
| **Multiple Versions of Same Library** | — | ✨ P348 |
| **Unused Import** | — | ✨ P349 |

### 2️⃣9️⃣ FRONTEND_INTEGRATION (ID: P350–P359)
*Frontend and integration vulnerabilities*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Incorrect Decimal Handling** | — | ✨ P350 |
| **Token Address Mismatch** | — | ✨ P351 |
| **Swap Without Minimum Return** | — | ✨ P352 |
| **Transaction Simulation Mismatch** | — | ✨ P353 |
| **Off-Chain Signature Reuse** | — | ✨ P354 |
| **Domain Hash Collision Across Chains** | — | ✨ P355 |
| **RPC Endpoint Manipulation** | — | ✨ P356 |
| **Wallet Fingerprinting** | — | ✨ P357 |
| **Permit Data Mismatch** | — | ✨ P358 |
| **Rate Limit Bypass** | — | ✨ P359 |

### 3️⃣0️⃣ PREDICTIVE_ANOMALY (ID: P360–P369)
*ML-based anomaly detection (v3.0)*

| Subcategory | Existing Patterns | New Patterns Planned |
|-------------|-------------------|---------------------|
| **Unusual External Call Frequency** | — | ✨ P360 |
| **Abnormal Assembly Usage Pattern** | — | ✨ P361 |
| **Suspicious Modifier Structure** | — | ✨ P362 |
| **Inheritance Depth Anomaly** | — | ✨ P363 |
| **State Variable Access Pattern** | — | ✨ P364 |
| **Function Naming Similarity to Scams** | — | ✨ P365 |
| **Honeypot Classification Model** | — | ✨ P366 |
| **Rug Pull Predictor** | — | ✨ P367 |
| **Flash Loan Vulnerability Predictor** | — | ✨ P368 |
| **Zero-Day Exploit Precursor Detection** | — | ✨ P369 |

---

## ⚠️ ID Assignment Policy

**All new patterns use P21+ IDs.** The "ID Range" column shows *recommended* grouping only — actual IDs are assigned sequentially from P21 upward to avoid conflicts with existing P01-P20 patterns.

New patterns reference their TAXONOMY category via the `category` field in YAML, NOT via ID number. This allows unlimited growth.

### ID Allocation Map

| Current Range | Purpose | Status |
|---------------|---------|--------|
| P01–P20 | Original 20 patterns | ✅ Filled |
| P21–P99 | v0.5 Pattern Explosion (all categories) | 🚧 In progress |
| P100–P199 | v0.7+ Deep patterns (DeFi, Business Logic) | 📅 Planned |
| P200–P299 | v0.9+ Niche patterns (NFT, MEV, L2, AA) | 📅 Planned |
| P300–P399 | v1.0+ Advanced patterns | 📅 Future |
| P400–P499 | Reserved | 🔮 |
| P500+ | Non-EVM chains (Solana, TON, Cosmos, etc.) | 🔮 |

## 📌 Existing Pattern Mapping (P01–P20)

| ID | Name | Category | Subcategory | Difficulty | Requires AST | Exploitability |
|----|------|----------|-------------|------------|-------------|----------------|
| **P01** | Unprotected Mint | `ACCESS_CONTROL` | Unprotected Mint | easy | false | 0.95 |
| **P02** | Selfdestruct Anyone | `ACCESS_CONTROL` | Missing Access Control | easy | false | 0.90 |
| **P03** | Reentrancy | `REENTRANCY` | Classic Reentrancy | medium | false | 0.95 |
| **P04** | Integer Overflow/Underflow | `ARITHMETIC` | Integer Overflow | medium | false | 0.75 |
| **P05** | tx.origin Authentication | `ACCESS_CONTROL` | tx.origin Auth | easy | false | 0.85 |
| **P06** | Unchecked Call | `EXTERNAL_CALLS` | Unchecked Call Return | easy | false | 0.70 |
| **P07** | Delegatecall Injection | `EXTERNAL_CALLS` | Arbitrary Delegatecall | hard | false | 0.95 |
| **P08** | Storage Collision | `PROXY_UPGRADEABLE` | Storage Collision | expert | true | 0.60 |
| **P09** | No Input Validation | `BUSINESS_LOGIC` | Missing Input Validation | easy | false | 0.30 |
| **P10** | Oracle Manipulation | `TOKEN_ECONOMICS` | Oracle Manipulation | hard | false | 0.80 |
| **P11** | Flash Loan Attack Vector | `TOKEN_ECONOMICS` | Flash Loan Vector | medium | false | 0.70 |
| **P12** | Signature Replay | `SIGNATURE_CRYPTO` | Signature Replay | medium | false | 0.85 |
| **P13** | Governance Attack | `GOVERNANCE` | Governance Attack | hard | false | 0.75 |
| **P14** | Unsafe Ownership Renounce | `ACCESS_CONTROL` | Unsafe Ownership Renounce | easy | false | 0.40 |
| **P15** | Incorrect Visibility | `BUSINESS_LOGIC` | Wrong Visibility | easy | false | 0.20 |
| **P16** | Uninitialized Proxy | `PROXY_UPGRADEABLE` | Uninitialized Proxy | medium | false | 0.85 |
| **P17** | Arbitrary External Call | `EXTERNAL_CALLS` | Arbitrary External Call | medium | false | 0.90 |
| **P18** | Missing Access Control | `ACCESS_CONTROL` | Missing Access Control | medium | false | 0.80 |
| **P19** | No SafeERC20 | `ERC_STANDARDS` | Missing SafeERC20 | easy | false | 0.50 |
| **P20** | Timestamp Dependence | `BUSINESS_LOGIC` | Timestamp Dependence | easy | false | 0.35 |

---

## 🔧 YAML Field Reference

Each pattern YAML file now supports these fields:

```yaml
# Core identifiers
id: "PXX"                    # Pattern ID (required)
name: "Pattern Name"         # Human-readable name (required)
category: "CATEGORY_NAME"    # Category from taxonomy above (required)
subcategory: "Subcategory"   # Subcategory name (required)
severity: "critical"         # critical | high | medium | low (required)

# Classification
difficulty: "medium"         # easy | medium | hard | expert (required)
requires_ast: false          # true = needs AST/Slither analysis
exploitability_estimate: 0.85  # 0.0 - 1.0 float (required)

# Runtime
enabled: true                # Whether this pattern is active

# Documentation
description: >               # Full description of the vulnerability
  ...

# Detection rules
detectors:
  - type: "regex"            # regex | function_signature | ast_pattern
    description: "..."
    pattern: "..."           # For regex type
    func_pattern: "..."      # For function_signature type
    modifier_forbids: [...]  # Optional
    required_elements: [...] # For ast_pattern type
    forbidden_elements: [...] # For ast_pattern type
    confidence: 0.75         # 0.0 - 1.0
    recommendation: >        # Fix recommendation
      ...

# Metadata
notes: >                     # Optional additional notes
  CWE-ID: ...
  SWC-ID: ...
```

---

## 🔮 Future Categories (v2.0+)

These categories are reserved for non-EVM chain support:

| Reserved Range | Chain | Language |
|---------------|-------|----------|
| P500–P519 | Solana | Rust/Anchor |
| P520–P539 | TON | FunC/Tact |
| P540–P559 | Cosmos | CosmWasm/Go |
| P560–P579 | StarkNet | Cairo |
| P580–P599 | Aptos/Sui | Move |
| P600–P619 | Polkadot/Ink! | Rust |
| P620–P639 | Bitcoin | Script |
| P640–P659 | Near | Rust/AS |
| P660–P679 | zkSync Era | EraVM/Solidity |

---

*Last updated: 2026-06-18*
*Part of MaatEye — Multi-Chain Vulnerability Scanner*
