// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol";
// import "https://github.com/NomicFoundation/hardhat/blob/main/packages/hardhat-core/console.sol";

contract BlockChatCoin is ERC20 {
    address pairedContract;

    constructor(address _pairedContract) ERC20("BlockChatToken", "BLCC") {
        _mint(msg.sender, 10000);
        pairedContract = _pairedContract;
    }

    function transfer(address _sender,address _recipient, uint _amount) public returns (bool) {
        _transfer(_sender, _recipient, _amount);
        emit Transfer(_sender, _recipient, _amount);
        return true;
    }

    function burn(uint amount) public {
        emit Transfer(msg.sender, address(0), amount);
    }

    function mint(address to, uint256 amount) public {
        // msg.sender must be the BlockChat contract. Nothing else is able to mint new tokens.
        require(msg.sender == pairedContract, "Unautorised contract!!");
        _mint(to, amount);
        emit Transfer(address(0), msg.sender, amount);
    }

    function deleteContract() external {
        selfdestruct(payable(msg.sender));
    }
}
