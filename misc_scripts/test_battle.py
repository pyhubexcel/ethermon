import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../'))

from etheremon_lib.monster_config import MONSTER_CLASS_STATS, MONSTER_AGAINST_CONFIG
import copy


class BattleResult(object):
    A_WIN = 1
    B_WIN = 2


DEF_PER = 1
ATK_BUFF = 1.5
DEF_BUFF = 1
NO_OF_TURNS = 10


def run_single_battle(monster_a, monster_b):

    is_a_better = False
    is_b_better = False
    for type_a in monster_a['types']:
        for type_b in monster_b['types']:
            if MONSTER_AGAINST_CONFIG[type_a] == type_b:
                is_a_better = True
            if MONSTER_AGAINST_CONFIG[type_b] == type_a:
                is_b_better = True

    if is_a_better:
        monster_a['stats'][1] = int(monster_a['stats'][1] * ATK_BUFF)
        monster_a['stats'][3] = int(monster_a['stats'][3] * ATK_BUFF)
        monster_a['stats'][2] = int(monster_a['stats'][2] * DEF_BUFF)
        monster_a['stats'][4] = int(monster_a['stats'][4] * DEF_BUFF)

    if is_b_better:
        monster_b['stats'][1] = int(monster_b['stats'][1] * ATK_BUFF)
        monster_b['stats'][3] = int(monster_b['stats'][3] * ATK_BUFF)
        monster_b['stats'][2] = int(monster_b['stats'][2] * DEF_BUFF)
        monster_b['stats'][4] = int(monster_b['stats'][4] * DEF_BUFF)

    a_attack_first = bool(monster_a['stats'][5] > monster_b['stats'][5])

    for turn in xrange(1, NO_OF_TURNS + 1):
        is_a_turn = ((turn % 2 == 1) == a_attack_first)
        if is_a_turn:
            dam1 = max(10, monster_a['stats'][1] - int(monster_b['stats'][2] * DEF_PER))
            dam2 = max(10, monster_a['stats'][3] - int(monster_b['stats'][4] * DEF_PER))
            monster_b['stats'][0] -= max(dam1, dam2, 0)
            if monster_b['stats'][0] < 0:
                return BattleResult.A_WIN
        else:
            dam1 = max(10, monster_b['stats'][1] - int(monster_a['stats'][2] * DEF_PER))
            dam2 = max(10, monster_b['stats'][3] - int(monster_a['stats'][4] * DEF_PER))
            monster_a['stats'][0] -= max(dam1, dam2, 0)
            if monster_a['stats'][0] < 0:
                return BattleResult.B_WIN

    if monster_b['stats'][0] < monster_a['stats'][0]:
        return BattleResult.A_WIN
    else:
        return BattleResult.B_WIN


def run_battle_simulation(class_a, level_a, class_b, level_b):
    monster_a = copy.deepcopy(class_a)
    monster_b = copy.deepcopy(class_b)
    for index in xrange(0, 6):
        monster_a['stats'][index] = monster_a['stats'][index] + (level_a - 1) * monster_a['steps'][index] * 3
        monster_b['stats'][index] = monster_b['stats'][index] + (level_b - 1) * monster_b['steps'][index] * 3
    return run_single_battle(monster_a, monster_b)


def run_single_class_test(monster_class_info):
    total_win = 0
    wins = []
    for level in xrange(1, 101, 20):
        win_count = 0
        lost_to = []
        for class_id in MONSTER_CLASS_STATS:
            opp_class = MONSTER_CLASS_STATS[class_id]
            result = run_battle_simulation(monster_class_info, level, opp_class, level)
            if result == BattleResult.A_WIN:
                win_count += 1
            else:
                lost_to.append(class_id)
        wins.append(win_count)
        print "level: ", level, " - win: ", win_count
        print "lost to: ", lost_to
    return wins


def run_all_class_test():
    for level in xrange(1, 101, 20):
        win_list = []
        for class_id in MONSTER_CLASS_STATS:
            win_count = 0
            for class_id_opp in MONSTER_CLASS_STATS:
                result = run_battle_simulation(MONSTER_CLASS_STATS[class_id], level, MONSTER_CLASS_STATS[class_id_opp], level)
                if result == BattleResult.A_WIN:
                    win_count += 1
            win_list.append({
                'win_count': win_count,
                'class_id': class_id
            })
        win_list = sorted(win_list, key=lambda win: -win['win_count'])
        print "At Level: ", level
        for i in xrange(0, 10):
            print "Class ", win_list[i]['class_id'], " win against ", win_list[i]['win_count'], " classes."


def run_test():
    # class_id = 100
    # run_single_class_test(MONSTER_CLASS_STATS[class_id])
    run_all_class_test()


if __name__ == "__main__":
    run_test()