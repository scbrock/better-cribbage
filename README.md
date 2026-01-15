# 🃏 Cribbage Trainer

A Streamlit web application that helps players improve their cribbage skills by practicing optimal discard decisions.

## Features

### 🎓 Training Mode
- Practice with randomly generated hands
- Get scored on your discard choices
- Track your progress and accuracy over time
- Detailed feedback on optimal vs. suboptimal choices
- Educational explanations of scoring rules

### 🔍 Hand Analyzer
- Enter custom hands (visual selector or text input)
- Get optimal discard recommendations for dealer/non-dealer positions
- Compare expected values across different discard options
- Generate random hands for quick analysis

### 📊 Progress Tracking
- Accuracy percentage and session statistics
- Interactive charts showing improvement over time
- Detailed performance insights
- Session-by-session score tracking

## How to Play Cribbage

Cribbage is a classic card game where players try to score points through various combinations:
- **Pairs**: Two cards of the same rank (2 points)
- **Fifteens**: Cards that sum to 15 (2 points)
- **Runs**: Consecutive cards (1 point per card)
- **Flush**: All cards same suit (4-5 points)
- **Nobs**: Jack matching the cut card suit (1 point)

## Live Demo

🚀 **[Try the app live on Streamlit Community Cloud](https://scbrock-better-cribbage-streamlit-app-xyz123.streamlit.app)**

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/scbrock/better-cribbage.git
   cd better-cribbage
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure

```
├── streamlit_app.py          # Main entry point for Streamlit
├── run_app.py               # Alternative entry point
├── requirements.txt         # Python dependencies
├── cribbage_trainer/        # Main application package
│   ├── app.py              # Core Streamlit application
│   ├── models.py           # Data models (Hand, Card, UserStats)
│   ├── engine.py           # Cribbage game engine and optimal play calculation
│   ├── scoring.py          # Cribbage scoring rules implementation
│   ├── ui_components.py    # Reusable UI components
│   ├── session_manager.py  # Session state management
│   ├── feedback.py         # Result feedback and explanations
│   ├── progress_display.py # Progress tracking and visualization
│   └── hand_analyzer.py    # Custom hand analysis features
```

## Technical Details

### Optimal Play Calculation
The app calculates optimal discards by:
1. Evaluating all possible 2-card discards from a 6-card hand
2. Computing expected value across all 46 possible cut cards
3. Considering both hand scoring and crib value (dealer vs. non-dealer)
4. Handling ties within a small tolerance (0.01 points)

### Scoring Engine
Implements complete cribbage scoring rules:
- Pairs, fifteens, runs, flush, and nobs
- Proper handling of edge cases and combinations
- Efficient algorithms for complex hands

### User Experience
- Clean, intuitive interface with card visualizations
- Real-time feedback and educational content
- Progress persistence across sessions
- Responsive design for desktop and mobile

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).