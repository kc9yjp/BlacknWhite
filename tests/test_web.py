"""Browser UI tests using Playwright.

All tests start a fresh browser page against the live Flask server.
The board initialises with WHITE's turn, so tests that need to interact
immediately use 'Play as White'.  Tests that check BLACK's game-info label
click 'Play as Black' and only wait for the controls to appear (not for the
AI to move).
"""
import pytest


pytestmark = pytest.mark.playwright


# ---------------------------------------------------------------------------
# Page load
# ---------------------------------------------------------------------------

def test_page_title(page, live_server_url):
    page.goto(live_server_url)
    assert page.title() == 'BlacknWhite'


def test_start_area_visible_on_load(page, live_server_url):
    page.goto(live_server_url)
    assert page.locator('#start-area').is_visible()


def test_game_controls_hidden_on_load(page, live_server_url):
    page.goto(live_server_url)
    assert page.locator('#game-controls').is_hidden()


def test_board_has_64_squares(page, live_server_url):
    page.goto(live_server_url)
    assert page.locator('.square').count() == 64


def test_strategy_dropdown_has_three_options(page, live_server_url):
    page.goto(live_server_url)
    assert page.locator('#strategySelect option').count() == 3


def test_initial_pieces_rendered(page, live_server_url):
    page.goto(live_server_url)
    # Starting position: 2 WHITE and 2 BLACK pieces
    assert page.locator('.piece.white').count() == 2
    assert page.locator('.piece.black').count() == 2


# ---------------------------------------------------------------------------
# Starting a game
# ---------------------------------------------------------------------------

def test_play_as_white_shows_game_controls(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert page.locator('#start-area').is_hidden()


def test_play_as_white_game_info_shows_white(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert 'White' in page.locator('#game-info').text_content()


def test_play_as_black_game_info_shows_black(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startBlackBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert 'Black' in page.locator('#game-info').text_content()


def test_game_info_shows_opponent_strategy(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#strategySelect').select_option('smart')
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert 'Smart' in page.locator('#game-info').text_content()


def test_status_shows_score_after_start(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#status').wait_for(state='visible')
    text = page.locator('#status').text_content()
    assert 'Black' in text and 'White' in text


# ---------------------------------------------------------------------------
# Valid move hints
# ---------------------------------------------------------------------------

def test_valid_move_dots_appear_on_player_turn(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.wait_for_selector('.square.VALID')
    assert page.locator('.square.VALID').count() == 4


def test_no_valid_move_dots_for_ai_turn(page, live_server_url):
    page.goto(live_server_url)
    # Start as BLACK: AI (WHITE) goes first, so no VALID hints for the player yet
    page.locator('#startBlackBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    # VALID dots should not appear immediately (it is the AI's turn)
    assert page.locator('.square.VALID').count() == 0


# ---------------------------------------------------------------------------
# Making a move
# ---------------------------------------------------------------------------

def test_click_valid_square_places_piece(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.wait_for_selector('.square.VALID')
    first_valid = page.locator('.square.VALID').first
    row = first_valid.get_attribute('data-row')
    col = first_valid.get_attribute('data-col')
    first_valid.click()
    page.wait_for_selector(f'.square[data-row="{row}"][data-col="{col}"] .piece.white')


def test_move_reduces_valid_squares(page, live_server_url):
    """After WHITE moves, it is BLACK's (AI's) turn — no VALID hints."""
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.wait_for_selector('.square.VALID')
    page.locator('.square.VALID').first.click()
    # immediately after clicking, valid squares should disappear (AI's turn)
    page.wait_for_selector('.square.VALID', state='hidden')


# ---------------------------------------------------------------------------
# Game-over panel
# ---------------------------------------------------------------------------

def test_game_over_panel_initially_hidden(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert page.locator('#game-over-area').is_hidden()


def test_play_controls_visible_during_game(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert page.locator('#play-controls').is_visible()


# ---------------------------------------------------------------------------
# New Game / navigation
# ---------------------------------------------------------------------------

def test_new_game_button_returns_to_start_screen(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    page.locator('#resetBtn').click()
    page.locator('#start-area').wait_for(state='visible')
    assert page.locator('#game-controls').is_hidden()


def test_pass_button_visible_during_game(page, live_server_url):
    page.goto(live_server_url)
    page.locator('#startWhiteBtn').click()
    page.locator('#game-controls').wait_for(state='visible')
    assert page.locator('#passBtn').is_visible()
