"""
Progress display components for the cribbage trainer.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List

from cribbage_trainer.models import UserStats, SessionSummary
from cribbage_trainer.session_manager import SessionManager


class ProgressDisplay:
    """Handles detailed progress and statistics display."""
    
    @staticmethod
    def show_detailed_progress():
        """Display comprehensive progress information."""
        st.header("📊 Your Progress")
        
        stats = SessionManager.get_user_stats()
        session_history = SessionManager.get_session_history()
        
        if stats.total_attempts == 0:
            st.info("No training data yet. Start practicing to see your progress!")
            return
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Detailed Stats"])
        
        with tab1:
            ProgressDisplay._show_overview(stats)
        
        with tab2:
            ProgressDisplay._show_trends(stats, session_history)
        
        with tab3:
            ProgressDisplay._show_detailed_stats(stats, session_history)
    
    @staticmethod
    def _show_overview(stats: UserStats):
        """Show overview statistics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Accuracy", 
                f"{stats.accuracy_percentage:.1f}%",
                help="Percentage of optimal choices made"
            )
        
        with col2:
            st.metric(
                "Total Attempts", 
                stats.total_attempts,
                help="Total number of hands practiced"
            )
        
        with col3:
            st.metric(
                "Correct Choices", 
                stats.correct_choices,
                help="Number of optimal discards chosen"
            )
        
        with col4:
            if stats.session_scores:
                st.metric(
                    "Avg Session Score", 
                    f"{stats.average_session_score:.1f}",
                    help="Average score per training session"
                )
            else:
                st.metric("Sessions", stats.total_sessions)
        
        # Progress bar
        st.subheader("Accuracy Progress")
        progress_color = "green" if stats.accuracy_percentage >= 70 else "orange" if stats.accuracy_percentage >= 50 else "red"
        st.progress(stats.accuracy_percentage / 100)
        
        # Performance level
        if stats.accuracy_percentage >= 80:
            st.success("🏆 Excellent! You're making optimal choices most of the time!")
        elif stats.accuracy_percentage >= 60:
            st.info("📈 Good progress! Keep practicing to improve your accuracy.")
        elif stats.accuracy_percentage >= 40:
            st.warning("📚 Learning phase. Focus on understanding the feedback.")
        else:
            st.error("🎯 Keep practicing! Every expert was once a beginner.")
    
    @staticmethod
    def _show_trends(stats: UserStats, session_history: List[SessionSummary]):
        """Show trend analysis and charts."""
        if not session_history or len(session_history) < 2:
            st.info("Complete more sessions to see trend analysis.")
            return
        
        st.subheader("Performance Trends")
        
        # Create session data for plotting
        session_data = []
        for i, session in enumerate(session_history):
            session_data.append({
                'Session': i + 1,
                'Accuracy': session.accuracy_percentage,
                'Score': session.session_score,
                'Attempts': session.total_attempts
            })
        
        df = pd.DataFrame(session_data)
        
        # Accuracy trend
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Accuracy Trend")
            fig_accuracy = px.line(
                df, 
                x='Session', 
                y='Accuracy',
                title="Accuracy Over Time",
                markers=True
            )
            fig_accuracy.update_layout(
                yaxis_title="Accuracy (%)",
                xaxis_title="Session Number"
            )
            st.plotly_chart(fig_accuracy, use_container_width=True)
        
        with col2:
            st.subheader("Session Scores")
            fig_scores = px.bar(
                df, 
                x='Session', 
                y='Score',
                title="Scores by Session"
            )
            fig_scores.update_layout(
                yaxis_title="Score",
                xaxis_title="Session Number"
            )
            st.plotly_chart(fig_scores, use_container_width=True)
        
        # Calculate trend
        if len(session_history) >= 3:
            recent_accuracy = sum(s.accuracy_percentage for s in session_history[-3:]) / 3
            early_accuracy = sum(s.accuracy_percentage for s in session_history[:3]) / 3
            improvement = recent_accuracy - early_accuracy
            
            if improvement > 5:
                st.success(f"📈 Great improvement! Your accuracy has increased by {improvement:.1f}% over recent sessions.")
            elif improvement > 0:
                st.info(f"📊 Steady progress! Your accuracy has improved by {improvement:.1f}%.")
            elif improvement > -5:
                st.warning("📉 Accuracy is stable. Try focusing on the feedback to improve further.")
            else:
                st.error("📉 Consider reviewing the educational content to improve your decision-making.")
    
    @staticmethod
    def _show_detailed_stats(stats: UserStats, session_history: List[SessionSummary]):
        """Show detailed statistics and breakdowns."""
        st.subheader("Detailed Statistics")
        
        # Session history table
        if session_history:
            st.subheader("Session History")
            
            session_data = []
            for i, session in enumerate(session_history):
                session_data.append({
                    'Session': i + 1,
                    'Attempts': session.total_attempts,
                    'Correct': session.correct_choices,
                    'Accuracy': f"{session.accuracy_percentage:.1f}%",
                    'Score': session.session_score
                })
            
            df = pd.DataFrame(session_data)
            st.dataframe(df, use_container_width=True)
        
        # Performance insights
        st.subheader("Performance Insights")
        
        if stats.total_attempts >= 10:
            insights = ProgressDisplay._generate_insights(stats, session_history)
            for insight in insights:
                st.markdown(f"• {insight}")
        else:
            st.info("Complete at least 10 attempts to see performance insights.")
        
        # Goals and recommendations
        st.subheader("Recommendations")
        recommendations = ProgressDisplay._get_recommendations(stats)
        for rec in recommendations:
            st.markdown(f"🎯 {rec}")
    
    @staticmethod
    def _generate_insights(stats: UserStats, session_history: List[SessionSummary]) -> List[str]:
        """Generate performance insights based on statistics."""
        insights = []
        
        # Accuracy insights
        if stats.accuracy_percentage >= 75:
            insights.append("You're consistently making good decisions! Focus on the most challenging scenarios.")
        elif stats.accuracy_percentage >= 50:
            insights.append("You're improving! Pay attention to dealer vs non-dealer strategy differences.")
        else:
            insights.append("Focus on understanding the basic scoring principles and crib strategy.")
        
        # Session consistency
        if len(session_history) >= 3:
            recent_sessions = session_history[-3:]
            accuracy_variance = max(s.accuracy_percentage for s in recent_sessions) - min(s.accuracy_percentage for s in recent_sessions)
            
            if accuracy_variance < 10:
                insights.append("Your performance is becoming more consistent across sessions.")
            else:
                insights.append("Your performance varies between sessions. Try to maintain focus throughout each session.")
        
        # Volume insights
        if stats.total_attempts >= 50:
            insights.append("Great dedication! You've practiced extensively and should see significant improvement.")
        elif stats.total_attempts >= 20:
            insights.append("Good practice volume. Keep going to build stronger intuition.")
        
        return insights
    
    @staticmethod
    def _get_recommendations(stats: UserStats) -> List[str]:
        """Get personalized recommendations based on performance."""
        recommendations = []
        
        if stats.accuracy_percentage < 40:
            recommendations.extend([
                "Review the educational content in the Learning tab after each hand",
                "Focus on understanding pairs, fifteens, and run potential",
                "Pay attention to dealer vs non-dealer strategy differences"
            ])
        elif stats.accuracy_percentage < 70:
            recommendations.extend([
                "Study the 'All Options' tab to understand why other choices score differently",
                "Practice identifying the best crib discards for your dealer status",
                "Focus on hands where you made suboptimal choices"
            ])
        else:
            recommendations.extend([
                "Challenge yourself with more complex scenarios",
                "Focus on marginal decisions where multiple options are close",
                "Consider the advanced strategy concepts in the feedback"
            ])
        
        # Always include general recommendations
        recommendations.extend([
            "Aim for at least 10-15 hands per session for effective learning",
            "Take breaks between sessions to let the concepts sink in"
        ])
        
        return recommendations