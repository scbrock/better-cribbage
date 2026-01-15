"""
Streamlit session state management for the cribbage trainer.
"""

import streamlit as st
from typing import Optional, List

from cribbage_trainer.models import Hand, UserStats, SessionSummary


class SessionManager:
    """Manages Streamlit session state for the cribbage trainer."""
    
    @staticmethod
    def initialize_session():
        """Initialize all required session state variables."""
        if 'current_hand' not in st.session_state:
            st.session_state.current_hand = None
            
        if 'user_stats' not in st.session_state:
            st.session_state.user_stats = UserStats()
            
        if 'session_history' not in st.session_state:
            st.session_state.session_history = []
            
        if 'current_session_attempts' not in st.session_state:
            st.session_state.current_session_attempts = []
            
        if 'selected_cards' not in st.session_state:
            st.session_state.selected_cards = []
    
    @staticmethod
    def get_current_hand() -> Optional[Hand]:
        """Get the current training hand."""
        return st.session_state.get('current_hand')
    
    @staticmethod
    def set_current_hand(hand: Hand):
        """Set the current training hand."""
        st.session_state.current_hand = hand
    
    @staticmethod
    def get_user_stats() -> UserStats:
        """Get the current user statistics."""
        return st.session_state.user_stats
    
    @staticmethod
    def update_user_stats(stats: UserStats):
        """Update the user statistics."""
        st.session_state.user_stats = stats
    
    @staticmethod
    def get_session_history() -> List[SessionSummary]:
        """Get the history of completed sessions."""
        return st.session_state.session_history
    
    @staticmethod
    def add_session_to_history(summary: SessionSummary):
        """Add a completed session to the history."""
        st.session_state.session_history.append(summary)
    
    @staticmethod
    def get_selected_cards() -> List:
        """Get the currently selected cards for discard."""
        return st.session_state.selected_cards
    
    @staticmethod
    def set_selected_cards(cards: List):
        """Set the selected cards for discard."""
        st.session_state.selected_cards = cards
    
    @staticmethod
    def clear_selected_cards():
        """Clear the selected cards."""
        st.session_state.selected_cards = []
    
    @staticmethod
    def complete_current_session():
        """Complete the current session and add it to history."""
        # Calculate current session stats from attempts
        current_attempts = st.session_state.get('current_session_attempts', [])
        
        if current_attempts:
            total_attempts = len(current_attempts)
            correct_choices = sum(1 for attempt in current_attempts if attempt.get('correct', False))
            session_score = correct_choices
            
            # Create session summary
            from .models import SessionSummary
            summary = SessionSummary(
                total_attempts=total_attempts,
                correct_choices=correct_choices,
                session_score=session_score
            )
            
            # Add to history
            SessionManager.add_session_to_history(summary)
            
            # Update overall stats
            stats = SessionManager.get_user_stats()
            stats.total_sessions += 1
            stats.session_scores.append(session_score)
            SessionManager.update_user_stats(stats)
            
            # Clear current session
            st.session_state.current_session_attempts = []
    
    @staticmethod
    def record_attempt_result(is_correct: bool):
        """Record the result of a training attempt."""
        if 'current_session_attempts' not in st.session_state:
            st.session_state.current_session_attempts = []
        
        st.session_state.current_session_attempts.append({
            'correct': is_correct,
            'timestamp': None  # Could add timestamp if needed
        })
    
    @staticmethod
    def reset_all_progress():
        """Reset all user progress and statistics."""
        st.session_state.user_stats = UserStats()
        st.session_state.session_history = []
        st.session_state.current_session_attempts = []
        st.session_state.current_hand = None
        st.session_state.selected_cards = []