from typing import Dict, List


class ConversationService:
    """Manage conversation history for active sessions."""

    def __init__(self):
        self._conversations: Dict[str, List[dict]] = {}

    def create_session(self, session_id: str) -> None:
        """Create a new conversation session."""

        if session_id not in self._conversations:
            self._conversations[session_id] = []

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        """Add a message to a conversation."""

        if not session_id:
            raise ValueError("Session ID cannot be empty.")

        if role not in {"user", "assistant"}:
            raise ValueError(
                "Role must be 'user' or 'assistant'."
            )

        if not content or not content.strip():
            raise ValueError(
                "Message content cannot be empty."
            )

        self.create_session(session_id)

        self._conversations[session_id].append(
            {
                "role": role,
                "content": content.strip()
            }
        )

    def get_history(
        self,
        session_id: str
    ) -> List[dict]:
        """Return conversation history."""

        if session_id not in self._conversations:
            return []

        return list(
            self._conversations[session_id]
        )

    def clear_session(
        self,
        session_id: str
    ) -> None:
        """Delete a conversation session."""

        self._conversations.pop(
            session_id,
            None
        )