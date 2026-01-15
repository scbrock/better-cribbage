"""
Main Streamlit application for the Cribbage Trainer.
"""

import streamlit as st
from typing import Optional

from cribbage_trainer.models import Hand, UserStats
from cribbage_trainer.session_manager import SessionManager
from cribbage_trainer.ui_components import CardDisplay, HandGenerator, GameControls
from cribbage_trainer.engine import CribbageEngine


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Cribbage Trainer",
        page_icon="🃏",
        layout="centered",  # Changed from "wide" to "centered" for better mobile experience
        initial_sidebar_state="auto"
    )
    
    # Initialize session state
    SessionManager.initialize_session()
    
    # Initialize show_progress state
    if 'show_progress' not in st.session_state:
        st.session_state.show_progress = False
    
    # Initialize app mode
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'training'  # 'training' or 'analyzer'
    
    # Check if we should show progress view
    if st.session_state.show_progress:
        show_progress_view()
        return
    
    # Main navigation
    st.title("🃏 Cribbage Trainer")
    
    # Mode selection
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.radio(
            "Choose Mode:",
            options=['training', 'analyzer'],
            format_func=lambda x: "🎓 Training Mode" if x == 'training' else "🔍 Hand Analyzer",
            index=0 if st.session_state.app_mode == 'training' else 1,
            horizontal=True,
            key="mode_selector"
        )
        
        if mode != st.session_state.app_mode:
            st.session_state.app_mode = mode
            st.rerun()
    
    st.divider()
    
    # Show appropriate interface based on mode
    if st.session_state.app_mode == 'training':
        show_training_mode()
    else:
        show_analyzer_mode()


def show_training_mode():
    """Show the training mode interface."""
    st.markdown("**Training Mode:** Practice with random hands and get scored on your choices!")
    
    # Initialize engine
    if 'engine' not in st.session_state:
        st.session_state.engine = CribbageEngine()
    
    # Sidebar for navigation and stats
    with st.sidebar:
        st.header("Your Progress")
        stats = SessionManager.get_user_stats()
        
        if stats.total_attempts > 0:
            st.metric("Accuracy", f"{stats.accuracy_percentage:.1f}%")
            st.metric("Total Attempts", stats.total_attempts)
            st.metric("Correct Choices", stats.correct_choices)
            st.metric("Sessions Completed", stats.total_sessions)
            
            if stats.session_scores:
                st.metric("Average Session Score", f"{stats.average_session_score:.1f}")
        else:
            st.info("Start training to see your progress!")
        
        st.divider()
        
        # Progress controls
        progress_action = GameControls.render_progress_controls()
        if progress_action == "view_progress":
            st.session_state.show_progress = True
            st.rerun()
        elif progress_action == "reset_progress":
            SessionManager.reset_all_progress()
            st.success("Progress reset!")
            st.rerun()
    
    # Main content area
    st.header("Training Session")
    
    current_hand = SessionManager.get_current_hand()
    
    if current_hand is None:
        # No current hand - show start screen
        st.info("Click 'New Hand' to begin training!")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("New Hand", type="primary", use_container_width=True):
                new_hand = HandGenerator.generate_random_hand()
                SessionManager.set_current_hand(new_hand)
                SessionManager.clear_selected_cards()
                st.rerun()
    
    else:
        # Display current hand and handle interactions
        selected_cards = CardDisplay.display_hand_with_selection(current_hand)
        
        st.divider()
        
        # Action buttons
        action = GameControls.render_action_buttons(selected_cards)
        
        if action == "submit":
            handle_discard_submission(current_hand, selected_cards)
        elif action == "new_hand":
            new_hand = HandGenerator.generate_random_hand()
            SessionManager.set_current_hand(new_hand)
            SessionManager.clear_selected_cards()
            st.rerun()
        elif action == "clear_selection":
            SessionManager.clear_selected_cards()
            st.rerun()


def show_analyzer_mode():
    """Show the hand analyzer mode interface."""
    from cribbage_trainer.hand_analyzer import HandAnalyzer
    
    st.markdown("**Hand Analyzer:** Enter your own cards and get optimal discard recommendations!")
    
    # Show the hand analyzer
    HandAnalyzer.show_hand_analyzer()


def show_progress_view():
    """Display the progress view."""
    from cribbage_trainer.progress_display import ProgressDisplay
    
    # Back button
    if st.button("← Back to Training", type="secondary"):
        st.session_state.show_progress = False
        st.rerun()
    
    # Show detailed progress
    ProgressDisplay.show_detailed_progress()


def handle_discard_submission(hand: Hand, selected_cards: list):
    """Handle the submission of a discard choice."""
    engine = st.session_state.engine
    
    try:
        # Calculate all optimal discards (to handle ties)
        optimal_discards = engine.calculate_optimal_discards(hand)
        
        # Check if user's choice matches any optimal discard
        user_discard_set = set(selected_cards)
        is_optimal = any(
            user_discard_set == set(optimal.cards_to_discard) 
            for optimal in optimal_discards
        )
        
        # Get the primary optimal discard for display
        primary_optimal = optimal_discards[0]
        
        # Import and use the enhanced feedback display
        from cribbage_trainer.feedback import FeedbackDisplay
        
        # Show detailed results
        FeedbackDisplay.show_detailed_results(hand, selected_cards, primary_optimal, engine, optimal_discards)
        
        # Show remaining cards
        st.subheader("Your Final Hand")
        CardDisplay.display_remaining_cards(hand, selected_cards)
        
        # Update statistics
        stats = SessionManager.get_user_stats()
        stats.total_attempts += 1
        if is_optimal:
            stats.correct_choices += 1
        SessionManager.update_user_stats(stats)
        
        # Record attempt in current session
        SessionManager.record_attempt_result(is_optimal)
        
        # Clear current hand and selection
        SessionManager.set_current_hand(None)
        SessionManager.clear_selected_cards()
        
        st.divider()
        
        # Next action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Continue Training", type="primary", use_container_width=True):
                new_hand = HandGenerator.generate_random_hand()
                SessionManager.set_current_hand(new_hand)
                st.rerun()
        
        with col2:
            if st.button("View Progress", use_container_width=True):
                st.session_state.show_progress = True
                st.rerun()
        
    except Exception as e:
        st.error(f"Error calculating optimal discard: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()