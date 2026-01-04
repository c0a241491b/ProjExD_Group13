import os
import pygame
import sys
import random
import MapField


os.chdir(os.path.dirname(os.path.abspath(__file__)))


SCREEN_WIDTH = 800  # 設定
SCREEN_HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)  # 色定義
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
GRAY = (169, 169, 169)
RED = (255, 0, 0)  # こうかとん
BLUE = (0, 0, 255)  # 雑魚敵
YELLOW = (255, 215, 0)  # ボス
CYAN = (0, 255, 255)  # MP
FLASH_COLOR = (255, 255, 255)  # ダメージ時の閃光
GOLD = (255, 223, 0)  # レベルアップ用


STATE_MAP = "MAP"  # 状態定数
STATE_BATTLE = "BATTLE"
STATE_ENDING = "ENDING"
STATE_GAME_OVER = "GAME_OVER"
STATE_TRANSITION = "TRANSITION"


MAP_VILLAGE = 0  # マップID
MAP_FIELD = 1
MAP_CAMPUS = 2

class Game:
    def __init__(self):
        pygame.init()  # Pygameの初期化
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RPG 工科クエスト")
        self.clock = pygame.time.Clock()

        try:  # フォント設定
            self.font = self.get_japanese_font(32)
            self.small_font = self.get_japanese_font(24)
            self.msg_font = self.get_japanese_font(20)
        except:
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
            self.msg_font = pygame.font.Font(None, 20)

        try:  # 背景画像の読み込み  1. 最初の村
            self.bg_village_original = pygame.image.load("fig/2.png")
            self.bg_village = pygame.transform.scale(self.bg_village_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            print("エラー: 画像が見つかりません。figフォルダに 2.png を入れてください。")
            self.bg_village = None
        
        try:  # 2. キャンパス
            self.bg_campus_original = pygame.image.load("fig/gray-dot3.jpg")
            self.bg_campus = pygame.transform.scale(self.bg_campus_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except FileNotFoundError:
            print("エラー: 画像が見つかりません。figフォルダに gray-dot3.jpg を入れてください。")
            self.bg_campus = None

        self.enemy_images = []  # 敵画像の読み込み
        self.boss_image = None
        try:  # 雑魚敵用 (1と2)
            img1 = pygame.image.load("fig/enemy_1.png").convert_alpha()
            img1 = pygame.transform.scale(img1, (100, 100)) # 雑魚敵サイズ
            
            img2 = pygame.image.load("fig/enemy_2.png").convert_alpha()
            img2 = pygame.transform.scale(img2, (100, 100)) # 雑魚敵サイズ
            
            self.enemy_images = [img1, img2]

            img3 = pygame.image.load("fig/enemy_3.png").convert_alpha()  # ボス用 (3)
            self.boss_image = pygame.transform.scale(img3, (200, 200)) # ボスサイズ    
        except FileNotFoundError:
            print("警告: 敵画像(fig/enemy_*.png)が見つかりません。四角で表示します。")

        self.player_size = 64  # --- プレイヤー画像の読み込み ---
        try:  # MapFieldで使用している魔法使いの画像を読み込む
            self.img_front = pygame.image.load("fig/map_mahou_1.png").convert_alpha()
            self.img_back = pygame.image.load("fig/map_mahou_b_1.png").convert_alpha()
            self.img_left = pygame.image.load("fig/map_mahou_l_1.png").convert_alpha()
            self.img_right = pygame.image.load("fig/map_mahou_r_1.png").convert_alpha()
            self.img_front = pygame.transform.scale(self.img_front, (self.player_size, self.player_size))  # サイズ調整
            self.img_back = pygame.transform.scale(self.img_back, (self.player_size, self.player_size))
            self.img_left = pygame.transform.scale(self.img_left, (self.player_size, self.player_size))
            self.img_right = pygame.transform.scale(self.img_right, (self.player_size, self.player_size))
            self.player_img = self.img_front 
        except FileNotFoundError:
            print("警告: キャラクター画像が見つかりません。")
            self.player_img = None

        self.player_pos = [400, 200]  # プレイヤー初期設定
        self.speed = 3
        self.player_level = 1  # ステータス初期値
        self.player_exp = 0
        self.player_next_exp = 100
        self.player_max_hp = 100
        self.player_hp = 100
        self.player_max_mp = 100
        self.player_mp = 100

        self.state = STATE_MAP  # ゲーム進行管理フラグ
        self.current_map = MAP_VILLAGE
        self.is_boss_battle = False

        self.enemies = []  # 戦闘用変数
        self.enemy_hp = 0
        self.heals_left = 0
        self.items = {"potion":3, "atk":1,"def":1}
        self.atk_buff_turns = 0
        self.def_buff_turns = 0
        self.atk_multiplier = 1.0
        self.def_multiplier = 1.0
        self.battle_logs = []

        self.transition_step = 0  # 遷移演出用
        self.transition_speed = 32
        self.transition_wait_timer = 0
        self.next_is_boss = False

        self.map_field = MapField.MapField(self.screen)  # MapFieldの初期化

    def get_japanese_font(self, size):
        font_names = ["meiryo", "msgothic", "yugothic", "hiraginosans", "notosanscjkjp"]
        available_fonts = pygame.font.get_fonts()
        for name in font_names:
            if name in available_fonts:
                return pygame.font.SysFont(name, size)
        return pygame.font.Font(None, size)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_BATTLE:
                    if event.key == pygame.K_a: # 攻撃
                        self.execute_turn("ATTACK")
                    elif event.key == pygame.K_m: # 魔法
                        self.execute_turn("MAGIC")
                    elif event.key == pygame.K_h: # 回復
                        self.execute_turn("HOIMI")
                    
                    # アイテム使用 (数字キー)
                    elif event.key == pygame.K_1:
                        self.use_item("potion")
                    elif event.key == pygame.K_2:
                        self.use_item("atk")
                    elif event.key == pygame.K_3:
                        self.use_item("def")
                
                # --- ゲームオーバー/クリア時の操作 ---
                elif self.state == STATE_ENDING or self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if self.state == STATE_GAME_OVER and event.key == pygame.K_r:
                        self.restart()

    def update(self):
        if self.state == STATE_BATTLE:  # 敵のアニメーション処理
            enemies_to_remove = []
            for enemy in self.enemies:
                if enemy.get("flash_timer", 0) > 0:  # 1. ダメージ演出
                    enemy["flash_timer"] -= 1
                if enemy["hp"] <= 0:  # 2. 死亡演出
                    if "death_timer" not in enemy:
                        enemy["death_timer"] = 60 
                        self.battle_logs.append(f"{enemy['name']}をやっつけた！")
                    enemy["death_timer"] -= 1
                    if enemy["death_timer"] <= 0:  # タイマー0で消滅（経験値獲得）
                        self.gain_exp(enemy["xp"])   # 経験値処理へ
                        enemies_to_remove.append(enemy)

            for enemy in enemies_to_remove:  # リスト消滅実行
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
            if len(self.enemies) == 0:
                self.end_battle(win=True)

        if self.state == STATE_MAP:  # 移動画面処理
            if self.current_map == MAP_FIELD:
                self.map_field.update()

                if getattr(self.map_field, "move_cool", 0) == 8:  # エンカウント判定
                    self.check_random_encounter()   

                if self.map_field.player_x >= 24:  # 次のマップへ遷移
                    if self.current_map < MAP_CAMPUS:
                        self.current_map = MAP_CAMPUS
                        self.player_pos[0] = 10    
            else:  #村　または　キャンパスの場合
                keys = pygame.key.get_pressed()
                moved = False

                if keys[pygame.K_LEFT]:  # 移動方向に応じて画像を変更
                    self.player_pos[0] -= self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_left
                if keys[pygame.K_RIGHT]:
                    self.player_pos[0] += self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_right
                if keys[pygame.K_UP]:
                    self.player_pos[1] -= self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_back
                if keys[pygame.K_DOWN]:
                    self.player_pos[1] += self.speed
                    moved = True
                    if self.player_img: self.player_img = self.img_front

                self.check_map_transition()  # マップ端の遷移判定
                if self.current_map == MAP_CAMPUS and self.player_pos[0]> 700:
                    self.start_battle(is_boss=True)

        if self.state == STATE_TRANSITION:  # 遷移演出
            self.update_transition()
    def game_over(self):
        self.state = STATE_GAME_OVER

    def restart(self):
        self.state = STATE_MAP
        self.current_map = MAP_VILLAGE
        self.player_hp = self.player_max_hp
        self.player_pos = [400, 200]
        self.player_level = 1
        self.player_exp = 0

    def enemy_couterattack(self):
        dmg = random.randint(10,30)
        dmg = int(dmg * self.def_multiplier)
        self.player_hp -= dmg
        #self.add_message(f"敵の反撃！ {dmg}ダメージ")
        if self.player_hp <= 0: self.atk_buff_turns -= 1;
        if self.atk_buff_turns > 0: self.atk_multiplier = 1.0
        if self.def_buff_turns > 0: self.def_buff_turns -= 1;
        if self.def_buff_turns == 0: self.def_multiplier = 1.0
        

    
    def gain_exp(self, amount):  # 重要：経験値とレベルアップ処理
        self.player_exp += amount
        self.battle_logs.append(f"{amount} Expを獲得！")
        while self.player_exp >= self.player_next_exp:  # レベルアップ判定
            self.player_level += 1  # 現在のExpを消費して次のレベルへ
            self.player_exp -= self.player_next_exp
            self.player_next_exp = int(self.player_next_exp * 1.5) # 必要経験値増加
            self.player_max_hp += 20
            self.player_max_mp += 10
            self.player_hp = self.player_max_hp  # 全回復（ボーナス）
            self.player_mp = self.player_max_mp
            self.battle_logs.append(f"レベルアップ！ Lv{self.player_level} になった！")
            self.battle_logs.append("最大HPとMPが増え、全回復した！")

    def start_transition_to_battle(self, is_boss):
        self.state = STATE_TRANSITION
        self.transition_step = 0
        self.transition_wait_timer = 0
        self.next_is_boss = is_boss

    def update_transition(self):
        if self.transition_step < SCREEN_WIDTH + 100:  # 画面より大きくなるまで広げる
            self.transition_step += self.transition_speed
        else:  # 画面が真っ暗になったらタイマーを作動させる
            self.transition_wait_timer += 1
            if self.transition_wait_timer > 60:  # 60フレーム（約1秒）待ったら戦闘開始
                self.start_battle(self.next_is_boss)
        
    def check_map_transition(self):  # 画面端でのマップ切り替え
        if self.player_pos[0] > SCREEN_WIDTH:
            if self.current_map < MAP_CAMPUS:
                self.current_map += 1
                self.player_pos[0] = 10
            else:
                self.player_pos[0] = SCREEN_WIDTH - self.player_size
        elif self.player_pos[0] < 0:
            if self.current_map > MAP_VILLAGE:
                self.current_map -= 1
                self.player_pos[0] = SCREEN_WIDTH - 10
            else:
                self.player_pos[0] = 0

        if self.player_pos[1] < 0: self.player_pos[1] = 0
        if self.player_pos[1] > SCREEN_HEIGHT - self.player_size:
            self.player_pos[1] = SCREEN_HEIGHT - self.player_size

    def check_random_encounter(self):
        if random.randint(0, 100) < 15:
            self.start_transition_to_battle(is_boss=False)

    def start_battle(self, is_boss):
        self.state = STATE_BATTLE
        self.is_boss_battle = is_boss
        self.enemies = []
        self.battle_logs = ["まもののむれがあらわれた！"]
        self.message_log = []
        self.heals_left = 5 if is_boss else 3
        
        self.atk_multiplier = 1.0  # バフのリセット
        self.atk_buff_turns = 0
        self.def_multiplier = 1.0
        self.def_buff_turns = 0
        
        if is_boss:
            self.enemies.append({
                "name": "悪の組織",
                "hp": 1000, 
                "max_hp": 1000,
                "atk": 35,
                "xp": 5000,
                "color": YELLOW, 
                "rect": pygame.Rect(300, 50, 200, 200),
                "flash_timer": 0,
                "img": self.boss_image 
            })
        else:
            num = random.randint(1,3)
            enemy_types = [
                {"name":"小テスト","hp":30,"max_hp":30,"atk":5,"xp":20,"color":GREEN},
                {"name":"中間レポート","hp":70,"max_hp":70,"atk":10,"xp":50,"color":BLUE},
                {"name":"期末試験","hp":100,"max_hp":100,"atk":15,"xp":70,"color": RED},
            ]
            for i in range(num):
                x_pos = 150 + i * 180
                enemy_temp = random.choice(enemy_types)
                img = self.enemy_images[i % len(self.enemy_images)] if self.enemy_images else None
                self.enemies.append({
                    "name": f"{enemy_temp['name']}",
                    "hp": enemy_temp['hp'],
                    "max_hp": enemy_temp['max_hp'],
                    "atk": enemy_temp['atk'],
                    "xp": enemy_temp['xp'],
                    "color":enemy_temp['color'],
                    "rect": pygame.Rect(x_pos, 100, 100, 100),
                    "flash_timer": 0,
                    "img": img
                })
    
    def execute_turn(self, action_type):
        self.battle_logs = [] 
        valid_targets = [e for e in self.enemies if e["hp"] > 0]
        if not valid_targets and len(self.enemies) == 0:  # 生きている敵がいない場合はなにもしない
            return
        
        level_bonus = (self.player_level - 1) * 2
        acted = False

        if action_type == "HOIMI":
            if self.player_mp >= 10:
                self.player_mp -= 10
                heal = random.randint(30, 50) + level_bonus
                self.player_hp = min(self.player_max_hp, self.player_hp + heal)
                self.battle_logs.append(f"ホイミ！ こうかとんのHPが{heal}回復！")
                acted = True
            else:
                self.battle_logs.append("こうかとんのMPが足りない！")

        elif action_type == "MAGIC":
            if self.player_mp >= 30:
                self.player_mp -= 30
                damage = random.randint(50, 80) + (level_bonus * 2)
                damage = int(damage * self.atk_multiplier) # 魔法にも攻撃バフ乗せる場合
                if random.randint(0, 100) < 10:
                    damage = int(damage * 1.5)
                    self.battle_logs.append("会心の一撃！！")
                
                target = valid_targets[0]
                target["hp"] -= damage
                target["flash_timer"] = 10
                self.battle_logs.append(f"こうかとんはメラを唱えた！ {damage}ダメージをあたえた！")
                acted = True
            else:
                self.battle_logs.append("こうかとんのMPが足りない！")

        elif action_type == "ATTACK":
            damage = int((random.randint(20, 30) + level_bonus) * self.atk_multiplier)
            if random.randint(0, 100) < 15:
                damage *= 2
                self.battle_logs.append("会心の一撃！！")
            
            target = valid_targets[0]
            target["hp"] -= damage
            target["flash_timer"] = 10
            self.battle_logs.append(f"こうかとんは{damage}ダメージをあたえた！")
            acted = True

        if acted:
            self.enemy_turn()

    def use_item(self, item_name):
        self.battle_logs = []
        if self.items.get(item_name, 0) > 0:
            self.items[item_name] -= 1
            if item_name == "potion":
                self.player_hp = min(self.player_max_hp, self.player_hp + 150)
                self.battle_logs.append("こうかとんは回復薬を使用した！ HPが回復した！")
            elif item_name == "atk":
                self.atk_multiplier = 1.5
                self.atk_buff_turns = 3
                self.battle_logs.append("こうかとんの攻撃力が上がった！")
            elif item_name == "def":
                self.def_multiplier = 0.5
                self.def_buff_turns = 3
                self.battle_logs.append("こうかとんの防御力が上がった！")
            
            self.enemy_turn()  # アイテムを使っても敵のターンになる
        else:
            self.battle_logs.append("アイテムが足りない！")

    def enemy_turn(self):
        surviving = [e for e in self.enemies if e["hp"] > 0]
        total_dmg = 0
        for enemy in surviving:
            if random.randint(0, 100) >= 20: # 80%で攻撃
                dmg = int(random.randint(enemy["atk"]-3, enemy["atk"]+3) * self.def_multiplier)
                total_dmg += dmg
            else:
                self.battle_logs.append("まものの攻撃！　こうかとんはすばやく身をかわした！")
        
        if total_dmg > 0:
            self.player_hp -= total_dmg
            self.battle_logs.append(f"まものの攻撃！ 計{total_dmg}のダメージ！")
        
        if self.atk_buff_turns > 0:  # バフターンの処理
            self.atk_buff_turns -= 1
            if self.atk_buff_turns == 0: self.atk_multiplier = 1.0
        
        if self.def_buff_turns > 0:
            self.def_buff_turns -= 1
            if self.def_buff_turns == 0: self.def_multiplier = 1.0

        if self.player_hp <= 0:
            self.player_hp = 0
            self.end_battle(win=False)

    def end_battle(self, win):
        self.state = STATE_ENDING if (win and self.is_boss_battle) else STATE_MAP
        if not win: self.state = STATE_GAME_OVER       

    def draw_map_elements(self):
        if self.current_map == MAP_VILLAGE:
            if self.bg_village: self.screen.blit(self.bg_village, (0,0))
            else: self.screen.fill((100,200,100))
                
        elif self.current_map == MAP_CAMPUS:
            if self.bg_campus: self.screen.blit(self.bg_campus, (0, 0))
            else: self.screen.fill(GRAY)
        
        if self.current_map == MAP_FIELD:  # キャラクター or MapField
            self.map_field.draw()
        else:
            if self.player_img:
                self.screen.blit(self.player_img, self.player_pos)
            else:
                pygame.draw.rect(self.screen, RED, (*self.player_pos, self.player_size, self.player_size))
        
        # ステータス
        status_hp = self.small_font.render(f"Lv:{self.player_level} HP:{self.player_hp}/{self.player_max_hp}", True, BLACK)
        status_mp = self.small_font.render(f"MP:{self.player_mp}/{self.player_max_mp}", True, BLACK)
        self.screen.blit(status_hp, (550, 20))
        self.screen.blit(status_mp, (607, 44))

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == STATE_MAP:
            self.draw_map_elements()

        elif self.state == STATE_BATTLE:
            # 敵描画
            for enemy in self.enemies:
                if "death_timer" in enemy:
                    if (enemy["death_timer"] // 5) % 2 == 0:
                        self._draw_enemy(enemy)
                else:
                    self._draw_enemy(enemy)

            # UI枠
            pygame.draw.rect(self.screen, BLACK, (0, 350, SCREEN_WIDTH, 250))
            pygame.draw.rect(self.screen, WHITE, (0, 350, SCREEN_WIDTH, 250), 2)

            # ステータス
            hp_col = WHITE if self.player_hp > 30 else RED
            self.screen.blit(self.font.render(f"Lv: {self.player_level}", True, GOLD), (30, 365))
            self.screen.blit(self.font.render(f"HP: {self.player_hp}/{self.player_max_hp}", True, hp_col), (300, 365))
            self.screen.blit(self.font.render(f"MP: {self.player_mp}/{self.player_max_mp}", True, CYAN), (550, 365))

            # コマンド
            cmd = "[A]こうげき [M]メラ [H]ホイミ  [1]やくそう [2]攻撃UP [3]防御UP"
            self.screen.blit(self.small_font.render(cmd, True, YELLOW), (30, 410))
            pygame.draw.line(self.screen, WHITE, (0, 450), (SCREEN_WIDTH, 450), 1)

            # ログ
            for i, log in enumerate(self.battle_logs[-5:]):
                col = YELLOW if "会心" in log else (GOLD if "レベルアップ" in log else WHITE)
                self.screen.blit(self.small_font.render(log, True, col), (30, 460 + i * 28))

        elif self.state == STATE_TRANSITION:
            self.draw_map_elements()
            rect_w = self.transition_step
            rect_h = int(self.transition_step * (SCREEN_HEIGHT / SCREEN_WIDTH))
            black_rect = pygame.Rect(SCREEN_WIDTH//2 - rect_w//2, SCREEN_HEIGHT//2 - rect_h//2, rect_w, rect_h)
            pygame.draw.rect(self.screen, BLACK, black_rect)

        elif self.state == STATE_ENDING:
            self.screen.fill(WHITE)
            self.screen.blit(self.font.render("MISSION COMPLETE!", True, BLACK), (200, 300))

        elif self.state == STATE_GAME_OVER:
            self.screen.fill(BLACK)
            self.screen.blit(self.font.render("GAME OVER... (R to Retry)", True, RED), (200, 300))

        pygame.display.flip()

    def _draw_enemy(self, enemy):
        """敵描画の内部関数"""
        if enemy.get("img"):
            # フラッシュ（被ダメ）時は描画しない＝点滅
            if enemy.get("flash_timer", 0) > 0 and (enemy["flash_timer"] // 2) % 2 == 0:
                pass
            else:
                self.screen.blit(enemy["img"], enemy["rect"])
        else:
            # 画像がない場合
            draw_color = FLASH_COLOR if enemy.get("flash_timer", 0) > 0 else enemy["color"]
            pygame.draw.rect(self.screen, draw_color, enemy["rect"])
        
        # HPバー
        if enemy["hp"] > 0:
            hp_rate = enemy["hp"] / enemy["max_hp"]
            pygame.draw.rect(self.screen, RED, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width, 5))
            pygame.draw.rect(self.screen, GREEN, (enemy["rect"].x, enemy["rect"].y - 10, enemy["rect"].width * hp_rate, 5))

if __name__ == "__main__":
    game = Game()
    game.run()