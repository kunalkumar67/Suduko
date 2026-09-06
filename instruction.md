# GitHub Copilot Instructions for Sudoku Application

## Project Overview

This project is a 9x9 Sudoku web application built using Flask, Python, HTML, CSS, and JavaScript. The goal is to refactor legacy code into clean, modular, and maintainable code while using GitHub Copilot responsibly.

## Coding Guidelines

- Write clean, readable, and modular code.
- Keep functions focused on a single responsibility.
- Reuse existing functions instead of duplicating logic.
- Follow consistent naming conventions.
- Add comments for complex logic where necessary.

## Error Handling

- Use try-catch blocks for all asynchronous JavaScript operations.
- Validate all user inputs before processing.
- Display user-friendly error messages.
- Log unexpected errors using console.error() for debugging.

## User Interface

- Keep the interface responsive on desktop and mobile devices.
- Use plain CSS without external frameworks.
- Alternate the background colors of each 3x3 Sudoku box.
- Support Light Mode and Dark Mode.
- Save the selected theme using localStorage.

## Accessibility

- Use semantic HTML elements.
- Add labels and ARIA attributes where appropriate.
- Ensure keyboard navigation works correctly.
- Keep sufficient color contrast for readability.

## Sudoku Features

- Generate puzzles with exactly one unique solution.
- Support Easy, Medium, and Hard difficulty levels.
- Lock all prefilled cells.
- Highlight invalid entries immediately when the user types.
- Display a congratulatory message after solving the puzzle.
- Provide a Hint feature that fills one correct empty cell.
- Include a Check Solution feature.
- Display a timer during gameplay.

## Leaderboard

- Store the top 10 scores using localStorage.
- Save player name, completion time, difficulty level, and hints used.
- Sort scores by completion time.

## Testing

- Ensure the application runs using:

python app.py

- Ensure all tests pass using:

python -m pytest

- Avoid console errors and keep the application production-ready.