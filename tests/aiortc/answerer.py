import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription


async def run(description):
    # Create a new RTCPeerConnection with a STUN server for NAT traversal
    pc = RTCPeerConnection({
        "iceServers": [{"urls": "stun:stun.l.google.com:19302"}]
    })

    # Handle data channel events
    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("open")
        def on_open():
            print("Data channel opened")
            channel.send("Hello from the answerer!")

        @channel.on("message")
        def on_message(message):
            print("Message from the offerer:", message)

    # Set the remote description
    await pc.setRemoteDescription(RTCSessionDescription(description["sdp"], description["type"]))

    # Create an answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Output the local description to be sent to the offerer
    print(json.dumps({"sdp": pc.localDescription.sdp,
          "type": pc.localDescription.type}))

    # Keep the connection alive
    await asyncio.sleep(3600)

if __name__ == "__main__":
    # Paste the offer description here
    offer_description = {
        "sdp": "paste_offer_sdp_here",
        "type": "offer"
    }
    asyncio.run(run(offer_description))
