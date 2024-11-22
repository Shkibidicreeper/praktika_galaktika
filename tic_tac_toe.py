import pygame
import sys
import mysql.connector
import sqlalchemy
import logging
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

pygame.init()

# Размеры окна
WIDTH, HEIGHT = 500, 500
CELL_SIZE = WIDTH // 3

# Настройки цвета
GREY = (90, 90, 115)
RED = (255, 50, 60) 
BLUE = (0, 191, 255)
LINE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

# Экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Крестики-нолики')

# Инициализация игрового поля
board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
player1 = ""
player2 = ""

font = pygame.font.Font(None, 36)
game_over = False
game_message = ""

Base = declarative_base()

# Определяем модели
class Game(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    playerX_score = Column(Integer)  
    playerO_score = Column(Integer)  

# Создаем подключение и сессию
engine = create_engine('mysql+pymysql://is61-8:cxitmrxu@192.168.3.111:3306/tic_tac_toe')
Session = sessionmaker(bind=engine)

def save_game(session, name, playerX_score, playerO_score):
    new_game = Game(name=name, playerX_score=playerX_score, playerO_score=playerO_score)
    try:
        session.add(new_game)
        session.commit()
        print("Game saved successfully")
    except Exception as e:
        session.rollback()
        print(f"Error saving game: {e}")

def check_winner():
    for row in board:
        if row[0] == row[1] == row[2] != "":
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    return None

def reset_game():
    global board, current_player, game_over, game_message
    game_over = False
    game_message = ""
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"

def display_input_screen():
    global player1, player2
    input_active = True
    text_input = ""
    player_turn = 1

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_turn == 1:
                        player1 = text_input
                        text_input = ""
                        player_turn = 2
                    else:
                        player2 = text_input
                        input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                elif len(text_input) < 20:
                    text_input += event.unicode

        # Отображение экрана ввода
        screen.fill(GREY)
        input_text = font.render(f'Player {player_turn} name: {text_input}', True, TEXT_COLOR)
        screen.blit(input_text, (10, 10))
        pygame.display.flip()

def draw_board():
    screen.fill(GREY)
    for i in range(1, 4):
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 5)
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 5)

    for row in range(3):
        for col in range(3):
            if board[row][col] == "X":
                pygame.draw.line(screen, RED, (col * CELL_SIZE + 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + CELL_SIZE - 30), 10)
                pygame.draw.line(screen, RED, (col * CELL_SIZE + CELL_SIZE - 30, row * CELL_SIZE + 30),
                                 (col * CELL_SIZE + 30, row * CELL_SIZE + CELL_SIZE - 30), 10)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, BLUE, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 60, 10)

    player_text = font.render(f'Player 1: {player1} (X)    Player 2: {player2} (O)', True, TEXT_COLOR)
    screen.blit(player_text, (10, HEIGHT - 40))

    if game_over:
        message_text = font.render(game_message, True, TEXT_COLOR)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2 - 20))

def main():
    global current_player, game_over

    display_input_screen()
    session = Session()  # Создаем сессию здесь

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                session.close()  # Закрываем сессию перед выходом
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE

                if board[row][col] == "":
                    board[row][col] = current_player
                    winner = check_winner()

                    if winner:
                        game_message = f'Player {winner} wins!'
                        game_over = True
                        playerX_score = 1 if winner == "X" else 0
                        playerO_score = 1 if winner == "O" else 0
                        save_game(session, player1 + " vs " + player2, playerX_score, playerO_score)  # Передаем сессию
                    elif all(cell != "" for row in board for cell in row):
                        game_message = "It's a draw!"
                        game_over = True
                        save_game(session, player1 + " vs " + player2, 0, 0)  # Сохраняем ничью

                    current_player = "O" if current_player == "X" else "X"

            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()  # Сброс игры после нажатия пробела

        draw_board()
        pygame.display.flip()

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    main()