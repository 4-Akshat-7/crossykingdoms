import pygame
from gameObject import GameObject
from player import Player
from enemy import Enemy
import mysql.connector as mc
import datetime
class Game:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.white_colour = (255, 255, 255)

        self.game_window = pygame.display.set_mode((self.width,self.height))


        self.clock = pygame.time.Clock()

        self.background = GameObject(0, 0, self.width, self.height, 'assets/background.png')


        self.treasure = GameObject(375, 50, 50, 50, 'assets/treasure.png')
        

        self.level = 1.0
        
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 128)
        
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.text = self.font.render('Level {}'.format(self.level), True, self.green, self.blue)
        self.textRect = self.text.get_rect()
        
        
        self.text2 = self.font.render('Press L for leaderboard', True, self.green, self.blue)
        self.text2Rect=self.text2.get_rect()
        
        self.text2Rect.topright=(550,0)
        self.conn=mc.connect(host='localhost',user='root',password='root',database='game')
        self.wcur=self.conn.cursor()
        db_creation_query="create database if not exists game"
        self.conn.commit()
        self.wcur.execute(db_creation_query)
        table_creation_query ="create table if not exists gamedata(timestamp varchar(50), level int)"
        self.wcur.execute(table_creation_query)
        self.conn.commit()
        self.wcur.close()
        self.reset_map()
        
    def reset_map(self):

        self.player = Player(375, 700, 50, 50, 'assets/player.png', 10)

        speed = 5 + (self.level * 3 )

        if self.level >= 4.0:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/enemy.png', speed),
                Enemy(750, 400, 50, 50, 'assets/enemy.png', speed),
                Enemy(0, 200, 50, 50, 'assets/enemy.png', speed),
            ]
        elif self.level >= 2.0:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/enemy.png', speed),
                Enemy(750, 400, 50, 50, 'assets/enemy.png', speed),
            ]
        else:
            self.enemies = [
                Enemy(0, 600, 50, 50, 'assets/enemy.png', speed),
            ]


    def draw_objects(self):
        self.game_window.fill(self.white_colour)

        self.game_window.blit(self.background.image, (self.background.x, self.background.y))
        self.game_window.blit(self.treasure.image, (self.treasure.x, self.treasure.y))
        self.game_window.blit(self.player.image, (self.player.x, self.player.y))
        
        self.game_window.blit(self.text, self.textRect)
        self.game_window.blit(self.text2, self.text2Rect)
        for enemy in self.enemies:
            self.game_window.blit(enemy.image, (enemy.x, enemy.y))

        pygame.display.update()


    def move_objects(self, player_direction):
        self.player.move(player_direction, self.height)
        for enemy in self.enemies:
            enemy.move(self.width)


    def check_if_collided(self):
        for enemy in self.enemies:
            if self.detect_collision(self.player, enemy):
                self.conn=mc.connect(host='localhost',user='root',password='root',database='game')
                self.wcur=self.conn.cursor()
                self.current_datetime = str(datetime.datetime.now().strftime('%m-%d %H:%M'))
                insert_query ="insert into gamedata values(%s,%s)"
                values=self.current_datetime, int(self.level)
                self.wcur.execute(insert_query,values)
                self.conn.commit()
                self.wcur.close()
                self.conn.close()
                self.level = 1.0
                
                
                self.text = self.font.render('Level {}'.format(self.level), True, self.green, self.blue)
                self.text2 = self.font.render('Press L for leaderboard', True, self.green, self.blue)
                return True
        if self.detect_collision(self.player, self.treasure):
            self.level += 1
            
            self.text = self.font.render('Level {}'.format(self.level), True, self.green, self.blue)
            self.text2 = self.font.render('Press L for leaderboard', True, self.green, self.blue)
            return True
        
        return False


    def detect_collision(self, object_1, object_2):
        if object_1.y < (object_2.y + object_2.height) and (object_1.y + object_1.height) > object_2.y: 
            if object_1.x < (object_2.x + object_2.width) and (object_1.x + object_1.width) > object_2.x:
                return True
        return False

    def show_leaderboard(self):
        # Connect to the MySQL database
        conn = mc.connect(host='localhost', user='root', password='root', database='game')
        cursor = conn.cursor()

        try:
           
            select_query = "SELECT timestamp, level FROM gamedata ORDER BY level DESC LIMIT 10"
            cursor.execute(select_query)
            leaderboard_data = cursor.fetchall()

            leaderboard_text = "Leaderboard\n"
            for entry in leaderboard_data:
                leaderboard_text += f"{entry[0]}: {entry[1]}\n"

            leaderboard_lines = leaderboard_text.splitlines()

            leaderboard_surface = pygame.Surface((self.width, self.height))
            leaderboard_surface.fill((0, 0, 0))

            y_offset = (self.height - len(leaderboard_lines) * self.font.get_height()) // 2
            for line in leaderboard_lines:
                line_surface = self.font.render(line, True, self.green, (0, 0, 0))
                x_offset = (self.width - line_surface.get_width()) // 2
                leaderboard_surface.blit(line_surface, (x_offset, y_offset))
                y_offset += self.font.get_height() + 10 

            self.game_window.blit(leaderboard_surface, (0, 0))
            pygame.display.flip()

            waiting_for_key = True
            while waiting_for_key:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        waiting_for_key = False

        except mc.Error as e:
            print(f"Error: {e}")

        finally:
            cursor.close()
            conn.close()


    def run_game_loop(self):
        player_direction = 0

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player_direction = -1
                    elif event.key == pygame.K_DOWN:
                        player_direction = 1
                    elif event.key == pygame.K_l:  
                        self.show_leaderboard()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        player_direction = 0
                
            self.move_objects(player_direction)

            self.draw_objects()

            if self.check_if_collided():
                self.reset_map()

            self.clock.tick(60)
