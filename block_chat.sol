// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "https://github.com/f22daniel/helpful_smart_contracts/blob/main/contracts/MumbaiPriceFeedV1.sol";

contract BlockChat{
    mapping (string => address) public streamers;
    event Message(uint time, address recipient, string donor, string superchat, uint amount);
    address priceFeedContract;

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
    function sendSuperChat(string calldata _streamerName, string calldata _nickname, string calldata _message) external payable {
        address recipient = streamers[_streamerName];
        require(recipient != 0x0000000000000000000000000000000000000000, "Invalid address!!");
        payable(recipient).transfer(msg.value);
        emit Message(block.timestamp, recipient, _nickname, _message, msg.value);
    }
    function usdMaticConverter(uint _amount) public view returns(uint) {
        MumbaiPriceFeedV1 converter = MumbaiPriceFeedV1(priceFeedContract);
        (uint priceMaticUsd, ) = converter.getLatestMaticUsd();
        priceMaticUsd = priceMaticUsd * 10**10;
        uint amount = _amount * 10**18;
        uint MaticAmountSent = (amount * 10**18)/priceMaticUsd;
        return MaticAmountSent;
    }
    function deleteContract() external {
        selfdestruct(payable (msg.sender));
    }
}