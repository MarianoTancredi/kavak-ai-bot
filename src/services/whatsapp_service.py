from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from typing import Dict, List
import json


class WhatsAppService:
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
        self.conversations: Dict[str, List[Dict]] = {}
    
    def send_message(self, to_number: str, message: str):
        """Send a WhatsApp message"""
        try:
            message = self.client.messages.create(
                body=message,
                from_=f'whatsapp:{self.phone_number}',
                to=f'whatsapp:{to_number}'
            )
            return message.sid
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def handle_incoming_message(self, from_number: str, message_body: str) -> str:
        """Handle incoming WhatsApp message and return response"""
        # Initialize conversation history if not exists
        if from_number not in self.conversations:
            self.conversations[from_number] = []
        
        # Add user message to conversation history
        self.conversations[from_number].append({
            "role": "user",
            "content": message_body
        })
        
        # Keep only last 10 messages to avoid token limits
        if len(self.conversations[from_number]) > 10:
            self.conversations[from_number] = self.conversations[from_number][-10:]
        
        return f"whatsapp:{from_number}"
    
    def get_conversation_history(self, phone_number: str) -> List[Dict]:
        """Get conversation history for a phone number"""
        return self.conversations.get(phone_number, [])
    
    def add_assistant_message(self, phone_number: str, message: str):
        """Add assistant message to conversation history"""
        if phone_number not in self.conversations:
            self.conversations[phone_number] = []
        
        self.conversations[phone_number].append({
            "role": "assistant",
            "content": message
        })
    
    def create_webhook_response(self, message: str) -> str:
        """Create TwiML response for webhook"""
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)
    
    def clear_conversation(self, phone_number: str):
        """Clear conversation history for a phone number"""
        if phone_number in self.conversations:
            del self.conversations[phone_number]