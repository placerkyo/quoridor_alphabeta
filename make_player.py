from collections import deque
import random
import time

class make_player:
    #盤面の初期化
    def __init__(self,player):
        self.player = player        #自分の手番
        self.board = [[0]*17 for _ in range(17)]     #盤面の初期化
        self.start_time = time.time()      #実行時間を測るためにこの時点での時間を記録

    #各種の情報を入れていく
    def input_information(self,list_information):
        self.list_information = list_information       #盤面情報をself.list_informationに入れる
        if self.list_information == [-1]:              #盤面情報が-1の場合、勝負がついているので'finish'を返す
            return 'finish'

        self.board[self.list_information[1]*2-2][self.list_information[0]*2-2] = 2     #白の駒
        self.board[self.list_information[3]*2-2][self.list_information[2]*2-2] = 3     #黒の駒
        if self.player == 1:            #自分が先手の場合
            self.player_pos = self.list_information[0:2]     #自分の駒の位置
            self.partner_pos = self.list_information[2:4]     #相手の駒の位置
            self.player_goal = 9                             #自分のゴール列
            self.partner_goal = 1                             #相手のゴール列
            self.player_wall_nu = self.list_information[4]    #自分の残壁数
            self.partner_wall_nu = self.list_information[5]   #相手の残壁数
        else :                          #自分が後手の場合
            self.player_pos = self.list_information[2:4]     #自分の駒の位置
            self.partner_pos = self.list_information[0:2]     #相手の駒の位置
            self.player_goal = 1                             #自分のゴール列
            self.partner_goal = 9                             #相手のゴール列
            self.player_wall_nu = self.list_information[5]    #自分の残壁数
            self.partner_wall_nu = self.list_information[4]   #相手の残壁数

        wall = self.list_information[6:]            #壁に関する情報をwallに取り出す
        wall_conf_1 = []                  #置かれている壁周りを探索する際の壁を置く候補にするため、その候補を入れるリスト
        wall_conf_2 = []                  #壁を置く候補を簡単に変えられるように3種類のリストを用意して最後にまとめる
        wall_conf_3 = []
        while len(wall)>0:         #壁の丈夫がなくなるまで回す
            x = wall.pop(0)        #壁の情報を出していく。x,y,zの順番に入っており、x,yは座標を、zは向きを表す
            y = wall.pop(0)
            z = wall.pop(0)
            self.board[y*2-1][x*2-1] = 1         #壁情報は1で表す

            #壁の情報を入れるのと、壁を置く候補を見つけていく処理を同時に行う
            if z == 1:              #置かれている壁が横向きのとき
                self.board[y*2-2][x*2-1],self.board[y*2][x*2-1] = 1,1     #壁情報をいれる
                #壁の周りに壁を置ける位置があればwall_confにいれていく
                for wa_con in [[x,y-2,1],[x,y+2,1]]:             
                    if self.is_put_wall(wa_con):
                        wall_conf_1.append(wa_con)
                for wa_con in [[x,y-1,2],[x,y+1,2]]:
                    if self.is_put_wall(wa_con):
                        wall_conf_2.append(wa_con)
                for wa_con in [[x-1,y,2],[x+1,y,2]]:
                    if self.is_put_wall(wa_con):
                        wall_conf_3.append(wa_con)
            else :               #置かれている壁が横向きのとき
                self.board[y*2-1][x*2-2],self.board[y*2-1][x*2] = 1,1     #壁情報をいれる
                #壁の周りに壁を置ける位置があればwall_confにいれていく
                for wa_con in [[x-2,y,2],[x+2,y,2]]:             
                    if self.is_put_wall(wa_con):
                        wall_conf_1.append(wa_con)   
                for wa_con in [[x-1,y,1],[x+1,y,1]]:
                    if self.is_put_wall(wa_con):
                        wall_conf_2.append(wa_con)
                for wa_con in [[x,y-1,1],[x,y+1,1]]:
                    if self.is_put_wall(wa_con):
                        wall_conf_3.append(wa_con) 

        self.wall_conf = wall_conf_1 + wall_conf_2 + wall_conf_3      #3種類のwall_confを合わせる


    #アルファベータ法
    def alphabeta(self,depth):
        return self.alphabeta_r(-float('inf'), float('inf'), depth)    #alphaとbetaを設定してalphabeta_rに渡す

    def alphabeta_r(self,alpha, beta, depth):
        if depth == 0:                #depth==0であれば、これ以上探索は行わずその時点の盤面の評価を返す
            return self.eval_1(), None

        best_score = -float('inf')       #best_scoreを-∞で初期化
        if depth%2 == 1:                 #depthが奇数の場合、自分の手番
            pos = self.player_pos        #手番の駒の位置posとturnをきめる
            turn = 'player'
        else :                           #depthが奇数の場合、自分の手番
            pos = self.partner_pos       #手番の駒の位置posとturnをきめる
            turn = 'partner'

        moves = self.generate_moves(pos,turn)     #候補手を見つけてmovesに入れる

        #処理時間で探索を終了させるため、探索を行う前にmovesの手を評価順に並び替える
        moves_score_dic = {}              #辞書に手=keyとその評価値=valueを入れていく
        for i,move in enumerate(moves):   #movesの候補手を
            #候補手を置く
            if move[0] == 1:              #駒を置く手
                next_pos = move[1:]
                move_ = move + pos
                self.move_pos(pos,next_pos,turn)
            else :                        #壁を置く手
                move_ = move
                self.put_wall(move[1:],turn) 
            #候補手を置いたときの盤面を評価する
            if depth != 1:
                moves_score_dic[i] = (self.eval_0())*((-1)**(depth%2))      #depthが1でないときは残壁数を考慮しない評価をする
            else :
                moves_score_dic[i] = (self.eval_1())*((-1)**(depth%2))      #depthが1のときは残壁数を考慮する評価をする
            self.undo(move_,turn)    #行った手を戻す

        moves_score = sorted(moves_score_dic.items(), key=lambda x:x[1], reverse=True)      #評価値順に並び替える
        moves = [moves[i[0]] for i in moves_score]       #movesを評価順に並べたのに変える

        #探索時間短縮のため、最大評価値上位18手のみ探索に使う
        if depth !=1:
            moves = moves[:max(18,len(moves))]
        #depth==1の場合並び替えた最初の手が最善手のため、この一手のみmovesに入れる
        else :
            moves = moves[0:1]

        #movesに入っている手を探索していく
        for move in moves:
            if move[0] == 1:              #駒を置く手
                next_pos = move[1:]
                if depth==3 and move[2]==self.player_goal:   #次の手ですぐにゴールできるときは探索を行わずにその手をbest_moveにする
                    best_score, best_move = 10 , move
                    break
                move += pos
                self.move_pos(pos,next_pos,turn)
            else :                        #壁を置く手
                self.put_wall(move[1:],turn)
            
            score, child_best = self.alphabeta_r(-beta, -alpha, depth-1)     #次の手を探索
            score = -score

            self.undo(move,turn)          #行った手を戻す

            if score > best_score:        #スコアがbest_scoreより大きくなる場合はbest_scoreとbest_moveを更新する
                best_score = score
                if move[0] == 1: move = move[:-2]
                best_move = move

            #この時点での時間を測り、実行時間が4.98sを超えている場合はその時点で探索を終了する
            if time.time() - self.start_time > 4.98: break

            #アルファベータ法
            if best_score > alpha:       #alphaの更新
                alpha = best_score
            if alpha >= beta:            #不要な探索を省略する
                break
        
        return best_score, best_move
        

    #盤面の評価を行う。eval_0は残壁数を考慮しない、eval_1は残壁数を考慮する
    def eval_0(self):
        mi_pl = self.min_dis_ignore_pa(self.player_pos,self.player_goal)     #mi_plはplayer(自分)のゴールまでの最短距離
        mi_pa = self.min_dis_ignore_pa(self.partner_pos,self.partner_goal)     #mi_plはpartner(相手)のゴールまでの最短距離
        score = mi_pl*1 + mi_pa*(-1)                            #自分の最短距離の重さを1,相手の最短距離の重さを-1として評価値に
        return score
    
    def eval_1(self):
        #特徴量に対する重さを格納したリスト。重さの値はPAに則った学習で決定した
        W = [ 0.8857026, -0.87554909, 0.46791599, 0.26234566, -0.23649033]

        #最短距離に関する特徴量
        mi_pl = self.min_dis_ignore_pa(self.player_pos,self.player_goal)     #mi_plはplayer(自分)のゴールまでの最短距離
        mi_pa = self.min_dis_ignore_pa(self.partner_pos,self.partner_goal)     #mi_plはpartner(相手)のゴールまでの最短距
        score = mi_pl*W[0] + mi_pa*W[1]
        #ゴールしている場合、評価値を大きくして強調する
        if mi_pl == 0:
            score -= 20
        if mi_pa == 0:
            score += 20
        #残壁数に関する特徴量
        if self.player_wall_nu >=6:          #壁を6以上持っているときに作用する
            score += self.player_wall_nu*W[2]
        if self.player_wall_nu >=4:          #壁を4以上持っているときに作用する
            score += self.player_wall_nu*W[3]
        if self.player_wall_nu >=3:          #壁を3以上持っているときに作用する
            score += self.player_wall_nu*W[4]

        return score


    #可能な手を返す
    def generate_moves(self,pos,turn):
        moves = []                     #ここに可能な手を入れていく
        #移動可能なマスをmovesに入れていく
        for idousaki in self.return_pos(pos):
            idousaki[0],idousaki[1] = (idousaki[0]+2)//2,(idousaki[1]+2)//2
            moves.append([1,idousaki[0],idousaki[1]])
        #残壁数が0の場合、ここでmovesを返す
        if (turn == 'player' and self.player_wall_nu==0) or (turn == 'partner' and self.partner_wall_nu==0):
            return moves
        #置くことができる壁の位置をmovesに入れていく
        for okisaki in self.return_wall():
            moves.append([2] + okisaki)
        return moves                #movesを返す


    #移動可能な手を返す
    def return_pos(self,pos):
        Dir = [[0,1],[0,-1],[1,0],[-1,0]]         #Dirに四方向のベクトルを入れておく
        x,y = pos[0]*2-2,pos[1]*2-2
        block = []                                #blockに移動可能なマスを入れていく
        for dir in Dir:                 #移動方向ごとに移動可能かを見ていく
            #盤面の外に出る or 移動方向に壁がある　なら移動できない
            if not(0<=x+dir[0]<=16 and 0<=y+dir[1]<=16) or (self.board[y+dir[1]][x+dir[0]]!=0):
                continue
            #移動先が0であれば移動可能
            if self.board[y+dir[1]*2][x+dir[0]*2]==0:           
                block.append([x+dir[0]*2,y+dir[1]*2])
                continue
            #移動先に相手の駒があり、その後ろに壁がなければ、相手の駒を越えて移動可能
            if (0<=x+dir[0]*3<=16 and 0<=y+dir[1]*3<=16) and (self.board[y+dir[1]*3][x+dir[0]*3]==0):
                block.append([x+dir[0]*4,y+dir[1]*4])
                continue
            #移動先に相手の駒があり、その後ろに壁があり、相手の駒の移動方向の垂直2方向に壁がなければ、その先に移動可能
            #2方向に分けて処理
            if (0<=x+dir[0]*2+dir[1]<=16 and 0<=y+dir[1]*2+dir[0]<=16) and (self.board[y+dir[1]*2+dir[0]][x+dir[0]*2+dir[1]])==0:
                block.append([x+dir[0]*2+dir[1]*2,y+dir[1]*2+dir[0]*2])
            if (0<=x+dir[0]*2-dir[1]<=16 and 0<=y+dir[1]*2-dir[0]<=16) and (self.board[y+dir[1]*2-dir[0]][x+dir[0]*2-dir[1]])==0:
                block.append([x+dir[0]*2-dir[1]*2,y+dir[1]*2-dir[0]*2])
        return block                      #移動可能な手が入ったblockを返す


    #与えられたマスから各マスまでの最短距離を返す
    def cal_dis(self,pos):
        visited = [[[] for _ in range(9)] for _ in range(9)]    #visitedに各マスまでの最短距離を入れていく
        visited[pos[1]-1][pos[0]-1] = 0             #駒のあるマスは距離0のなので0をいれる
        next_q = deque([pos])                       #next_qに探索しているマスをいれる。最初は駒がある位置を入れる
        #幅優先探索を行う
        while len(next_q)>0:                     #next_qが空になるまで探索を行う
            now_block = next_q.popleft()
            for next_block in self.return_pos(now_block):        #可能な手を全て見ていく
                next_block[0],next_block[1] = (next_block[0]+2)//2,(next_block[1]+2)//2
                if visited[next_block[1]-1][next_block[0]-1] != []: continue        #移動先が空のリストでなければ探索済み
                visited[next_block[1]-1][next_block[0]-1] = visited[now_block[1]-1][now_block[0]-1] + 1       #距離はもともといた位置までの距離+1
                next_q.append(next_block)             #後でそこから探索を始められる余殃にnext_qにいれる
        return visited          #各マスまでの最短距離が入ったリストを返す


    #ゴールまでの最短距離を返す
    def min_dis(self,pos,goal):
        visited = self.cal_dis(pos)        #各マスまでの最短距離を算出する
        min_route = 9*9+1                 #最短距離がはいる変数。初期値は9×9+1
        for i in visited[goal-1]:         #ゴール列の要素を見ていき、最短距離を更新していく
            if i != [] and i < min_route:
                min_route = i
        if min_route==9*9+1: return False      #最短距離が9×9+1のままのときゴールができていないのでFalseを返す
        else : return min_route                #最短距離を返す


    #ゴールまでの平均距離を求めるメソッドだが使用していない
    def min_ave_dis(self,pos,goal):    
        visited = self.cal_dis(pos)
        min_route = 9**9+1
        ave_route_li = []
        for i in visited[goal-1]:
            if i != [] :
                if  i < min_route:
                    min_route = i
                ave_route_li.append(i)
        if len(ave_route_li) > 0:
            ave_route = sum(ave_route_li) / len(ave_route_li)
        else : ave_route = False
        if min_route==9**9+1: return False, False
        else : return min_route, ave_route


    #ゴールできるかどうかの判定を行う
    def is_goal(self,pos,goal):
        visited = [[[] for _ in range(9)] for _ in range(9)]         #探索済みか否かの情報を入れていく。探索済みなら1、そうでなければ空
        visited[pos[1]-1][pos[0]-1] = 1                 #現在駒がある位置は探索済み
        next_q = deque([pos])                           #next_qに探索しているマスをいれる。最初は駒がある位置を入れる
        fl = False                        #ゴール可能かどうかのフラグ。Falseなら不可、Trueなら可
        #深さ優先探索を行う
        while len(next_q)>0:                     #next_qが空になるまで探索を行う
            now_block = next_q.pop()
            for next_block in self.return_pos(now_block):        #可能な手を全て見ていく
                next_block[0],next_block[1] = (next_block[0]+2)//2,(next_block[1]+2)//2
                if visited[next_block[1]-1][next_block[0]-1] != []: continue        #移動先が空のリストでなければ探索済み
                if next_block[1]-1 == goal-1:                    #ゴール列であればゴール到達可能
                    fl = True                                    #flをTrueにして探索終了
                    break
                visited[next_block[1]-1][next_block[0]-1] = 1         #ゴール列でなければ1をいれる
                next_q.append(next_block)                             #next_qに追加
        return fl                             #TrueかFalseを返す

    #相手の駒を無視して移動可能な手を返す
    def return_pos_ignore_pa(self,pos):
        Dir = [[0,1],[0,-1],[1,0],[-1,0]]         #Dirに四方向のベクトルを入れておく
        x,y = pos[0]*2-2,pos[1]*2-2
        block = []                                #blockに移動可能なマスを入れていく
        for dir in Dir:                 #移動方向ごとに移動可能かを見ていく
            #盤面の外に出る or 移動方向に壁がある　なら移動できない
            if not(0<=x+dir[0]<=16 and 0<=y+dir[1]<=16) or not(self.board[y+dir[1]][x+dir[0]]==0): continue
            #そうでなければ移動可能
            block.append([x+dir[0]*2,y+dir[1]*2])
        return block                      #移動可能な手が入ったblockを返す


    #相手の駒を無視して与えられたマスから各マスまでの最短距離を返す
    def cal_dis_ignore_pa(self,pos):
        visited = [[[] for _ in range(9)] for _ in range(9)]    #visitedに各マスまでの最短距離を入れていく
        visited[pos[1]-1][pos[0]-1] = 0             #駒のあるマスは距離0のなので0をいれる
        next_q = deque([pos])                       #next_qに探索しているマスをいれる。最初は駒がある位置を入れる
        #幅優先探索を行う
        while len(next_q)>0:                     #next_qが空になるまで探索を行う
            now_block = next_q.popleft()
            for next_block in self.return_pos_ignore_pa(now_block):        #可能な手を全て見ていく
                next_block[0],next_block[1] = (next_block[0]+2)//2,(next_block[1]+2)//2
                if visited[next_block[1]-1][next_block[0]-1] != []: continue        #移動先が空のリストでなければ探索済
                visited[next_block[1]-1][next_block[0]-1] = visited[now_block[1]-1][now_block[0]-1] + 1       #距離はもともといた位置までの距離+1
                next_q.append(next_block)            #後でそこから探索を始められる余殃にnext_qにいれる
        return visited          #各マスまでの最短距離が入ったリストを返す


    #相手の駒を無視してゴールまでの最短距離を示す
    def min_dis_ignore_pa(self,pos,goal):
        visited = self.cal_dis_ignore_pa(pos)        #各マスまでの最短距離を算出する
        min_route = 9*9+1                 #最短距離がはいる変数。初期値は9×9+1
        for i in visited[goal-1]:
            if i != [] and i < min_route:
                min_route = i
        if min_route==9*9+1: return False      #最短距離が9×9+1のままのときゴールができていないのでFalseを返す
        else : return min_route                #最短距離を返す


    #壁を置くことが可能な位置(探索を行う位置)を返す
    def return_wall(self):
        wall = []                              #ここに壁を置くことができる位置を入れていく

        #自分の駒の周りの壁候補を判定していく
        x,y = self.player_pos
        wall_conf = [[x-1,y-1,1],[x-1,y-1,2],[x,y-1,1],[x,y-1,2],[x-1,y,1],[x-1,y,2],[x,y,1],[x,y,2],[x-1,y-2,1],[x,y-2,1],[x-1,y+1,1],[x,y+1,1],[x-2,y-1,2],[x,y,2],[x+1,y-1,2],[x+1,y,2]]
        for i in wall_conf:
            if self.is_put_wall(i):
                wall.append(i)

        #相手の駒の周りの壁候補を判定していく
        x,y = self.partner_pos
        wall_conf = [[x-1,y-1,1],[x-1,y-1,2],[x,y-1,1],[x,y-1,2],[x-1,y,1],[x-1,y,2],[x,y,1],[x,y,2],[x-1,y-2,1],[x,y-2,1],[x-1,y+1,1],[x,y+1,1],[x-2,y-1,2],[x,y,2],[x+1,y-1,2],[x+1,y,2]]
        for i in wall_conf:
            if self.is_put_wall(i) and not(i in wall):
                wall.append(i)

        #self.wall_confに入った壁候補を判定していく
        for i in list(self.wall_conf):
            if self.is_put_wall(i) and not(i in wall):
                wall.append(i)

        return wall           #壁を置くことが可能な位置が言ったリストを返す


    #与えられた位置に壁が置けるかどうかを返す
    def is_put_wall(self,wall_list):
        x = wall_list[0]           #壁の列
        y = wall_list[1]           #壁の行
        z = wall_list[2]           #縦か横か

        #盤面から出てしまう場合は置けないのでFalseを返す
        if not(1<=x<=8) or not(1<=y<=8):
             return False          
        #すでに壁が置けれている場合は桶にのでFalseを返す
        if self.board[y*2-1][x*2-1]==1 or (z==1 and (self.board[y*2-2][x*2-1]==1 or self.board[y*2][x*2-1]==1)) or (z==2 and (self.board[y*2-1][x*2-2]==1 or self.board[y*2-1][x*2]==1)):
            return False

        #ここからは壁を置いた場合ゴールできなくならないかの判定
        #壁を置く
        self.board[y*2-1][x*2-1] = 1
        if z == 1: self.board[y*2-2][x*2-1],self.board[y*2][x*2-1] = 1,1
        else : self.board[y*2-1][x*2-2],self.board[y*2-1][x*2] = 1,1
        #自分の駒がゴールできるかの判定
        visited = self.is_goal(self.player_pos,self.player_goal)
        if visited == False : fl_1 = False           #ゴールできなければfl_1をFalseとする
        else : fl_1 = True                           #ゴールで着ればfl_1をTrueとする
        #相手の駒がゴールできるかの判定
        visited = self.is_goal(self.partner_pos,self.partner_goal) 
        if visited == False : fl_2 = False           #ゴールできなければfl_1をFalseとする
        else : fl_2 = True                           #ゴールで着ればfl_1をTrueとする
        #行った操作を戻す
        self.undo_in_is_put_wall([2]+wall_list)      

        #どちらの駒もゴール可能な場合TrueをそうでなければFalseを返す
        if not(fl_1) or not(fl_2): return False
        return True    


    #駒を与えられた位置に移動させる
    def move_pos(self,now_pos,next_pos,turn):
        x,y = now_pos[0]*2-2,now_pos[1]*2-2      #移動前の座標を17×17の盤面の座標に変換して、x,yに代入する     
        pre_nu = self.board[y][x]                #移動させたい駒の数字(2か3)をpre_nuに入れておく
        self.board[y][x] = 0                     #移動前の位置を0にする
        next_x, next_y = next_pos[0]*2-2,next_pos[1]*2-2       #移動後の座標を17×17の盤面の座標に変換して、x,yに代入する
        self.board[next_y][next_x] = pre_nu                     #移動後の位置をもともと移動前の位置に入っていた数字にする
        #駒の位置を表すメンバを更新する
        if turn == 'player':
            self.player_pos = next_pos
        else :
            self.partner_pos = next_pos


    #与えられた位置に壁を置く
    def put_wall(self,wall_list,turn):
        x = wall_list[0]           #壁の列
        y = wall_list[1]           #壁の行
        z = wall_list[2]           #縦か横か
        #self.boardの壁を置く位置を1にする
        self.board[y*2-1][x*2-1] = 1
        if z == 1: 
            self.board[y*2-2][x*2-1] = 1
            self.board[y*2][x*2-1] = 1
        else : 
            self.board[y*2-1][x*2-2] = 1
            self.board[y*2-1][x*2] = 1
        #残壁数を表すメンバを更新する
        if turn == 'player':
            self.player_wall_nu -= 1
        else :
            self.player_wall_nu -= 1


    #移動させた駒屋置いた壁を戻す
    def undo(self,undo_list,turn):
        #壁を取り除く
        if undo_list[0] == 2:
            x = undo_list[1]           #壁の列
            y = undo_list[2]           #壁の行
            z = undo_list[3]           #縦か横か
            #壁を取り除く位置のself.boardを0にする
            self.board[y*2-1][x*2-1] = 0
            if z == 1: 
                self.board[y*2-2][x*2-1] = 0
                self.board[y*2][x*2-1] = 0
            else : 
                self.board[y*2-1][x*2-2] = 0
                self.board[y*2-1][x*2] = 0
            #残壁数を表すメンバを更新する
            if turn == 'player':
                self.player_wall_nu += 1
            else :
                self.player_wall_nu += 1
        #駒を戻す
        else :
            x,y = undo_list[1]*2-2,undo_list[2]*2-2       #戻したい駒がある位置
            pre_nu = self.board[y][x]                     #戻したい駒の数字(2か3)をpre_nuに入れておく
            self.board[y][x] = 0                          #戻したい駒の位置を0にする
            pre_x, pre_y = undo_list[3]*2-2,undo_list[4]*2-2           #戻す位置
            self.board[pre_y][pre_x] = pre_nu             #戻す位置に駒の数字を入れる
            #駒の位置を表すメンバを更新する
            if turn == 'player':
                self.player_pos = undo_list[3:5]
            else :
                self.partner_pos = undo_list[3:5]


    #is_put_wall内で使う。置いた壁を戻す
    def undo_in_is_put_wall(self,undo_list):
        x = undo_list[1]           #壁の列
        y = undo_list[2]           #壁の行
        z = undo_list[3]           #縦か横か
        #壁を取り除く位置のself.boardを0にする
        self.board[y*2-1][x*2-1] = 0
        if z == 1: 
            self.board[y*2-2][x*2-1] = 0
            self.board[y*2][x*2-1] = 0
        else : 
            self.board[y*2-1][x*2-2] = 0
            self.board[y*2-1][x*2] = 0


    #3手目までの定石を返す(前に進む)
    def initial_move_1(self,dir):           #dirはゴールの方向
        x,y = self.player_pos[0]*2-2,self.player_pos[1]*2-2           #x,yは自分の駒の位置
        if not(0<=x+dir[0]<=16 and 0<=y+dir[1]<=16) or (self.board[y+dir[1]][x+dir[0]]!=0): return False    #前に進んだときに盤面空でないか
        if self.board[y+dir[1]*2][x+dir[0]*2]==0: return [1,self.player_pos[0]+dir[0],self.player_pos[1]+dir[1]]     #前に進める場合はその手番を返す
        return False         #前に進めないときはFalseを返す


    #4手目の定石を返す(後ろに壁を置く)
    def initial_move_2(self,dir):           #dirはゴールの方向
        x,y = self.player_pos           #x,yは自分の駒の位置
        if dir[1] == 1:                 #壁を置きたい位置をwall_confに入れる
            wall_conf = [x-1,y-1,2]
        else :
            wall_conf = [x-1,y,2]
        if self.is_put_wall(wall_conf): return [2]+wall_conf       #壁を置くことができればその手を返す
        return False          #壁を置けないときはFalseを返す


    #5手目の定石を返す(後ろに壁を置く)
    def initial_move_3(self,dir):           #dirはゴールの方向
        x,y = self.player_pos           #x,yは自分の駒の位置
        if dir[1] == 1:                 #壁を置きたい位置をwall_confに入れる
            wall_conf = [x+1,y-1,2]
        else :
            wall_conf = [x+1,y,2]
        if self.is_put_wall(wall_conf): return [2]+wall_conf       #壁を置くことができればその手を返す
        return False          #壁を置けないときはFalseを返す


############################################################################################################################################################

player = int(input())
print(player)

#定石を打つ際に使う、ゴールの方向を表すdirの作製
if player==1: dir = [0,1]
else : dir = [0,-1]

#初手から5手は定石を打つ
nu_move = 0            #自分が打った手の回数をカウントする
while nu_move <= 4:               #自分が打った手が5手未満であれば定石を打つ
    data = make_player(player)
    finish = data.input_information(list(map(int,input().split())))     #盤面を読み込む

    #3手目までは前に進む
    if nu_move <= 2:
        best_move = data.initial_move_1(dir)   #定石が打てるかの判定
        if best_move != False:          #定石が打てればそれを返す
            print(*best_move)
            nu_move += 1
            continue
        else :                          #定石が打てなければアルファベータ法により最善手を決める
            best_score, best_move = data.alphabeta(3)
            print(*best_move)
            break
    #4手目と5手目自分の後ろに壁を置く
    if nu_move == 3:
        best_move = data.initial_move_2(dir)   #定石が打てるかの判定
        if best_move != False:          #定石が打てればそれを返す
            print(*best_move)
            nu_move += 1
            continue
        else :                          #定石が打てなければアルファベータ法により最善手を決める
            best_score, best_move = data.alphabeta(3)
            print(*best_move)
            break
    if nu_move == 4:
        best_move = data.initial_move_3(dir)   #定石が打てるかの判定
        if best_move != False:          #定石が打てればそれを返す
            print(*best_move)
            nu_move += 1
            continue
        else :                          #定石が打てなければアルファベータ法により最善手を決める
            best_score, best_move = data.alphabeta(3)
            print(*best_move)
            break


#5手目以降はアルファベータにより最善手を決める
while True:
    data = make_player(player)
    finish = data.input_information(list(map(int,input().split())))     #盤面を読み込む
    if finish == 'finish': break                 #勝負がついていればその時点で終了させる
    best_score, best_move = data.alphabeta(3)        #アルファベータ法により最善手の決定を行う
    print(*best_move)                                #最善手を返す


"""
cd softexp
python3 server.py -1 greedy_player.py -2 make_player.py
python3 server.py -1 make_player.py -2 greedy_player.py
python3 server.py -1 greedy_player.py -2 make_player.py -r 50
"""