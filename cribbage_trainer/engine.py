"""
Cribbage engine for optimal discard calculation and game logic.
"""

from typing import List, Tuple, Dict
import itertools
from collections import defaultdict

from cribbage_trainer.models import Card, Hand, OptimalDiscard, DiscardOption, Rank, Suit
from cribbage_trainer.scoring import CribbageScorer


class CribbageEngine:
    """Main engine for cribbage optimal play calculations."""
    
    def __init__(self):
        """Initialize the cribbage engine."""
        self.scorer = CribbageScorer()
        # Create a full deck for expected value calculations
        self._full_deck = self._create_full_deck()
    
    def _create_full_deck(self) -> List[Card]:
        """Create a standard 52-card deck."""
        deck = []
        for suit in Suit:
            for rank in Rank:
                deck.append(Card(rank, suit))
        return deck
    
    def calculate_optimal_discards(self, hand: Hand, tolerance: float = 0.1) -> List[OptimalDiscard]:
        """
        Find all mathematically optimal discards (within tolerance).
        
        Args:
            hand: The 6-card hand to analyze
            tolerance: Expected value tolerance for considering options equal
            
        Returns:
            List of OptimalDiscard objects for all optimal choices
        """
        all_options = self.get_all_discard_options(hand)
        
        if not all_options:
            raise ValueError("No valid discard options found")
        
        # Find the maximum expected value
        max_value = max(opt.total_expected_value for opt in all_options)
        
        # Find all options within tolerance of the maximum
        optimal_options = [
            opt for opt in all_options 
            if opt.total_expected_value >= max_value - tolerance
        ]
        
        # Convert to OptimalDiscard objects
        optimal_discards = []
        for i, option in enumerate(optimal_options):
            # Generate reasoning
            reasoning = self._generate_reasoning(option, all_options, hand.is_dealer, len(optimal_options) > 1, i)
            
            optimal_discards.append(OptimalDiscard(
                cards_to_discard=sorted(option.discard, key=lambda c: (c.rank.value, c.suit.value)),
                expected_score=option.total_expected_value,
                reasoning=reasoning
            ))
        
        return optimal_discards
    
    def calculate_optimal_discard(self, hand: Hand) -> OptimalDiscard:
        """
        Find the mathematically optimal 2 cards to discard.
        
        Args:
            hand: The 6-card hand to analyze
            
        Returns:
            OptimalDiscard with the best choice and reasoning
        """
        optimal_discards = self.calculate_optimal_discards(hand)
        
        # Return the first optimal choice (they're all equally good)
        return optimal_discards[0]
    
    def get_all_discard_options(self, hand: Hand) -> List[DiscardOption]:
        """
        Get expected values for all possible discard combinations.
        
        Args:
            hand: The 6-card hand to analyze
            
        Returns:
            List of all possible discard options with their evaluations
        """
        options = []
        
        # Generate all possible 2-card discards
        for discard_combo in itertools.combinations(hand.cards, 2):
            discard = list(discard_combo)
            keep_cards = [card for card in hand.cards if card not in discard]
            
            expected_hand_score = self._calculate_expected_hand_score(keep_cards, hand.cards)
            expected_crib_impact = self._calculate_expected_crib_impact(discard, hand.is_dealer)
            
            # Total expected value considers both hand score and crib impact
            dealer_multiplier = 1 if hand.is_dealer else -1
            total_expected_value = expected_hand_score + (expected_crib_impact * dealer_multiplier)
            
            options.append(DiscardOption(
                discard=discard,
                expected_hand_score=expected_hand_score,
                expected_crib_impact=expected_crib_impact,
                total_expected_value=total_expected_value
            ))
        
        return options
    
    def _calculate_expected_hand_score(self, keep_cards: List[Card], original_hand: List[Card]) -> float:
        """
        Calculate expected score for the 4 cards we keep across all possible cut cards.
        
        Args:
            keep_cards: The 4 cards we're keeping
            original_hand: The original 6-card hand (to exclude from possible cuts)
            
        Returns:
            Expected score across all possible cut cards
        """
        if len(keep_cards) != 4:
            raise ValueError("Must keep exactly 4 cards")
        
        total_score = 0
        valid_cuts = 0
        
        # Consider all possible cut cards (excluding cards in original hand)
        for cut_card in self._full_deck:
            if cut_card not in original_hand:
                score = self.scorer.calculate_hand_score(keep_cards, cut_card)
                total_score += score
                valid_cuts += 1
        
        return total_score / valid_cuts if valid_cuts > 0 else 0.0
    
    def _calculate_expected_crib_impact(self, discard: List[Card], is_dealer: bool) -> float:
        """
        Calculate expected impact of discarded cards on crib scoring.
        
        This is a simplified calculation that considers the potential of the
        discarded cards to form scoring combinations in the crib.
        
        Args:
            discard: The 2 cards being discarded
            is_dealer: Whether the player is the dealer
            
        Returns:
            Expected crib impact (positive = good for crib, negative = bad)
        """
        if len(discard) != 2:
            raise ValueError("Must discard exactly 2 cards")
        
        card1, card2 = discard
        impact = 0.0
        
        # Pair bonus - if we discard a pair, that's 2 guaranteed points
        if card1.rank == card2.rank:
            impact += 2.0
        
        # Fifteen potential - if the two cards sum to 15, that's 2 guaranteed points
        if card1.rank.numeric_value + card2.rank.numeric_value == 15:
            impact += 2.0
        
        # Fifteen potential - if either card is a 5, it has good fifteen potential
        for card in discard:
            if card.rank == Rank.FIVE:
                impact += 0.5  # 5s are valuable in cribs
        
        # Run potential - if cards are consecutive, they have run potential
        rank_values = sorted([self._get_run_value(card.rank) for card in discard])
        if len(rank_values) == 2 and rank_values[1] - rank_values[0] == 1:
            impact += 1.0  # Consecutive cards have run potential
        
        # Avoid giving away face cards together (they don't help much)
        face_cards = [Rank.JACK, Rank.QUEEN, Rank.KING]
        if all(card.rank in face_cards for card in discard):
            impact -= 0.5
        
        return impact
    
    def _get_run_value(self, rank: Rank) -> int:
        """Get the numeric value of a rank for run calculations."""
        if rank == Rank.ACE:
            return 1
        elif rank == Rank.JACK:
            return 11
        elif rank == Rank.QUEEN:
            return 12
        elif rank == Rank.KING:
            return 13
        else:
            return int(rank.value)
    
    def _generate_reasoning(self, best_option: DiscardOption, all_options: List[DiscardOption], is_dealer: bool, has_ties: bool = False, tie_index: int = 0) -> str:
        """
        Generate human-readable reasoning for why this discard is optimal.
        
        Args:
            best_option: The optimal discard choice
            all_options: All possible discard options
            is_dealer: Whether the player is the dealer
            
        Returns:
            Explanation string
        """
        reasoning_parts = []
        
        # If there are ties, mention it
        if has_ties and tie_index == 0:
            reasoning_parts.append("Multiple equally optimal choices available")
        
        # Explain the expected hand score
        reasoning_parts.append(f"Expected hand score: {best_option.expected_hand_score:.1f} points")
        
        # Explain crib impact
        crib_impact = best_option.expected_crib_impact
        if is_dealer:
            if crib_impact > 0:
                reasoning_parts.append(f"Good crib potential: +{crib_impact:.1f} points")
            else:
                reasoning_parts.append(f"Neutral crib impact: {crib_impact:.1f} points")
        else:
            if crib_impact > 0:
                reasoning_parts.append(f"Gives opponent {crib_impact:.1f} crib points (unavoidable)")
            else:
                reasoning_parts.append(f"Minimizes opponent's crib by {abs(crib_impact):.1f} points")
        
        # Compare to other options
        sorted_options = sorted(all_options, key=lambda x: x.total_expected_value, reverse=True)
        if len(sorted_options) > 1:
            second_best = sorted_options[1]
            advantage = best_option.total_expected_value - second_best.total_expected_value
            if advantage > 0.1:
                reasoning_parts.append(f"This choice is {advantage:.1f} points better than the next best option")
        
        # Identify key scoring opportunities in the kept cards
        discard_cards = best_option.discard
        keep_cards = [card for card in self._get_sample_hand_cards(best_option) if card not in discard_cards]
        
        if len(keep_cards) == 4:
            scoring_features = self._identify_scoring_features(keep_cards)
            if scoring_features:
                reasoning_parts.append(f"Keeping: {', '.join(scoring_features)}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_sample_hand_cards(self, option: DiscardOption) -> List[Card]:
        """Helper to reconstruct hand cards from discard option (simplified)."""
        # This is a simplified version - in practice we'd need to track the original hand
        # For now, return empty list to avoid errors
        return []
    
    def _identify_scoring_features(self, cards: List[Card]) -> List[str]:
        """
        Identify key scoring features in a set of cards.
        
        Args:
            cards: List of cards to analyze
            
        Returns:
            List of scoring feature descriptions
        """
        features = []
        
        # Check for pairs
        rank_counts = defaultdict(int)
        for card in cards:
            rank_counts[card.rank] += 1
        
        for rank, count in rank_counts.items():
            if count >= 2:
                features.append(f"pair of {rank.value}s")
        
        # Check for fifteen potential
        values = [card.rank.numeric_value for card in cards]
        for combo_size in range(2, len(values) + 1):
            for combo in itertools.combinations(values, combo_size):
                if sum(combo) == 15:
                    features.append("fifteen combination")
                    break
        
        # Check for run potential
        unique_ranks = sorted(set(self._get_run_value(card.rank) for card in cards))
        consecutive_count = 1
        max_consecutive = 1
        
        for i in range(1, len(unique_ranks)):
            if unique_ranks[i] == unique_ranks[i-1] + 1:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1
        
        if max_consecutive >= 3:
            features.append(f"run potential ({max_consecutive} consecutive ranks)")
        
        return features