"""
Hand analyzer component for custom hand analysis.
"""

import streamlit as st
from typing import List, Optional, Tuple
import itertools

from cribbage_trainer.models import Card, Hand, Rank, Suit
from cribbage_trainer.engine import CribbageEngine
from cribbage_trainer.ui_components import CardDisplay
from cribbage_trainer.feedback import FeedbackDisplay


class HandAnalyzer:
    """Handles custom hand input and analysis."""
    
    @staticmethod
    def show_hand_analyzer():
        """Display the hand analyzer interface."""
        st.header("🔍 Hand Analyzer")
        st.markdown("Enter your own 6-card hand to get optimal discard recommendations!")
        
        # Initialize session state for custom hand
        if 'custom_hand_cards' not in st.session_state:
            st.session_state.custom_hand_cards = []
        if 'custom_dealer_status' not in st.session_state:
            st.session_state.custom_dealer_status = True
        
        # Hand input section
        st.subheader("Enter Your Hand")
        
        # Dealer status selection
        col1, col2 = st.columns(2)
        with col1:
            dealer_status = st.radio(
                "Dealer Status:",
                options=[True, False],
                format_func=lambda x: "🎯 Dealer" if x else "👤 Non-Dealer",
                index=0 if st.session_state.custom_dealer_status else 1,
                key="dealer_radio"
            )
            st.session_state.custom_dealer_status = dealer_status
        
        with col2:
            st.markdown("**Current Hand Size:**")
            st.metric("Cards", len(st.session_state.custom_hand_cards), help="Need exactly 6 cards")
        
        # Card input methods
        tab1, tab2 = st.tabs(["Card Selector", "Text Input"])
        
        with tab1:
            HandAnalyzer._show_card_selector()
        
        with tab2:
            HandAnalyzer._show_text_input()
        
        # Display current hand
        if st.session_state.custom_hand_cards:
            HandAnalyzer._display_current_hand()
        
        # Analysis section
        if len(st.session_state.custom_hand_cards) == 6:
            st.divider()
            HandAnalyzer._show_analysis()
        elif len(st.session_state.custom_hand_cards) > 0:
            st.info(f"Add {6 - len(st.session_state.custom_hand_cards)} more cards to analyze the hand.")
    
    @staticmethod
    def _show_card_selector():
        """Show interactive card selector."""
        st.markdown("**Select cards by clicking:**")
        
        # Create card grid
        suits = [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]
        ranks = [Rank.ACE, Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX,
                Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
        
        for suit in suits:
            st.markdown(f"**{suit.value} {CardDisplay.SUIT_SYMBOLS[suit]}**")
            cols = st.columns(13)
            
            for i, rank in enumerate(ranks):
                with cols[i]:
                    card = Card(rank, suit)
                    is_selected = card in st.session_state.custom_hand_cards
                    
                    # Create button for card selection
                    button_text = f"{rank.value}"
                    button_type = "primary" if is_selected else "secondary"
                    
                    if st.button(button_text, key=f"card_{rank.value}_{suit.value}", type=button_type):
                        if is_selected:
                            # Remove card
                            st.session_state.custom_hand_cards.remove(card)
                        else:
                            # Add card (if not at limit)
                            if len(st.session_state.custom_hand_cards) < 6:
                                st.session_state.custom_hand_cards.append(card)
                            else:
                                st.error("Maximum 6 cards allowed!")
                        st.rerun()
    
    @staticmethod
    def _show_text_input():
        """Show text input for cards."""
        st.markdown("**Enter cards as text (e.g., 'AH 5D KC QS 10H 7C'):**")
        
        # Input field
        card_text = st.text_input(
            "Cards:",
            placeholder="AH 5D KC QS 10H 7C",
            help="Format: RankSuit (A=Ace, J=Jack, Q=Queen, K=King, H=Hearts, D=Diamonds, C=Clubs, S=Spades)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Parse Cards", type="primary"):
                try:
                    cards = HandAnalyzer._parse_card_text(card_text)
                    if len(cards) == 6:
                        st.session_state.custom_hand_cards = cards
                        st.success("✅ Hand parsed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Expected 6 cards, got {len(cards)}")
                except Exception as e:
                    st.error(f"❌ Error parsing cards: {str(e)}")
        
        with col2:
            if st.button("Clear Hand"):
                st.session_state.custom_hand_cards = []
                st.rerun()
        
        # Show format examples
        with st.expander("Card Format Examples"):
            st.markdown("""
            **Valid formats:**
            - `AH 5D KC QS 10H 7C` (spaces between cards)
            - `AH,5D,KC,QS,10H,7C` (commas between cards)
            - `AH KD QC JS 10S 9H` (mixed ranks)
            
            **Rank codes:**
            - A = Ace, 2-9 = Number cards, 10 = Ten, J = Jack, Q = Queen, K = King
            
            **Suit codes:**
            - H = Hearts ♥️, D = Diamonds ♦️, C = Clubs ♣️, S = Spades ♠️
            """)
    
    @staticmethod
    def _parse_card_text(text: str) -> List[Card]:
        """Parse card text into Card objects."""
        if not text.strip():
            return []
        
        # Split by spaces or commas
        card_strings = text.replace(',', ' ').split()
        cards = []
        
        for card_str in card_strings:
            card_str = card_str.strip().upper()
            if not card_str:
                continue
            
            # Parse rank and suit
            if len(card_str) < 2:
                raise ValueError(f"Invalid card format: {card_str}")
            
            # Handle 10 specially
            if card_str.startswith('10'):
                rank_str = '10'
                suit_str = card_str[2:]
            else:
                rank_str = card_str[:-1]
                suit_str = card_str[-1:]
            
            # Convert to enums
            rank = None
            for r in Rank:
                if r.value == rank_str:
                    rank = r
                    break
            
            if rank is None:
                raise ValueError(f"Invalid rank: {rank_str}")
            
            suit = None
            for s in Suit:
                if s.value == suit_str:
                    suit = s
                    break
            
            if suit is None:
                raise ValueError(f"Invalid suit: {suit_str}")
            
            card = Card(rank, suit)
            if card in cards:
                raise ValueError(f"Duplicate card: {card_str}")
            
            cards.append(card)
        
        return cards
    
    @staticmethod
    def _display_current_hand():
        """Display the currently selected hand."""
        st.subheader("Current Hand")
        
        # Sort cards for display
        sorted_cards = sorted(st.session_state.custom_hand_cards, key=lambda c: (c.rank.sort_order, c.suit.value))
        
        # Display cards
        if len(sorted_cards) <= 6:
            cols = st.columns(len(sorted_cards))
            for i, card in enumerate(sorted_cards):
                with cols[i]:
                    st.markdown(CardDisplay.display_card(card), unsafe_allow_html=True)
        
        # Show as text
        cards_text = " ".join(str(card) for card in sorted_cards)
        st.code(cards_text)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🗑️ Clear All Cards"):
                st.session_state.custom_hand_cards = []
                st.rerun()
        
        with col2:
            if st.button("🎲 Random Hand"):
                # Generate a random 6-card hand
                from .ui_components import HandGenerator
                random_hand = HandGenerator.generate_random_hand()
                st.session_state.custom_hand_cards = random_hand.cards
                st.session_state.custom_dealer_status = random_hand.is_dealer
                st.rerun()
        
        with col3:
            if st.button("📋 Copy Text"):
                st.code(cards_text)
                st.success("Hand copied to display above!")
    
    @staticmethod
    def _show_analysis():
        """Show the hand analysis results."""
        st.subheader("📊 Analysis Results")
        
        try:
            # Create hand object
            hand = Hand(st.session_state.custom_hand_cards, st.session_state.custom_dealer_status)
            engine = CribbageEngine()
            
            # Get optimal discards
            optimal_discards = engine.calculate_optimal_discards(hand)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["Recommendations", "All Options", "Detailed Analysis"])
            
            with tab1:
                HandAnalyzer._show_recommendations(optimal_discards, hand)
            
            with tab2:
                HandAnalyzer._show_all_options(hand, engine)
            
            with tab3:
                HandAnalyzer._show_detailed_analysis(optimal_discards[0], hand, engine)
            
            # Add comparison tab if in one mode
            if len(optimal_discards) == 1:
                # Show comparison with opposite dealer status
                st.subheader("🔄 Dealer vs Non-Dealer Comparison")
                
                opposite_hand = Hand(hand.cards, not hand.is_dealer)
                opposite_optimal = engine.calculate_optimal_discards(opposite_hand)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    current_status = "Dealer" if hand.is_dealer else "Non-Dealer"
                    st.markdown(f"**As {current_status}:**")
                    
                    optimal = optimal_discards[0]
                    sorted_discard = sorted(optimal.cards_to_discard, key=lambda c: (c.rank.sort_order, c.suit.value))
                    cards_str = ", ".join(str(card) for card in sorted_discard)
                    
                    st.success(f"Discard: {cards_str}")
                    st.metric("Expected Score", f"{optimal.expected_score:.2f}")
                
                with col2:
                    opposite_status = "Non-Dealer" if hand.is_dealer else "Dealer"
                    st.markdown(f"**As {opposite_status}:**")
                    
                    opp_optimal = opposite_optimal[0]
                    opp_sorted_discard = sorted(opp_optimal.cards_to_discard, key=lambda c: (c.rank.sort_order, c.suit.value))
                    opp_cards_str = ", ".join(str(card) for card in opp_sorted_discard)
                    
                    if opp_cards_str == cards_str:
                        st.info(f"Discard: {opp_cards_str} (Same!)")
                    else:
                        st.warning(f"Discard: {opp_cards_str} (Different!)")
                    
                    st.metric("Expected Score", f"{opp_optimal.expected_score:.2f}")
                
                # Show difference
                score_diff = optimal.expected_score - opp_optimal.expected_score
                if abs(score_diff) > 0.1:
                    if score_diff > 0:
                        st.success(f"💡 Being {current_status.lower()} is {score_diff:.2f} points better for this hand!")
                    else:
                        st.warning(f"💡 Being {opposite_status.lower()} would be {abs(score_diff):.2f} points better for this hand!")
                else:
                    st.info("💡 Dealer status makes little difference for this hand.")
        
        except Exception as e:
            st.error(f"Error analyzing hand: {str(e)}")
    
    @staticmethod
    def _show_recommendations(optimal_discards: List, hand: Hand):
        """Show optimal discard recommendations."""
        dealer_text = "dealer" if hand.is_dealer else "non-dealer"
        
        if len(optimal_discards) == 1:
            st.success(f"🎯 **Optimal discard as {dealer_text}:**")
            optimal = optimal_discards[0]
            sorted_discard = sorted(optimal.cards_to_discard, key=lambda c: (c.rank.sort_order, c.suit.value))
            cards_str = ", ".join(str(card) for card in sorted_discard)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Discard", cards_str)
            with col2:
                st.metric("Expected Score", f"{optimal.expected_score:.1f}")
            
            st.markdown(f"**Reasoning:** {optimal.reasoning}")
        
        else:
            st.success(f"🎯 **{len(optimal_discards)} equally optimal discards as {dealer_text}:**")
            
            for i, optimal in enumerate(optimal_discards):
                sorted_discard = sorted(optimal.cards_to_discard, key=lambda c: (c.rank.sort_order, c.suit.value))
                cards_str = ", ".join(str(card) for card in sorted_discard)
                
                with st.expander(f"Option {i+1}: {cards_str} (Expected: {optimal.expected_score:.1f})"):
                    st.markdown(f"**Reasoning:** {optimal.reasoning}")
        
        # Show remaining hand for the first option
        st.subheader("Remaining Hand")
        remaining_cards = [card for card in hand.cards if card not in optimal_discards[0].cards_to_discard]
        remaining_cards = sorted(remaining_cards, key=lambda c: (c.rank.sort_order, c.suit.value))
        
        cols = st.columns(len(remaining_cards))
        for i, card in enumerate(remaining_cards):
            with cols[i]:
                st.markdown(CardDisplay.display_card(card), unsafe_allow_html=True)
    
    @staticmethod
    def _show_all_options(hand: Hand, engine: CribbageEngine):
        """Show all discard options ranked."""
        options = engine.get_all_discard_options(hand)
        sorted_options = sorted(options, key=lambda x: x.total_expected_value, reverse=True)
        
        # Create table
        data = []
        for i, option in enumerate(sorted_options):
            sorted_discard = sorted(option.discard, key=lambda c: (c.rank.sort_order, c.suit.value))
            discard_str = ", ".join(str(card) for card in sorted_discard)
            
            data.append({
                "Rank": i + 1,
                "Discard": discard_str,
                "Expected Score": f"{option.total_expected_value:.2f}",
                "Hand Score": f"{option.expected_hand_score:.2f}",
                "Crib Impact": f"{option.expected_crib_impact:.2f}"
            })
        
        st.dataframe(data, use_container_width=True)
        
        # Highlight top choices
        top_3 = sorted_options[:3]
        st.subheader("Top 3 Choices")
        for i, option in enumerate(top_3):
            sorted_discard = sorted(option.discard, key=lambda c: (c.rank.sort_order, c.suit.value))
            cards_str = ", ".join(str(card) for card in sorted_discard)
            
            if i == 0:
                st.success(f"🥇 **Best:** {cards_str} ({option.total_expected_value:.2f} points)")
            elif i == 1:
                st.info(f"🥈 **2nd:** {cards_str} ({option.total_expected_value:.2f} points)")
            else:
                st.warning(f"🥉 **3rd:** {cards_str} ({option.total_expected_value:.2f} points)")
    
    @staticmethod
    def _show_detailed_analysis(optimal: object, hand: Hand, engine: CribbageEngine):
        """Show detailed analysis of the optimal choice."""
        st.markdown("**Detailed breakdown of the optimal choice:**")
        
        # Show what cards are kept
        kept_cards = [card for card in hand.cards if card not in optimal.cards_to_discard]
        kept_cards = sorted(kept_cards, key=lambda c: (c.rank.sort_order, c.suit.value))
        
        st.markdown("**Cards you keep:**")
        cols = st.columns(len(kept_cards))
        for i, card in enumerate(kept_cards):
            with cols[i]:
                st.markdown(CardDisplay.display_card(card), unsafe_allow_html=True)
        
        # Show scoring potential
        FeedbackDisplay._show_scoring_potential(kept_cards, "Your kept cards")
        
        # Show strategy explanation
        st.subheader("Strategy Explanation")
        dealer_tips = FeedbackDisplay._get_strategy_tips(hand.is_dealer)
        for tip in dealer_tips:
            st.markdown(f"💡 {tip}")
