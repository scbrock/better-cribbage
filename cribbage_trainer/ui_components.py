"""
Streamlit UI components for the cribbage trainer.
"""

import streamlit as st
from typing import List, Optional, Tuple
import random

from cribbage_trainer.models import Card, Hand, Rank, Suit
from cribbage_trainer.session_manager import SessionManager


class CardDisplay:
    """Handles card display and selection in Streamlit."""
    
    # Card suit symbols for better visual display
    SUIT_SYMBOLS = {
        Suit.HEARTS: "♥️",
        Suit.DIAMONDS: "♦️", 
        Suit.CLUBS: "♣️",
        Suit.SPADES: "♠️"
    }
    
    # Colors for suits
    SUIT_COLORS = {
        Suit.HEARTS: "red",
        Suit.DIAMONDS: "red",
        Suit.CLUBS: "black", 
        Suit.SPADES: "black"
    }
    
    @staticmethod
    def display_card(card: Card, selected: bool = False) -> str:
        """
        Create a visual representation of a card.
        
        Args:
            card: The card to display
            selected: Whether the card is currently selected
            
        Returns:
            HTML string for the card display
        """
        suit_symbol = CardDisplay.SUIT_SYMBOLS[card.suit]
        suit_color = CardDisplay.SUIT_COLORS[card.suit]
        
        # Create card styling
        border_color = "#007bff" if selected else "#dee2e6"
        background_color = "#e3f2fd" if selected else "white"
        
        card_html = f"""
        <div style="
            border: 2px solid {border_color};
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
            background-color: {background_color};
            text-align: center;
            min-width: 60px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 18px; font-weight: bold; color: {suit_color};">
                {card.rank.value}
            </div>
            <div style="font-size: 24px;">
                {suit_symbol}
            </div>
        </div>
        """
        
        return card_html
    
    @staticmethod
    def display_hand_with_selection(hand: Hand) -> List[Card]:
        """
        Display a hand of cards with selection capability.
        
        Args:
            hand: The hand to display
            
        Returns:
            List of selected cards
        """
        st.subheader("Your Hand")
        
        # Display dealer status
        dealer_status = "🎯 Dealer" if hand.is_dealer else "👤 Non-Dealer"
        st.markdown(f"**Status:** {dealer_status}")
        
        # Instructions
        st.markdown("**Instructions:** Select exactly 2 cards to discard to the crib.")
        
        # Sort cards for consistent display
        sorted_cards = sorted(hand.cards, key=lambda c: (c.rank.value, c.suit.value))
        
        # Create columns for card layout
        cols = st.columns(6)
        
        selected_cards = SessionManager.get_selected_cards()
        new_selected_cards = []
        
        # Display each card with selection checkbox
        for i, card in enumerate(sorted_cards):
            with cols[i]:
                # Create a unique key for each card
                card_key = f"card_{card.rank.value}_{card.suit.value}"
                
                # Check if this card was previously selected
                is_selected = card in selected_cards
                
                # Display the card
                st.markdown(CardDisplay.display_card(card, is_selected), unsafe_allow_html=True)
                
                # Add selection checkbox
                if st.checkbox(f"Select", key=card_key, value=is_selected):
                    new_selected_cards.append(card)
        
        # Update selected cards in session state
        SessionManager.set_selected_cards(new_selected_cards)
        
        # Show selection status
        if len(new_selected_cards) == 0:
            st.info("Please select 2 cards to discard.")
        elif len(new_selected_cards) == 1:
            st.warning("Please select 1 more card to discard.")
        elif len(new_selected_cards) == 2:
            st.success("✅ 2 cards selected. Ready to submit!")
            # Sort selected cards for display
            sorted_selected = sorted(new_selected_cards, key=lambda c: (c.rank.value, c.suit.value))
            st.markdown(f"**Selected cards:** {', '.join(str(card) for card in sorted_selected)}")
        else:
            st.error(f"❌ Too many cards selected ({len(new_selected_cards)}). Please select exactly 2 cards.")
        
        return new_selected_cards
    
    @staticmethod
    def validate_selection(selected_cards: List[Card]) -> Tuple[bool, str]:
        """
        Validate the card selection.
        
        Args:
            selected_cards: List of selected cards
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(selected_cards) < 2:
            return False, f"Please select 2 cards. You have selected {len(selected_cards)}."
        elif len(selected_cards) > 2:
            return False, f"Please select exactly 2 cards. You have selected {len(selected_cards)}."
        else:
            return True, "Selection is valid."
    
    @staticmethod
    def display_remaining_cards(hand: Hand, discarded_cards: List[Card]) -> List[Card]:
        """
        Display the cards remaining in hand after discard.
        
        Args:
            hand: Original hand
            discarded_cards: Cards that were discarded
            
        Returns:
            List of remaining cards
        """
        remaining_cards = [card for card in hand.cards if card not in discarded_cards]
        
        # Sort remaining cards
        remaining_cards = sorted(remaining_cards, key=lambda c: (c.rank.value, c.suit.value))
        
        st.subheader("Your Remaining Hand")
        
        # Create columns for remaining cards
        if remaining_cards:
            cols = st.columns(len(remaining_cards))
            
            for i, card in enumerate(remaining_cards):
                with cols[i]:
                    st.markdown(CardDisplay.display_card(card), unsafe_allow_html=True)
        
        return remaining_cards


class HandGenerator:
    """Generates training hands for the cribbage trainer."""
    
    @staticmethod
    def generate_random_hand(is_dealer: Optional[bool] = None) -> Hand:
        """
        Generate a random 6-card hand for training.
        
        Args:
            is_dealer: Force dealer status, or None for random
            
        Returns:
            A new Hand object
        """
        # Create full deck
        full_deck = []
        for suit in Suit:
            for rank in Rank:
                full_deck.append(Card(rank, suit))
        
        # Randomly select 6 cards
        selected_cards = random.sample(full_deck, 6)
        
        # Sort cards by rank and suit for consistent display
        selected_cards = sorted(selected_cards, key=lambda c: (c.rank.value, c.suit.value))
        
        # Randomly determine dealer status if not specified
        if is_dealer is None:
            is_dealer = random.choice([True, False])
        
        return Hand(selected_cards, is_dealer)
    
    @staticmethod
    def generate_training_hand(difficulty: str = "mixed") -> Hand:
        """
        Generate a hand with specific difficulty characteristics.
        
        Args:
            difficulty: "beginner", "intermediate", "advanced", or "mixed"
            
        Returns:
            A new Hand object with appropriate difficulty
        """
        # For now, just generate random hands
        # TODO: Implement difficulty-based hand generation
        return HandGenerator.generate_random_hand()


class GameControls:
    """Handles game control buttons and actions."""
    
    @staticmethod
    def render_action_buttons(selected_cards: List[Card]) -> str:
        """
        Render the main action buttons.
        
        Args:
            selected_cards: Currently selected cards
            
        Returns:
            Action taken ("submit", "new_hand", "reset", or None)
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Submit button - only enabled if exactly 2 cards selected
            is_valid, _ = CardDisplay.validate_selection(selected_cards)
            if st.button("Submit Discard", disabled=not is_valid, type="primary"):
                return "submit"
        
        with col2:
            if st.button("New Hand"):
                return "new_hand"
        
        with col3:
            if st.button("Clear Selection"):
                return "clear_selection"
        
        return None
    
    @staticmethod
    def render_progress_controls() -> str:
        """
        Render progress and session control buttons.
        
        Returns:
            Action taken or None
        """
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("View Progress"):
                return "view_progress"
        
        with col2:
            if st.button("Reset All Progress", type="secondary"):
                return "reset_progress"
        
        return None