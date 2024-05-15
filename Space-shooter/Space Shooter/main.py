import pygame
import os
import time
import random
from pygame import mixer
import sys
import socket
import threading
import json
from threading import Lock
from button import Button
from objects import Background

# initialize pygame, mixer and font 
pygame.init()
pygame.font.init()
mixer.init()

WIDTH, HEIGHT = 700, 670
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue.png"))
BLOOD_IMAGE = pygame.image.load(os.path.join("assets", "blood.png"))
ENERGY_IMAGE = pygame.image.load(os.path.join("assets", "energy.png"))

# load sound filed
shoot_sound = mixer.Sound(os.path.join("assets", "bullet_sound.wav"))
shoot_sound_enemy = mixer.Sound(os.path.join("assets", "bullet_sound_enemy.wav"))
get_score = mixer.Sound(os.path.join("assets", "get_score.wav"))
gameOver_sound = mixer.Sound(os.path.join("assets", "gameOver_sound.wav"))
gameWin_sound = mixer.Sound(os.path.join("assets", "get_score.wav"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "bullet.png"))
DOUBLE_LASER = pygame.image.load(os.path.join("assets", "double_bullet.png"))
SUPER_LASER = pygame.image.load(os.path.join("assets", "super_bullet.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT))

# Background menu
BG_MENU = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_menu.jpg")), (WIDTH, HEIGHT))

# thêm biến background
bg = Background(WIN) 

POWER_UP_DURATION = 20 # Thời gian tồn tại của power-up (5 giây)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            shoot_sound.play()
            laser = Laser(self.x + 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class BloodIcon:
    def __init__(self, x, y, speed = 1):
        self.x = x 
        self.y = y 
        self.img = BLOOD_IMAGE
        self.mask = pygame.mask.from_surface(self.img)
        self.speed = speed

    def move(self):
        self.y += self.speed

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)

class Energy:
    def __init__(self, x, y, power_level, speed=1):
        self.x = x
        self.y = y
        self.vel = speed
        self.img = ENERGY_IMAGE
        self.power_level = power_level
        self.mask = pygame.mask.from_surface(self.img)
        self.start_time = time.time()

    def move(self):
        self.y += self.vel

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0
        self.max_score = self.score + 30
        self.power_level = 1

    def spawn_blood_icon(self, blood_icons):
        if random.randint(1, 200) == 1:
            blood_icon = BloodIcon(random.randint(50, WIDTH - 50), -100)
            blood_icons.append(blood_icon)

    def spawn_energy_icon(self, energy_icons):
        while self.score == self.max_score:
            energy_icon = Energy(random.randint(50, WIDTH - 50), -100)
            energy_icons.append(energy_icon)
            self.max_score += 30
            
    def power_up(self, power_level):
        if power_level == 1:
            self.power_level = 1
        elif power_level == 2:
            self.power_level = 2
        elif power_level == 3:
            self.power_level = 3
        else:
            self.power_level = 1  # Nếu giá trị không hợp lệ thì mặc định là cấp độ 1

    def move_lasers(self, vel, objs, blood_icons, energy_icons):
        self.spawn_blood_icon(blood_icons)
        self.spawn_energy_icon(energy_icons)
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if self.power_level == 1:
                            self.laser_img = YELLOW_LASER
                            self.power_level = 1
                            for player_laser in self.lasers: 
                                if collide(obj, player_laser):
                                    obj.health -= 20
                        elif self.power_level == 2:
                            self.laser_img = DOUBLE_LASER
                            self.power_level = 2
                            for player_laser in self.lasers: 
                                if collide(obj, player_laser):
                                    obj.health -= 30
                        elif self.power_level >= 3:
                            self.laser_img = SUPER_LASER
                            self.power_level = 3
                            for player_laser in self.lasers: 
                                if collide(obj, player_laser):
                                    obj.health -= 50
                        else:
                            self.power_level = 1
                        if obj.health <= 0:
                            objs.remove(obj)
                            self.score += 10
                            get_score.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 7))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 7))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    """
        Initializes an enemy ship object.

        Args:
        x (int): The x-coordinate of the enemy ship.
        y (int): The y-coordinate of the enemy ship.
        color (str): The color of the enemy ship.
        health (int): The health of the enemy ship.
    """
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.cool_down_counter = 0

    # Moves the enemy ship down by the specified velocity.
    def move(self, vel):
        self.y += vel

    def kill(self):
        self.visible = False
        self.health = 0

    def shoot(self, player):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 20, self.y + 20, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            for player_laser in player.lasers:
                if collide(self, player_laser):
                    self.health -= 20
                    player.lasers.remove(player_laser)
                    if self.health <= 0:
                        self.kill()
                    else:
                        self.healthbar(WIN)

    def off_screen(self, height):
        return self.y > height or self.y < 0

    # Draws a health bar on the screen to represent the enemy's health.
    def healthbar(self, screen):
        bar_length = self.ship_img.get_width()
        bar_height = 7
        health_bar = (self.health / 100) * bar_length
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, bar_length, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, health_bar, bar_height))

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#Chat
class ChatButton:
    def __init__(self, image, pos):
        self.image = image
        self.pos = pos

    def draw(self, win):
        win.blit(self.image, self.pos)

    def is_clicked(self, pos):
        x, y = pos
        button_rect = self.image.get_rect(topleft=self.pos)
        return button_rect.collidepoint(x, y)

# Tạo một đối tượng lock
chat_log_lock = threading.Lock()

# Trong hàm send_message:
def send_message(client_socket, input_text):
    try:
        client_socket.sendall(input_text.encode('utf-8'))
        # Thêm tin nhắn vào chat_log
        with chat_log_lock:
            chat_log.append("You: "+input_text)
    except Exception as e:
        print("Error sending message:", e)

# Trong hàm receive_messages:
def receive_messages(client_socket, chat_log):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                with chat_log_lock:
                    # Thêm tin nhắn từ client vào chat log
                    chat_log.append(message)
            else:
                break
    except Exception as e:
        print("Error receiving message:", e)
    finally:
        client_socket.close()

chat_log = []  # Danh sách để lưu tin nhắn trong cuộc trò chuyện

def chat_box():
    run_chat = True
    chat_font = pygame.font.SysFont("Arial", 14)
    input_font = pygame.font.SysFont("Arial", 14)

    current_client_address = client_socket.getpeername()
    
    input_text = ""  # Biến để lưu nội dung của ô nhập liệu

    # Kích thước của chat menu
    chat_menu_width = WIDTH // 2
    chat_menu_height = HEIGHT // 2

    # Vị trí của chat menu
    chat_menu_x = 10
    chat_menu_y = 150

    # Vị trí của nút tắt
    close_button_x = chat_menu_x + chat_menu_width - 30
    close_button_y = chat_menu_y + 10

    while run_chat:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Thoát khỏi trò chơi khi cửa sổ bị đóng
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Xử lý khi người dùng nhấn Enter
                    if input_text:  # Đảm bảo rằng ô nhập liệu không trống
                        send_message(client_socket, input_text)  # Gửi tin nhắn đến máy chủ
                        input_text = ""  # Đặt lại nội dung của ô nhập liệu
                elif event.key == pygame.K_BACKSPACE:  # Xử lý khi người dùng nhấn phím Backspace
                    input_text = input_text[:-1]  # Xóa ký tự cuối cùng trong ô nhập liệu
                else:
                    # Thêm ký tự vào ô nhập liệu
                    input_text += event.unicode if event.unicode.isprintable() else ""

            elif event.type == pygame.MOUSEBUTTONDOWN:  # Xử lý khi người dùng nhấn chuột
                mouse_pos = pygame.mouse.get_pos()
                # Kiểm tra nếu người dùng nhấn vào nút tắt
                if close_button_x <= mouse_pos[0] <= close_button_x + 20 and \
                   close_button_y <= mouse_pos[1] <= close_button_y + 20:
                    run_chat = False  # Đóng cửa sổ chat menu

        # Vẽ nền trong suốt cho chat menu
        chat_menu_surface = pygame.Surface((chat_menu_width, chat_menu_height), pygame.SRCALPHA)
        pygame.draw.rect(chat_menu_surface, (0, 0, 0, 100), (0, 0, chat_menu_width, chat_menu_height), border_radius=10)
        WIN.blit(chat_menu_surface, (chat_menu_x, chat_menu_y))

        # Vẽ giao diện chat
        y_offset = chat_menu_y + 10
        for message in chat_log:
            # Kiểm tra xem tin nhắn có đến từ client khác không
            if message.startswith("You:") and message[5:] != current_client_address:
                message = "You: " + message[5:]
            else:
                message = "Other: " + message
            
            text_surface = chat_font.render(message, True, (255, 255, 255))  # Render tin nhắn
            WIN.blit(text_surface, (chat_menu_x + 10, y_offset))  # Vẽ tin nhắn lên màn hình
            y_offset += text_surface.get_height() + 5  # Tăng y_offset để vẽ tin nhắn tiếp theo

        # Vẽ ô nhập liệu
        pygame.draw.rect(WIN, (255, 255, 255), (chat_menu_x + 5, chat_menu_y + chat_menu_height - 35, chat_menu_width - 10, 30), 2)  # Vẽ khung ô nhập liệu
        input_surface = input_font.render(input_text, True, (255, 255, 255))  # Render nội dung ô nhập liệu
        WIN.blit(input_surface, (chat_menu_x + 10, chat_menu_y + chat_menu_height - 30))  # Vẽ nội dung ô nhập liệu lên màn hình

        # Vẽ nút tắt
        pygame.draw.rect(WIN, (255, 0, 0), (close_button_x, close_button_y, 20, 20))
        close_text = input_font.render("X", True, (255, 255, 255))
        WIN.blit(close_text, (close_button_x + 4, close_button_y))

        pygame.display.update() 

def main():
    global run
    run = True
    level = 0
    enemies = []
    explosions = []
    player_vel = 6
    laser_vel = 7
    player = Player(300, 550)
    dif = 1 # health bar of enemise reduce rely on this variable
    blood_icons = []
    energy_icons = []
    bg_running = 0
    
    main_font = pygame.font.SysFont("Arial", 30)
    lost_font = pygame.font.SysFont("Arial", 40)
    win_font = pygame.font.SysFont("Arial", 40)

    # get the level from user
    FPS = 50
    wave_length = 5
    enemy_vel = 1
    lives = 6
    dif = 4
    bg_running = 0.50
    clock = pygame.time.Clock()

    global lost, win, status_sent

    lost = False

    win = False

    status_sent = False


    # Vẽ nút chat chỉ khi người dùng đã nhấn "PLAY"
    CHAT_BUTTON_POS = (10, 150)  # Vị trí của nút chat
    CHAT_BUTTON_IMAGE = pygame.image.load(os.path.join("assets", "Chat_Rect.png"))  # Load hình ảnh của nút chat
    chat_button = ChatButton(CHAT_BUTTON_IMAGE, CHAT_BUTTON_POS)

    # Khởi tạo thread để nhận tin nhắn
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, chat_log))
    receive_thread.daemon = True  # Đặt thread nhận tin nhắn thành daemon để nó tự đóng khi chương trình chính kết thúc
    receive_thread.start()

    def redraw_window():
        WIN.blit(BG, (0,0))
        bg.update(bg_running) # running background
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))

        chat_button.draw(WIN)

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for laser in player.lasers:
            laser.draw(WIN)

        for blood_icon in blood_icons:
            blood_icon.draw(WIN)

        for energy_icon in energy_icons:
            energy_icon.draw(WIN)

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)
            enemy.healthbar(WIN) # draw health bar for each enemy

        if lost:
            lost_label = lost_font.render("Game Over!", 1, (255,255,255))
            if lost_label:
                gameOver_sound.play()
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        if win:
            win_label = win_font.render("You Win!", 1, (255,255,255))
            if win_label:
                gameWin_sound.play()
            WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2, 350))

        pygame.display.update()

    def delay_run_false():
        global run
        run = False

    def send_game_status(status):
        message = json.dumps({'status': status})
        client_socket.sendall(message.encode('utf-8'))

    def receive_game_status():
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    status = json.loads(data).get('status')
                    if status == 'lost':
                        global win
                        win = True
                    elif status == 'win':
                        global lost
                        lost = True
            except Exception as e:
                print(f"Error receiving game status: {e}")
                break

    status_thread = threading.Thread(target=receive_game_status)
    status_thread.daemon = True
    status_thread.start()
    
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True

        if player.score == 500:
            win = True

        if (win or lost) and not status_sent:
            if win:
                send_game_status('win')  # Gửi thông tin chiến thắng tới server
            if lost:
                send_game_status('lost')  # Gửi thông tin thua cuộc tới server

            threading.Timer(2, delay_run_false).start()  # Trì hoãn việc đặt run thành False
            threading.Timer(2, reset).start()  # Trì hoãn việc reset
            status_sent = True  # Đặt cờ để ngăn chặn việc gửi nhiều lần


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        # spawn new BloodIcon objects randomly at the top of the screen
        if random.randint(0, 1300) < 1:
            blood_icon = BloodIcon(random.randint(50, WIDTH-50), 0)
            blood_icons.append(blood_icon)

        # move and draw the BloodIcon objects
        for blood_icon in blood_icons:
            blood_icon.move()
            blood_icon.draw(WIN)
            if blood_icon.collision(player):
                player.health += 20
                if player.health > player.max_health:
                    player.health = player.max_health
                blood_icons.remove(blood_icon)

        # spawn new EnergyIcon objects randomly at the top of the screen
        while player.score == player.max_score:
            energy_icon = Energy(random.randint(50, WIDTH - 50), 1, -100)
            energy_icons.append(energy_icon)
            player.max_score += 30

        # move and draw the EnergyIcon objects
        for energy_icon in energy_icons:
            energy_icon.move()
            energy_icon.draw(WIN)
            if energy_icon.collision(player):
                player.power_level += 1
                # Kiểm tra thời gian tồn tại của power-up, nếu hết hiệu lực thì hủy nó
                if time.time() - energy_icon.start_time >= POWER_UP_DURATION:
                    player.power_level = 1
                energy_icons.remove(energy_icon)
            elif time.time() - energy_icon.start_time >= 5:
                energy_icons.remove(energy_icon)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    client_socket.close()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if chat_button.is_clicked(mouse_pos):
                    chat_box()  # Hiển thị giao diện chat khi nút chat được nhấn
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    chat_box()  # Hiển thị giao diện chat khi nhấn phím "M"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*FPS) == 1:
                enemy.shoot(player)

            # collisions of enemy and player
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies, blood_icons, dif)

def get_font(size):
    return pygame.font.SysFont("comicsans",size)

# mode play in main menu
connected = threading.Event()
ready_to_start = threading.Event()
client_socket = None

def reset():
    reset_game_state()
    if client_socket is not None:
        try:
            client_socket.close()
            print("Socket closed successfully.")
        except Exception as e:
            print(f"Error closing socket: {e}")

def connect_to_server():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(socket.gethostname())
        port = 5500
        client_socket.connect((host, port))
        connected.set()
        print("Connected to server successfully.")
    except Exception as e:
        print(f"Lỗi khi kết nối tới máy chủ: {e}")
        client_socket = None

def ready_from_server():
    global client_socket
    while True:
        if ready_to_start.is_set():
            break
        try:
            if client_socket is not None:
                if connected.is_set():
                    # Nhận thông điệp từ máy chủ
                    message = client_socket.recv(1024).decode()
                    if message == "ready_to_start":
                        ready_to_start.set()
                else:
                    # Dừng một thời gian ngắn để cho socket có cơ hội kết nối
                    time.sleep(0.1)
        except ConnectionResetError as e:
            # print(f"Kết nối đã bị đóng bởi máy chủ: {e}")
            break
        except Exception as e:
            # print(f"Lỗi khi nhận thông điệp từ máy chủ: {e}")
            break

def reset_game_state():
    global connected, ready_to_start
    connected.clear()
    ready_to_start.clear()  # Đặt lại trạng thái "ready_to_start"

def play():
    global connected, ready_to_start, client_thread
    
    # Reset game state
    reset_game_state()

    waiting_text = "Waiting for other players..."
    start_time = time.time()
    display_start_message = False
    connect = False

    # Create Pygame screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if connect:
                        try:
                            client_socket.close()
                        except Exception as e:
                            print(f"Error closing socket: {e}")
                    running = False
                elif event.key == pygame.K_p:
                    if not connect:
                        connect_to_server()
                        connected.wait(1)  # Wait until connected, with a timeout of 5 seconds
                        if not connected.is_set():
                            screen.fill((0, 0, 0))
                            font = pygame.font.Font(None, 36)
                            text = font.render("Failed to connect to the server.", True, (255, 255, 255))
                            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                            screen.blit(text, text_rect)
                            pygame.display.flip()

                            # Wait for 2 seconds to show the message before returning
                            wait_time = 2000  # 2000 milliseconds = 2 seconds
                            start_wait = pygame.time.get_ticks()
                            while pygame.time.get_ticks() - start_wait < wait_time:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    elif event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_ESCAPE:
                                            return
                            return  # Return if unable to connect to the server
                        client_thread = threading.Thread(target=ready_from_server)
                        client_thread.start()
                    connect = True

        if not connect:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Press 'P' to play", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)
        else:
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render(waiting_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

            if ready_to_start.is_set() and not display_start_message:
                display_start_message = True
                waiting_text = "Both players are ready, let's start the game..."

        pygame.display.flip()

        if display_start_message:
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                running = False
                main()

    # Reset game state if the loop breaks
    reset_game_state()


# Khởi tạo luồng cho client
client_thread = threading.Thread(target=ready_from_server)
client_thread.start()

#mode help in main menu
def help():
    while True:
        HELP_MOUSE_POS=pygame.mouse.get_pos()
        WIN.fill("black")
        str='''Players must destroy all enemies on their flight path to pass different levels. Players use a keyboard with keys W, A, D, S to move the plane, use SPACE to shoot bullets. Players can also use helpful items such as bombs, missiles, or energy to help them destroy opponents faster'''
        blit_text(WIN,str,(20,100),get_font(25))
        # WIN.blit(HELP_TEXT,HELP_RECT)

        HELP_BACK = Button(image=None, pos=(340, 500), text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")

        HELP_BACK.changeColor(HELP_MOUSE_POS)
        HELP_BACK.update(WIN)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if HELP_BACK.checkForInput(HELP_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    title_font = pygame.font.SysFont("Arial", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))

        MENU_MOUSE_POS=pygame.mouse.get_pos()
        #game header text
        MENU_TEXT=get_font(45).render("SPACE SHOOTER",True,"#b68f40")
        MENU_RECT=MENU_TEXT.get_rect(center=(340,50))

        #buttons in main menu
        PLAY_BUTTON = Button(image=pygame.image.load(os.path.join("assets", "Play_Rect.png")), pos=(340, 250), 
                            text_input="PLAY", font=get_font(45), base_color="#d7fcd4", hovering_color="Green")
        HELP_BUTTON = Button(image=pygame.image.load(os.path.join("assets", "Help_Rect.png")), pos=(340, 400), 
                            text_input="HELP", font=get_font(45), base_color="#d7fcd4", hovering_color="Green")
        QUIT_BUTTON = Button(image=pygame.image.load(os.path.join("assets", "Quit_Rect.png")), pos=(340, 550), 
                            text_input="QUIT", font=get_font(45), base_color="#d7fcd4", hovering_color="Green")
        
        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, HELP_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # pygame.quit()
                # sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if HELP_BUTTON.checkForInput(MENU_MOUSE_POS):
                    help()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

#def add text in multiple lines
def blit_text(surface, text, pos, font, color=pygame.Color('white')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row

main_menu()