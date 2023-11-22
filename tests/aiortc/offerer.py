import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel


async def run():
    # Create a new RTCPeerConnection with a STUN server for NAT traversal
    pc = RTCPeerConnection({
        "iceServers": [{"urls": "stun:stun.l.google.com:19302"}]
    })

    # Create a data channel
    channel = pc.createDataChannel("chat")

    # Handle data channel events
    @channel.on("open")
    def on_open():
        print("Data channel opened")
        channel.send("Hello from the offerer!")

    @channel.on("message")
    def on_message(message):
        print("Message from the answerer:", message)

    # Create an offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    # Output the local description to be sent to the answerer
    print(json.dumps({"sdp": pc.localDescription.sdp,
          "type": pc.localDescription.type}))

    # Wait for the answer to be set remotely
    while not pc.remoteDescription:
        await asyncio.sleep(1)

    # Keep the connection alive
    await asyncio.sleep(3600)

# Set remote description received from the answerer


async def set_remote_description(description):
    await pc.setRemoteDescription(RTCSessionDescription(description["sdp"], description["type"]))

pc = None

if __name__ == "__main__":
    pc = RTCPeerConnection()
    asyncio.run(run())
