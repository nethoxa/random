#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

printf "\n\n"
printf "${GREEN}    ██╗ ██╗██╗  ██╗ █████╗ ██╗     ██████╗  ██████╗ ██████╗ ███╗   ██╗ \n"
printf "${GREEN}   ██╔╝██╔╝██║  ██║██╔══██╗██║     ██╔══██╗██╔═══██╗██╔══██╗████╗  ██║ \n"
printf "${GREEN}  ██╔╝██╔╝ ███████║███████║██║     ██████╔╝██║   ██║██████╔╝██╔██╗ ██║ \n"
printf "${GREEN} ██╔╝██╔╝  ██╔══██║██╔══██║██║     ██╔══██╗██║   ██║██╔══██╗██║╚██╗██║ \n"
printf "${GREEN}██╔╝██╔╝   ██║  ██║██║  ██║███████╗██████╔╝╚██████╔╝██║  ██║██║ ╚████║ \n"
printf "${GREEN}╚═╝ ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ \n"
printf "${NC}\n"

printf "${GREEN}███████╗ ██████╗ ██╗     ██╗██████╗ ██╗████████╗██╗   ██╗     ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ \n"
printf "${GREEN}██╔════╝██╔═══██╗██║     ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗\n"
printf "${GREEN}███████╗██║   ██║██║     ██║██║  ██║██║   ██║    ╚████╔╝     ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝\n"
printf "${GREEN}╚════██║██║   ██║██║     ██║██║  ██║██║   ██║     ╚██╔╝      ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗\n"
printf "${GREEN}███████║╚██████╔╝███████╗██║██████╔╝██║   ██║      ██║       ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║\n"
printf "${GREEN}╚══════╝ ╚═════╝ ╚══════╝╚═╝╚═════╝ ╚═╝   ╚═╝      ╚═╝        ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝\n"
printf "${NC}\n\n"

printf "${YELLOW}Introduce the contracts path of the Solidity project you want to check: (Example: /root/halborn/projects/beanstalk/contracts/): "
read PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}CONTRACT SIZE${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${GREEN}\n"
cd $PROJECT_DIRECTORY; find -name '*.sol' | xargs wc -l; cd -
printf "${NC}\n\n"

printf "${GREEN}TOKEN TRANSFERS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check for possible incompatibility with non standard erc20 tokens\n"
printf "	2. Check for possible incompatibility with deflationary/transfer-on-fee tokens\n"
printf "	3. ERC721.safeTransferFrom() could be exploited with reentrancy\n"
printf "	4. ERC777 tokens transfers could be exploited with reentrancy\n"
printf "	5. transferFrom() & safeTransferFrom() should always use msg.sender as from address if the contract is taking funds. If other account is used, this could be frontrun.\n"
printf "		Example of vulnerable code: https://github.com/HalbornSecurity/CTFs/blob/master/HalbornCTF_Solidity_Ethereum/CTF1_NFTMarketplace/contracts/NFTMarketplace.sol#L320\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.transfer(\|\.transferFrom(\|\.safeTransfer(\|\.safeTransferFrom(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}NATIVE ETHER TRANSFERS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. call() & sendValue()(OpenZeppelin's Address contract) has no gas limit restrictions, hence they could be exploited with reentrancy. transfer() and send() both are limited to 2300 gas. Still it's recommended to use call() or sendValue() over transfer() or send()\n"
printf "		Reference: https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/\n"
printf "		Example report: https://github.com/code-423n4/2022-04-backd-findings/issues/52\n"
printf "	2. Careful with Ether refunds. If these are done to a smart contract with no receive(), fallback() function transaction will revert\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.call(\|\.sendValue(\|\.transfer(\|.send(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}MINTS/BURNS CALLS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. ERC721.safeMint() could be exploited with reentrancy\n"
printf "	2. Check that minting/burning calls are protected with the proper access control mechanism\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.mint(\|.safeMint(\|_mint(\|.burn(\|_burn(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}APPROVES${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check for possible incompatibility with non standard erc20 tokens. Tokens like USDT require a 0 allowance to be approved.\n"
printf "	2. Some tokens like USDT does not return true after an approve call. If the return value of the approve() call is checked with a require this will be a problem as it will always revert with this type of token\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.approve(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}SAFEAPPROVES${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. SafeERC20.safeApprove() requires that the allowance is 0 otherwise it reverts. Careful when this function is called multiple times, as the second call may fail if the allowance is not zero\n"
printf "		Example report 1: https://github.com/code-423n4/2022-04-backd-findings/issues/178\n"
printf "		Example report 2: https://doc.halborn.com/project/62965865b88980007701b98e\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.safeApprove(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}DELEGATE CALLS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check that untrusted code is not executed with delegatecall because it could maliciously modify state variables or call selfdestruct to destroy the calling contract.\n"
printf "	2. Make sure that delegatecall calls only addresses that have code. Delegatecall will return True for the status value if it is called on an address that is not a contract and so has no code. This can cause bugs if code expects delegatecall functions to return False when they can’t execute.\n"
printf "	3. If delegatecall is called within a loop, the follow inconsistency with msg.value occurs. This can turn into a critical vulnerability\n"
printf "		Issue described in this video: https://youtu.be/NkTWU6tc9WU?t=361\n"
printf "		Article about it: https://samczsun.com/two-rights-might-make-a-wrong/\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'delegatecall(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}ECRECOVER${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. ecrecover returns address(0) with invalid signatures. Check that the returned address by ecrecover is checked against address(0) in the smart contract. If the signer address is not set (hence it is initialized as address(0)) and the contract does not check this there is a problem.\n"
printf "	2. Check that the signatures can not be replayed. EIP-712 standard covers very well whats needed to avoid replay attacks.\n"
printf "		Nonces can be used to mitigate the risk of signature replay attacks within the same contract\n"
printf "		address(this) + contract version (See EIP-712) can be used to mitigate the risk of signature replay attacks within the same blockchain\n"
printf "		chain.id can be used to mitigate the risk of crosschain signature replay attacks\n"
printf "	3. Chain.id should be recalculated every time\n"
printf "		Example report: https://github.com/code-423n4/2021-06-realitycards-findings/issues/166\n"
printf "	4. Signature Malleability: The implementation of a cryptographic signature system in Ethereum contracts often assumes that the signature is unique, but signatures can be altered without the possession of the private key and still be valid. This issue only occurs if the only mechanism in the smart contract to prevent replay attacks is checking that the signature has not been used before.\n"
printf "		Example: https://swcregistry.io/docs/SWC-117\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'ecrecover(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}ENCODEDPACKED CALLS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check for possible hash collissions if abi.encodedPacked() is used with multiple variable-length arguments.\n"
printf "		For example: abi.encodedPacked(dynamic_size_array1[], dynamic_size_array2[]) or abi.encodedPacked(bytes a, bytes b)\n"
printf "		Reference: https://medium.com/swlh/new-smart-contract-weakness-hash-collisions-with-multiple-variable-length-arguments-dc7b9c84e493\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'abi.encodePacked(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}MSG.VALUE CALLS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check the requirements around msg.value are correct.\n"
printf "	2. Careful with loops. msg.value will be the same in every iteration of the loop.\n"
printf "		Example: https://gist.github.com/HickupHH3/8eca4d2142f3ddbd694e921a0db33088#file-vulnerablec4lottery-sol Line 63, guessEth(), msg.value will only be sent once.\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'msg.value' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}TX.ORIGIN CALLS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check that tx.origin is not used for authentication purposes.\n"
printf "		Reference: https://hackernoon.com/hacking-solidity-contracts-using-txorigin-for-authorization-are-vulnerable-to-phishing\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'tx.origin' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}INITIALIZE FUNCTIONS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check that the initialize() functions are correctly protected with the initialize/onlyInitializing modifier.\n"
printf "		Reference: https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable\n"
printf "	2. Check that the imports use @openzeppelin/contracts-upgradeable/ and not @openzeppelin/contracts/ libraries.\n"
printf "	3. Check all the parents contracts are correctly initialized.\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'function init(\|function initialize\| initializer\| onlyInitializing' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}LOOPS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check that the block gas limit can not be reached in any loop causing a Denial of Service.\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rn 'for(\|for (\|while(\|while (' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}IMPORTS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check the source of the imports. All those contracts that are custom should be checked.\n"
printf "	2. Check upgradeable contracts import @openzeppelin/contracts-upgradeable/ and not @openzeppelin/contracts/ libraries.\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'import ' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}DELETES/PUSH/POP${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Deleting mappings: If you have a mapping in a struct or in your state in general, Solidity cannot delete it, because it does not know the keys for the mapping. Since the keys are arbitrary and not stored along, the only way to delete structs is to know the key for each stored value. A value can then be deleted by delete myMapping[myKey].\n"
printf "	2. Check array.pop()'s are done correctly and are actually deleting the correct position in the array.\n"
printf "		pop() will always remove the last position of the array, usually the element to be deleted in the array is overwritten with the last element and then a pop() is called to delete the last element\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'delete\|\.push(\|\.pop(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}RANDOM NUMBER GENERATION${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Check that in the generation of random numbers the msg.sender address is not used. If it is, we can make use of CREATE2 to exploit it.\n"
printf "		Reference: https://doc.halborn.com/project/625d9f8fb88980007701b3f9 - HAL02 issue\n"
printf "	2. If blockhash is used check it is used properly as most devs do not know about this: blockhash(uint blockNumber) only works for 256 most recent blocks, excluding current, blocks.\n"
printf "		Using blockhash(block.number) will always return 0. blockhash(block.number - 1) should be used.\n"
printf "	3. When Chainlink is not used to generate random numbers it is usually recommended to restrict these calls to smart contracts by making use of require(msg.sender == tx.origin).\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'random\|block.blockhash(\|block.difficulty\|blockhash(\|block.basefee' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}SELF DESTRUCTS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. You should not really find this call in any smart contract, if you do, that is a very bad sign.\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin '\.selfdestruct(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}CHAINLINK CALLBACKS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. If your fulfillRandomness function uses more than 200k gas (Chainlink VRF v1), the transaction will fail. In Chainlink VRF v2 the callback gas limit can be set to a maximum of 2.5M gas\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rin 'function fulfillRandomness(' $PROJECT_DIRECTORY
printf "${NC}\n\n"

printf "${GREEN}CASTINGS${NC}\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${YELLOW}\n"
printf "${YELLOW}Checks: ${GREEN}\n"
printf "	1. Solidity 0.8 is introducing type checking for arithmetic operations, but not for type casting. Because of this, an overflow may occur during the casting operations.\n"
printf "		Example 1: https://doc.halborn.com/project/6277b81bb88980007701b612 - HAL02 issue\n"
printf "		Example 2: https://github.com/code-423n4/2021-09-sushitrident-2-findings/issues/50\n"
printf "${YELLOW}---------------------------------------------------------------------------------------------------------${RED}\n"
grep -Rn 'uint256(\|uint248(\|uint240(\|uint232(\|uint224(\|uint216(\|uint208(\|uint200(\|uint192(\|uint184(\|uint176(\|uint168(\|uint160(\|uint152(\|uint144(\|uint136(\|uint128(\|uint120(\|uint112(\|uint104(\|uint96(\|uint88(\|uint80(\|uint72(\|uint64(\|uint56(\|uint48(\|uint40(\|uint32(\|uint24(\|uint16(\|uint8(\|int256(\|int248(\|int240(\|int232(\|int224(\|int216(\|int208(\|int200(\|int192(\|int184(\|int176(\|int168(\|int160(\|int152(\|int144(\|int136(\|int128(\|int120(\|int112(\|int104(\|int96(\|int88(\|int80(\|int72(\|int64(\|int56(\|int48(\|int40(\|int32(\|int24(\|int16(\|int8(' $PROJECT_DIRECTORY
printf "${NC}\n\n"
