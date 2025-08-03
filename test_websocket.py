#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection and receive messages"""
    uri = "ws://localhost:8000/api/v1/ws/alerts"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket at {uri}")
            print("Waiting for messages...")
            
            # Send a test message
            await websocket.send("test")
            print("Sent test message")
            
            # Listen for messages
            while True:
                try:
                    message = await websocket.recv()
                    print(f"Received message: {message}")
                    
                    # Try to parse as JSON
                    try:
                        data = json.loads(message)
                        print(f"Parsed JSON: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"Raw message: {message}")
                        
                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break
                    
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing WebSocket connection...")
    asyncio.run(test_websocket()) 