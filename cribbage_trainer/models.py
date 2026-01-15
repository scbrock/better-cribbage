"""
Core data models for the cribbage trainer application.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class Suit(Enum):
    """Card suits in a standard deck."""
    HEARTS = 'H'
    DIAMONDS = 'D'
    CLUBS = 'C'
    SPADES = 'S'


class Rank(Enum):
    """Card ranks in a standard deck."""
    ACE = 'A'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'

    @property
    def numeric_value(self) -> int:
        """Get the numeric value of the rank for cribbage scoring."""
        if self == Rank.ACE:
            return 1
        elif self in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            # Convert the string value to int for numbered cards
            return int(self.value)

    @property
    def cribbage_value(self) -> int:
        """Get the cribbage value (for fifteens and runs)."""
        return self.numeric_value
    
    @property
    def sort_order(self) -> int:
        """Get the sort order for displaying cards (A=1, 2=2, ..., 10=10, J=11, Q=12, K=13)."""
        rank_order = {
            Rank.ACE: 1,
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13
        }
        return rank_order[self]


@dataclass
class Card:
    """Represents a playing card."""
    rank: Rank
    suit: Suit
    
    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit


@dataclass
class Hand:
    """Represents a 6-card cribbage hand."""
    cards: List[Card]
    is_dealer: bool
    
    def __post_init__(self):
        if len(self.cards) != 6:
            raise ValueError("Hand must contain exactly 6 cards")
        
        # Check for duplicates
        if len(set(self.cards)) != 6:
            raise ValueError("Hand cannot contain duplicate cards")
        
        # Sort cards by sort order and suit for consistent display
        self.cards = sorted(self.cards, key=lambda c: (c.rank.sort_order, c.suit.value))


@dataclass
class OptimalDiscard:
    """Represents the optimal discard choice for a hand."""
    cards_to_discard: List[Card]
    expected_score: float
    reasoning: str
    
    def __post_init__(self):
        if len(self.cards_to_discard) != 2:
            raise ValueError("Must discard exactly 2 cards")


@dataclass
class DiscardOption:
    """Represents a possible discard choice with its evaluation."""
    discard: List[Card]
    expected_hand_score: float
    expected_crib_impact: float
    total_expected_value: float
    
    def __post_init__(self):
        if len(self.discard) != 2:
            raise ValueError("Discard must contain exactly 2 cards")


@dataclass
class EvaluationResult:
    """Result of evaluating a user's discard choice."""
    points_awarded: int  # 0 or 1
    optimal_discard: OptimalDiscard
    user_choice_expected_value: float
    point_difference: float
    feedback_message: str
    
    def __post_init__(self):
        if self.points_awarded not in [0, 1]:
            raise ValueError("Points awarded must be 0 or 1")


@dataclass
class SessionSummary:
    """Summary of a training session."""
    total_attempts: int
    correct_choices: int
    session_score: int
    
    @property
    def accuracy_percentage(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_choices / self.total_attempts) * 100


@dataclass
class UserStats:
    """Overall user statistics across all sessions."""
    total_attempts: int = 0
    correct_choices: int = 0
    total_sessions: int = 0
    session_scores: List[int] = field(default_factory=list)
    
    @property
    def accuracy_percentage(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_choices / self.total_attempts) * 100
    
    @property
    def average_session_score(self) -> float:
        if not self.session_scores:
            return 0.0
        return sum(self.session_scores) / len(self.session_scores)