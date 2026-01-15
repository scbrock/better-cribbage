"""
Feedback and educational components for the cribbage trainer.
"""

import streamlit as st
from typing import List, Dict, Tuple
import itertools

from cribbage_trainer.models import Card, Hand, OptimalDiscard, DiscardOption, Rank
from cribbage_trainer.scoring import CribbageScorer
from cribbage_trainer.engine import CribbageEngine


class FeedbackDisplay:
    """Handles detailed feedback and educational content display."""
    
    @staticmethod
    def show_detailed_results(
        hand: Hand, 
        user_discard: List[Card], 
        optimal_discard: OptimalDiscard,
        engine: CribbageEngine,
        all_optimal_discards: List[OptimalDiscard] = None
    ):
        """
        Display comprehensive results and feedback.
        
        Args:
            hand: The original 6-card hand
            user_discard: Cards the user chose to discard
            optimal_discard: The primary optimal discard choice
            engine: The cribbage engine for calculations
            all_optimal_discards: List of all optimal discards (for ties)
        """
        if all_optimal_discards is None:
            all_optimal_discards = [optimal_discard]
        
        user_discard_set = set(user_discard)
        is_optimal = any(
            user_discard_set == set(optimal.cards_to_discard) 
            for optimal in all_optimal_discards
        )
        
        # Main result
        if is_optimal:
            st.success("🎉 Excellent! You chose the optimal discard!")
        else:
            st.error("❌ Not optimal, but good try!")
        
        # Create tabs for different types of feedback
        tab1, tab2, tab3, tab4 = st.tabs(["Results", "Analysis", "Learning", "All Options"])
        
        with tab1:
            FeedbackDisplay._show_basic_results(hand, user_discard, optimal_discard, engine, is_optimal, all_optimal_discards)
        
        with tab2:
            FeedbackDisplay._show_detailed_analysis(hand, user_discard, optimal_discard, engine)
        
        with tab3:
            FeedbackDisplay._show_educational_content(hand, user_discard, optimal_discard, is_optimal)
        
        with tab4:
            FeedbackDisplay._show_all_options(hand, engine)
    
    @staticmethod
    def _show_basic_results(
        hand: Hand, 
        user_discard: List[Card], 
        optimal_discard: OptimalDiscard,
        engine: CribbageEngine,
        is_optimal: bool,
        all_optimal_discards: List[OptimalDiscard]
    ):
        """Show basic results comparison."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Choice")
            user_cards_str = ", ".join(str(card) for card in user_discard)
            st.markdown(f"**Discarded:** {user_cards_str}")
            
            # Calculate user's expected value
            user_options = engine.get_all_discard_options(hand)
            user_option = next((opt for opt in user_options if set(opt.discard) == set(user_discard)), None)
            
            if user_option:
                st.metric("Expected Score", f"{user_option.total_expected_value:.1f}")
                st.metric("Hand Score", f"{user_option.expected_hand_score:.1f}")
                st.metric("Crib Impact", f"{user_option.expected_crib_impact:.1f}")
        
        with col2:
            st.subheader("Optimal Choice(s)")
            
            if len(all_optimal_discards) > 1:
                st.markdown(f"**{len(all_optimal_discards)} equally optimal discards:**")
                for i, opt_discard in enumerate(all_optimal_discards):
                    cards_str = ", ".join(str(card) for card in sorted(opt_discard.cards_to_discard, key=lambda c: (c.rank.value, c.suit.value)))
                    st.markdown(f"• {cards_str}")
            else:
                optimal_cards_str = ", ".join(str(card) for card in sorted(optimal_discard.cards_to_discard, key=lambda c: (c.rank.value, c.suit.value)))
                st.markdown(f"**Discarded:** {optimal_cards_str}")
            
            st.metric("Expected Score", f"{optimal_discard.expected_score:.1f}")
            
            # Find optimal option details
            optimal_option = next((opt for opt in user_options if set(opt.discard) == set(optimal_discard.cards_to_discard)), None)
            if optimal_option:
                st.metric("Hand Score", f"{optimal_option.expected_hand_score:.1f}")
                st.metric("Crib Impact", f"{optimal_option.expected_crib_impact:.1f}")
        
        # Show difference if not optimal
        if not is_optimal and user_option:
            difference = optimal_discard.expected_score - user_option.total_expected_value
            st.warning(f"💡 The optimal choice would score {difference:.1f} more points on average")
    
    @staticmethod
    def _show_detailed_analysis(
        hand: Hand, 
        user_discard: List[Card], 
        optimal_discard: OptimalDiscard,
        engine: CribbageEngine
    ):
        """Show detailed scoring analysis."""
        st.subheader("Detailed Analysis")
        
        # Show what cards are kept in each scenario
        user_keep = [card for card in hand.cards if card not in user_discard]
        optimal_keep = [card for card in hand.cards if card not in optimal_discard.cards_to_discard]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Kept Cards:**")
            kept_cards_str = ", ".join(str(card) for card in user_keep)
            st.markdown(f"- {kept_cards_str}")
            
            # Show scoring potential
            FeedbackDisplay._show_scoring_potential(user_keep, "Your hand")
        
        with col2:
            st.markdown("**Optimal Kept Cards:**")
            optimal_kept_str = ", ".join(str(card) for card in optimal_keep)
            st.markdown(f"- {optimal_kept_str}")
            
            # Show scoring potential
            FeedbackDisplay._show_scoring_potential(optimal_keep, "Optimal hand")
        
        # Show reasoning
        st.subheader("Why This Choice is Optimal")
        st.markdown(optimal_discard.reasoning)
    
    @staticmethod
    def _show_scoring_potential(cards: List[Card], title: str):
        """Show the scoring potential of a set of cards."""
        if len(cards) != 4:
            return
        
        st.markdown(f"**{title} scoring potential:**")
        
        # Check for pairs
        rank_counts = {}
        for card in cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        pairs = [rank for rank, count in rank_counts.items() if count >= 2]
        if pairs:
            st.markdown(f"- Pairs: {', '.join(rank.value for rank in pairs)}")
        
        # Check for fifteen combinations
        fifteen_combos = FeedbackDisplay._find_fifteen_combinations(cards)
        if fifteen_combos:
            st.markdown(f"- Fifteens: {len(fifteen_combos)} combinations")
        
        # Check for run potential
        run_length = FeedbackDisplay._find_run_potential(cards)
        if run_length >= 3:
            st.markdown(f"- Run potential: {run_length} consecutive ranks")
        
        # Check for flush potential
        suits = [card.suit for card in cards]
        if len(set(suits)) == 1:
            st.markdown(f"- Flush: All {suits[0].value}")
    
    @staticmethod
    def _find_fifteen_combinations(cards: List[Card]) -> List[List[Card]]:
        """Find all combinations that sum to 15."""
        combinations = []
        
        for r in range(2, len(cards) + 1):
            for combo in itertools.combinations(cards, r):
                if sum(card.rank.numeric_value for card in combo) == 15:
                    combinations.append(list(combo))
        
        return combinations
    
    @staticmethod
    def _find_run_potential(cards: List[Card]) -> int:
        """Find the longest potential run in the cards."""
        rank_values = []
        for card in cards:
            if card.rank == Rank.ACE:
                rank_values.append(1)
            elif card.rank == Rank.JACK:
                rank_values.append(11)
            elif card.rank == Rank.QUEEN:
                rank_values.append(12)
            elif card.rank == Rank.KING:
                rank_values.append(13)
            else:
                rank_values.append(int(card.rank.value))
        
        unique_values = sorted(set(rank_values))
        
        if len(unique_values) < 3:
            return 0
        
        max_run = 1
        current_run = 1
        
        for i in range(1, len(unique_values)):
            if unique_values[i] == unique_values[i-1] + 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        
        return max_run
    
    @staticmethod
    def _show_educational_content(
        hand: Hand, 
        user_discard: List[Card], 
        optimal_discard: OptimalDiscard,
        is_optimal: bool
    ):
        """Show educational tips and concepts."""
        st.subheader("Learning Points")
        
        if is_optimal:
            st.success("🎓 Great job! Here's what you did right:")
            tips = FeedbackDisplay._get_positive_tips(hand, optimal_discard)
        else:
            st.info("🎓 Learning opportunity! Here's what to consider:")
            tips = FeedbackDisplay._get_improvement_tips(hand, user_discard, optimal_discard)
        
        for tip in tips:
            st.markdown(f"- {tip}")
        
        # General cribbage strategy tips
        st.subheader("General Strategy Tips")
        strategy_tips = FeedbackDisplay._get_strategy_tips(hand.is_dealer)
        
        for tip in strategy_tips:
            st.markdown(f"💡 {tip}")
    
    @staticmethod
    def _get_positive_tips(hand: Hand, optimal_discard: OptimalDiscard) -> List[str]:
        """Generate positive reinforcement tips."""
        tips = []
        
        discard = optimal_discard.cards_to_discard
        keep = [card for card in hand.cards if card not in discard]
        
        # Check what they did well
        rank_counts = {}
        for card in keep:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        if any(count >= 2 for count in rank_counts.values()):
            tips.append("You kept a pair, which guarantees points!")
        
        fifteen_combos = FeedbackDisplay._find_fifteen_combinations(keep)
        if fifteen_combos:
            tips.append("You kept cards that can form fifteens!")
        
        run_potential = FeedbackDisplay._find_run_potential(keep)
        if run_potential >= 3:
            tips.append("You kept cards with good run potential!")
        
        if hand.is_dealer:
            tips.append("As dealer, you correctly prioritized your hand while considering crib potential!")
        else:
            tips.append("As non-dealer, you correctly minimized what you gave to the opponent's crib!")
        
        return tips if tips else ["You made the mathematically optimal choice!"]
    
    @staticmethod
    def _get_improvement_tips(
        hand: Hand, 
        user_discard: List[Card], 
        optimal_discard: OptimalDiscard
    ) -> List[str]:
        """Generate improvement tips."""
        tips = []
        
        user_keep = [card for card in hand.cards if card not in user_discard]
        optimal_keep = [card for card in hand.cards if card not in optimal_discard.cards_to_discard]
        
        # Compare what they kept vs optimal
        user_pairs = sum(1 for rank, count in 
                        {card.rank: sum(1 for c in user_keep if c.rank == card.rank) 
                         for card in user_keep}.items() if count >= 2)
        optimal_pairs = sum(1 for rank, count in 
                           {card.rank: sum(1 for c in optimal_keep if c.rank == card.rank) 
                            for card in optimal_keep}.items() if count >= 2)
        
        if optimal_pairs > user_pairs:
            tips.append("The optimal choice keeps more pairs for guaranteed points")
        
        user_fifteens = len(FeedbackDisplay._find_fifteen_combinations(user_keep))
        optimal_fifteens = len(FeedbackDisplay._find_fifteen_combinations(optimal_keep))
        
        if optimal_fifteens > user_fifteens:
            tips.append("The optimal choice has better fifteen potential")
        
        user_run = FeedbackDisplay._find_run_potential(user_keep)
        optimal_run = FeedbackDisplay._find_run_potential(optimal_keep)
        
        if optimal_run > user_run:
            tips.append("The optimal choice has better run potential")
        
        return tips if tips else ["Consider the expected value calculation more carefully"]
    
    @staticmethod
    def _get_strategy_tips(is_dealer: bool) -> List[str]:
        """Get general strategy tips based on dealer status."""
        if is_dealer:
            return [
                "As dealer, you get the crib, so consider what you discard to it",
                "Pairs, fifteens, and fives are valuable in the crib",
                "Balance your hand score with crib potential"
            ]
        else:
            return [
                "As non-dealer, minimize what you give to opponent's crib",
                "Avoid discarding pairs, fifteens, or fives when possible",
                "Focus on maximizing your hand score"
            ]
    
    @staticmethod
    def _show_all_options(hand: Hand, engine: CribbageEngine):
        """Show all possible discard options ranked by expected value."""
        st.subheader("All Possible Discards (Ranked)")
        
        options = engine.get_all_discard_options(hand)
        sorted_options = sorted(options, key=lambda x: x.total_expected_value, reverse=True)
        
        # Create a table of all options
        data = []
        for i, option in enumerate(sorted_options):
            # Sort discard cards for display
            sorted_discard = sorted(option.discard, key=lambda c: (c.rank.value, c.suit.value))
            discard_str = ", ".join(str(card) for card in sorted_discard)
            data.append({
                "Rank": i + 1,
                "Discard": discard_str,
                "Expected Score": f"{option.total_expected_value:.1f}",
                "Hand Score": f"{option.expected_hand_score:.1f}",
                "Crib Impact": f"{option.expected_crib_impact:.1f}"
            })
        
        st.table(data)