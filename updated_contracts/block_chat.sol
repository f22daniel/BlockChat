// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "https://github.com/f22daniel/helpful_smart_contracts/blob/main/contracts/MumbaiPriceFeedV1.sol";
import "./BlockChatCoin.sol";
import "https://github.com/NomicFoundation/hardhat/blob/main/packages/hardhat-core/console.sol";

contract BlockChat{
    mapping (string => address) public streamers;
    event Message(uint time, address recipient, string donor, string superchat, uint amount, bool payedBLCC);
    address priceFeedContract;
    address public pairedToken;
    bool public pairingDone;
    bool lengthVerified;

    constructor() {
        priceFeedContract = 0x212B30E972ABc4c0b9e24dB44E99D84C40c59731;
    }

    function subscribeStreamer(string calldata _streamerName) external {
        address subscriber = streamers[_streamerName];
        require(subscriber == 0x0000000000000000000000000000000000000000, "Name already in use!!");
        streamers[_streamerName] = msg.sender;
    }

    function unsubscribeStreamer(string calldata _streamerName) external {
        address streamer = streamers[_streamerName];
        require(streamer == msg.sender, "Not your Name!!");
        delete streamers[_streamerName];
    }

    function sendSuperChat(string calldata _streamerName, string calldata _nickname, string calldata _message, bool payWithBLCC) external payable {
        // Subscriber verification
        address recipient = streamers[_streamerName];
        require(recipient != 0x0000000000000000000000000000000000000000, "Invalid address!!");
        require(pairingDone, "Token not paired");
        // Block Chat Token minting plus msg.value transfer
        uint msgLength = getStringLength(_message);
        uint amountSent;
        if (payWithBLCC){
            // Payment via BLCC should the viewer decide to pay in such way.
            amountSent = payViaBlockChatToken(_message, msg.sender, recipient);
        }
        else {
            uint usdSent = maticUsdConverter(msg.value);
            (bool lengthOK, string memory message) = messageLengthCheck(_message, usdSent);
            require(lengthOK, message);
            BlockChatCoin _contract = BlockChatCoin(pairedToken);
            _contract.mint(msg.sender, msgLength); // Token minting for the viewer 1 BLCC per 1 letter
            payable(recipient).transfer(msg.value);
            amountSent = msg.value;
        }
        emit Message(block.timestamp, recipient, _nickname, _message, amountSent, payWithBLCC);
    }

    // Function that facilitates BlockChatToken transfer should the viewer decide to pay superchat via BLCC
    function payViaBlockChatToken(string calldata _message, address _sender, address _recipient) internal returns(uint) {
        BlockChatCoin _contract = BlockChatCoin(pairedToken);
        uint msgLength = getStringLength(_message);
        uint tokenSpent = msgLength * 10;
        uint senderBalance = _contract.balanceOf(_sender);
        require(senderBalance >= tokenSpent, "Insufficient funds!!");
        bool tokensTransfered = _contract.transfer(_sender ,_recipient, tokenSpent);
        require(tokensTransfered, "Transaction failed!!");
        return tokenSpent;
    }

    // Matic/USD price converter. Enter USD - get how much that makes in Matic
    function usdMaticConverter(uint _amount) public view returns(uint){
        MumbaiPriceFeedV1 converter = MumbaiPriceFeedV1(priceFeedContract);
        (uint priceMaticUsd, ) = converter.getLatestMaticUsd();
        priceMaticUsd = priceMaticUsd * 10**10;
        uint amount = _amount * 10**18;
        uint MaticAmountSent = (amount * 10**18)/priceMaticUsd;
        return MaticAmountSent;
    }

    // USD/Matic price converter. Enter Matic - get how much that makes in USD
    function maticUsdConverter(uint _amount) public view returns(uint){
        MumbaiPriceFeedV1 converter = MumbaiPriceFeedV1(priceFeedContract);
        (uint priceMaticUsd, ) = converter.getLatestMaticUsd();
        priceMaticUsd = priceMaticUsd * 10**10;
        //uint maticAmount = _amount * 10**18;
        uint usdAmountSent = (_amount * priceMaticUsd)/10**36;
        return usdAmountSent;
    }

    // Checking length of a sent superchat. If the length of the superchat is insufficient, the transaction will fail.
    function messageLengthCheck(string calldata _message, uint _amount) public pure returns(bool, string memory){
        uint msgLength = getStringLength(_message);
        if (msgLength > 100 && _amount < 10){
            return(false, "Min. amount 10$");
        }
        else if (msgLength > 200 && _amount < 20){
            return(false, "Min. amount 20$");
        }
        else if (msgLength > 400 && _amount < 30){
            return(false, "Min. amount 30$");
        }
        else if (msgLength > 800 && _amount < 50){
            return(false, "Min. amount 50$");
        }
        return (true, "Passed");
    }
    // Function which lets the contract know, which ERC20 BLCC to work with
    function tokenPairing(address _pairToken) external {
        require(!pairingDone, "Pairing already done!!");
        pairedToken = _pairToken;
        pairingDone = true;
    }

    function getStringLength(string calldata str) public pure returns (uint) {
        bytes memory bytesStr = bytes(str);
        return bytesStr.length;
    }

    function deleteContract() external {
        selfdestruct(payable(msg.sender));
    }
}
