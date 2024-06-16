import pygame
import time
import random
from pygame import mixer
import asyncio

mixer.init()
pygame.font.init()

# Load music tracks
MENU_MUSIC = "menu_music.mp3"
LEVEL_1_MUSIC = "level1_music.mp3"
LEVEL_2_MUSIC = "level2_music.mp3"
LEVEL_3_MUSIC = "level3_music.mp3"
LEVEL_4_MUSIC = "level4_music.mp3"

# Load and play main menu music
async def play_menu_music():
    mixer.music.load(MENU_MUSIC)
    mixer.music.set_volume(0.7)
    mixer.music.play(-1)  # Loop the music

# Load and play game music
async def play_game_music(music_file):
    mixer.music.load(music_file)
    mixer.music.set_volume(0.7)
    mixer.music.play(-1)  # Loop the music

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge")
BG = pygame.transform.scale(pygame.image.load("blue background.jpg"), (WIDTH, HEIGHT))
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 60
PLAYER_IMAGE = pygame.image.load("player.png").convert_alpha()
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
PLAYER_VEL = 10
STAR_WIDTH = 50
STAR_HEIGHT = 50
STAR_IMAGE = pygame.image.load("block.webp").convert_alpha()
STAR_IMAGE = pygame.transform.scale(STAR_IMAGE, (STAR_WIDTH, STAR_HEIGHT))
STAR_VEL = 3

FONT = pygame.font.SysFont("pusab", 50)  # comicsans

async def draw(player_rect, elapsed_time, stars, attempts):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (60, 60))

    attempts_text = FONT.render(f"Attempts: {attempts}", 1, "white")
    WIN.blit(attempts_text, (60, 120))

    WIN.blit(PLAYER_IMAGE, (player_rect.x, player_rect.y))

    for star in stars:
        WIN.blit(STAR_IMAGE, (star.x, star.y))

    pygame.display.update()

async def game_loop(attempts, level_time, music_file):
    await play_game_music(music_file)  # Start game music

    player_rect = pygame.Rect(400, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 2000
    star_count = 0

    stars = []
    hit = False

    run = True
    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        if star_count > star_add_increment:
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)

            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, attempts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -1, attempts

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.x - PLAYER_VEL >= 0:
            player_rect.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player_rect.x + PLAYER_VEL + player_rect.width <= WIDTH:
            player_rect.x += PLAYER_VEL

        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height >= player_rect.y and star.colliderect(player_rect):
                stars.remove(star)
                hit = True
                break

        if hit:
            mixer.music.stop()
            lost_text = FONT.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, HEIGHT / 2 - lost_text.get_height() / 2))
            pygame.display.update()
            await asyncio.sleep(2)  # Shorter delay before restart
            return True, attempts + 1

        await draw(player_rect, elapsed_time, stars, attempts)

        if elapsed_time >= level_time:  # Check if the player has survived for the level time
            mixer.music.stop()
            end_text = FONT.render("You Win!", 1, "white")
            WIN.blit(end_text, (WIDTH / 2 - end_text.get_width() / 2, HEIGHT / 2 - end_text.get_height() / 2))
            pygame.display.update()
            await asyncio.sleep(5)  # Display the end screen for 5 seconds
            return 2, attempts

    return False, attempts

async def main_menu():
    await play_menu_music()  # Start main menu music

    run = True
    while run:
        WIN.fill((0, 0, 0))  # Fill the screen with black

        title_text = FONT.render("Space Dodge", 1, "white")
        WIN.blit(title_text, (WIDTH / 2 - title_text.get_width() / 2, HEIGHT / 4))

        level_1_text = FONT.render("1. Level 1 (10 seconds)", 1, "white")
        WIN.blit(level_1_text, (WIDTH / 2 - level_1_text.get_width() / 2, HEIGHT / 2))

        level_2_text = FONT.render("2. Level 2 (20 seconds)", 1, "white")
        WIN.blit(level_2_text, (WIDTH / 2 - level_2_text.get_width() / 2, HEIGHT / 2 + 60))

        level_3_text = FONT.render("3. Level 3 (30 seconds)", 1, "white")
        WIN.blit(level_3_text, (WIDTH / 2 - level_3_text.get_width() / 2, HEIGHT / 2 + 120))
        
        level_4_text = FONT.render("4. Level 4 (40 seconds)", 1, "white")
        WIN.blit(level_4_text, (WIDTH / 2 - level_4_text.get_width() / 2, HEIGHT / 2 + 180))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 10, LEVEL_1_MUSIC
                if event.key == pygame.K_2:
                    return 20, LEVEL_2_MUSIC
                if event.key == pygame.K_3:
                    return 30, LEVEL_3_MUSIC
                if event.key == pygame.K_4:
                    return 40, LEVEL_4_MUSIC

async def main():
    level_time, music_file = await main_menu()
    if level_time is None:
        return

    attempts = 0
    running = True
    while running:
        game_over, attempts = await game_loop(attempts, level_time, music_file)
        if game_over == -1 or game_over == 2:  # Added condition to check if the player won
            level_time, music_file = await main_menu()
            if level_time is None:
                return
        elif game_over:
            await play_game_music(music_file)  # Restart the game music when the game restarts
        if not game_over:
            running = False

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
