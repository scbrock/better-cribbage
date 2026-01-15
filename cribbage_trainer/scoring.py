"""
Cribbage hand scoring engine.

Implements all cribbage scoring rules:
- Pairs: 2 points per pair
- Fifteens: 2 points per combination summing to 15
- Runs: 1 point per card in consecutive sequence
- Flush: 4 points (hand), 5 points (hand + cut)
- Nobs: 1 point for Jack matching cut suit
"""

from typing import List, Set, Tuple
from collections import Counter
import itertools

from cribbage_trainer.models import Card, Rank, Suit


class CribbageScorer:
    """Handles all cribbage hand scoring calculations."""
    
    @staticmethod
    def calculate_hand_score(hand_cards: List[Card], cut_card: Card) -> int:
        """
        Calculate the total score for a 4-card hand plus cut card.
        
        Args:
            hand_cards: List of 4 cards in the hand
            cut_card: The cut card
            
        Returns:
            Total points scored by the hand
        """
        if len(hand_cards) != 4:
            raise ValueError("Hand must contain exactly 4 cards")
        
        all_cards = hand_cards + [cut_card]
        
        score = 0
        score += CribbageScorer._score_pairs(all_cards)
        score += CribbageScorer._score_fifteens(all_cards)
        score += CribbageScorer._score_runs(all_cards)
        score += CribbageScorer._score_flush(hand_cards, cut_card)
        score += CribbageScorer._score_nobs(hand_cards, cut_card)
        
        return score
    
    @staticmethod
    def _score_pairs(cards: List[Card]) -> int:
        """Score pairs in the hand. Each pair is worth 2 points."""
        rank_counts = Counter(card.rank for card in cards)
        score = 0
        
        for count in rank_counts.values():
            if count >= 2:
                # Number of pairs from n cards of same rank = n * (n-1) / 2
                # Each pair is worth 2 points
                pairs = count * (count - 1) // 2
                score += pairs * 2
        
        return score
    
    @staticmethod
    def _score_fifteens(cards: List[Card]) -> int:
        """Score fifteens in the hand. Each combination summing to 15 is worth 2 points."""
        score = 0
        
        # Check all possible combinations of cards
        for r in range(2, len(cards) + 1):
            for combo in itertools.combinations(cards, r):
                if sum(card.rank.numeric_value for card in combo) == 15:
                    score += 2
        
        return score
    
    @staticmethod
    def _score_runs(cards: List[Card]) -> int:
        """Score runs (consecutive sequences). Each card in a run scores 1 point."""
        rank_counts = Counter(card.rank for card in cards)
        
        # Convert ranks to numeric values for sorting
        rank_values = {}
        for rank in rank_counts.keys():
            if rank == Rank.ACE:
                rank_values[1] = rank_counts[rank]
            elif rank == Rank.JACK:
                rank_values[11] = rank_counts[rank]
            elif rank == Rank.QUEEN:
                rank_values[12] = rank_counts[rank]
            elif rank == Rank.KING:
                rank_values[13] = rank_counts[rank]
            else:
                rank_values[int(rank.value)] = rank_counts[rank]
        
        # Find the longest consecutive sequence
        sorted_values = sorted(rank_values.keys())
        
        if len(sorted_values) < 3:
            return 0  # Need at least 3 cards for a run
        
        # Find consecutive sequences
        current_run_length = 1
        max_run_length = 1
        run_multiplier = 1
        
        for i in range(1, len(sorted_values)):
            if sorted_values[i] == sorted_values[i-1] + 1:
                current_run_length += 1
            else:
                if current_run_length >= 3:
                    max_run_length = current_run_length
                    # Calculate multiplier (product of counts for each rank in the run)
                    run_multiplier = 1
                    for j in range(i - current_run_length, i):
                        run_multiplier *= rank_values[sorted_values[j]]
                current_run_length = 1
        
        # Check the final sequence
        if current_run_length >= 3:
            max_run_length = current_run_length
            run_multiplier = 1
            for j in range(len(sorted_values) - current_run_length, len(sorted_values)):
                run_multiplier *= rank_values[sorted_values[j]]
        
        if max_run_length >= 3:
            return max_run_length * run_multiplier
        
        return 0
    
    @staticmethod
    def _score_flush(hand_cards: List[Card], cut_card: Card) -> int:
        """Score flush. 4 points if all hand cards same suit, 5 if cut card matches too."""
        hand_suits = [card.suit for card in hand_cards]
        
        # Check if all hand cards are the same suit
        if len(set(hand_suits)) == 1:
            hand_suit = hand_suits[0]
            if cut_card.suit == hand_suit:
                return 5  # All 5 cards same suit
            else:
                return 4  # Only hand cards same suit
        
        return 0
    
    @staticmethod
    def _score_nobs(hand_cards: List[Card], cut_card: Card) -> int:
        """Score nobs. 1 point if hand contains Jack matching cut card's suit."""
        for card in hand_cards:
            if card.rank == Rank.JACK and card.suit == cut_card.suit:
                return 1
        return 0
    
    @staticmethod
    def get_scoring_breakdown(hand_cards: List[Card], cut_card: Card) -> dict:
        """
        Get a detailed breakdown of how points were scored.
        
        Returns:
            Dictionary with scoring details for each category
        """
        if len(hand_cards) != 4:
            raise ValueError("Hand must contain exactly 4 cards")
        
        all_cards = hand_cards + [cut_card]
        
        breakdown = {
            'pairs': CribbageScorer._score_pairs(all_cards),
            'fifteens': CribbageScorer._score_fifteens(all_cards),
            'runs': CribbageScorer._score_runs(all_cards),
            'flush': CribbageScorer._score_flush(hand_cards, cut_card),
            'nobs': CribbageScorer._score_nobs(hand_cards, cut_card),
            'total': 0
        }
        
        breakdown['total'] = sum(breakdown[key] for key in breakdown if key != 'total')
        
        return breakdown