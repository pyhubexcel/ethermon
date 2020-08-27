import random
from django.db.models import Q
from common.utils import get_timestamp
from etheremon_lib.models import *
from etheremon_lib.constants import *

def get_rank_data(player_id):
    return EtheremonDB.UserLadderTab.objects.filter(player_id=player_id).first()

def get_rank_data_by_address(trainer):
    return EtheremonDB.UserLadderTab.objects.filter(trainer=trainer).first()

def get_rank_data_list(from_index, to_index):
    return EtheremonDB.UserLadderTab.objects.order_by('-point')[from_index:to_index]

def count_rank_data_list():
    return EtheremonDB.UserLadderTab.objects.count()

def count_higher_point(point):
    return EtheremonDB.UserLadderTab.objects.filter(point__gt=point).count()

def get_defenders_by_point(point, player_id):
    greater_records = EtheremonDB.UserLadderTab.objects.filter(point__gte=point).filter(~Q(player_id=player_id)).order_by('point')[:10]
    lower_records = EtheremonDB.UserLadderTab.objects.filter(point__lt=point).filter(~Q(player_id=player_id)).order_by('-point')[:5]
    result_list = []
    for greater_record in greater_records:
        result_list.append(greater_record)
    for lower_record in lower_records:
        result_list.append(lower_record)
    random.shuffle(result_list)
    return result_list[:10]

def add_battle(defender_id, attacker_id, result, monster_data):
    current_ts = get_timestamp()
    record = EtheremonDB.BattleLadderTab(refer_id=0,defender_id=defender_id,attacker_id=attacker_id,
                                         defender_before_point=0,defender_after_point=0,attacker_before_point=0,
                                         attacker_after_point=0,result=result,monster_data=monster_data,
                                         status=LadderStatus.STATUS_INIT,create_time=current_ts, update_time=current_ts)
    record.save()
    return record

def get_battle_log(player_id):
    return EtheremonDB.BattleLadderTab.objects.filter(Q(defender_id=player_id) | Q(attacker_id=player_id)).filter(~Q(status=LadderStatus.STATUS_INIT)).order_by('-battle_id')[:10]

def get_complete_battle_log(player_id):
    return EtheremonDB.BattleLadderTab.objects.filter(Q(defender_id=player_id) | Q(attacker_id=player_id)).filter(status=LadderStatus.STATUS_COMPLETE).order_by('-refer_id')[:15]

def get_pending_battle_log(player_id):
    return EtheremonDB.BattleLadderTab.objects.filter(Q(defender_id=player_id) | Q(attacker_id=player_id)).filter(status=LadderStatus.STATUS_PENDING).order_by('-battle_id')[:5]

def get_practice_players(player_id, avg_bp):
    greater_records = EtheremonDB.UserLadderTab.objects.filter(avg_bp__gte=avg_bp).filter(~Q(player_id=player_id)).order_by('avg_bp')[:10]
    lower_records = EtheremonDB.UserLadderTab.objects.filter(avg_bp__lt=avg_bp).filter(~Q(player_id=player_id)).order_by('-avg_bp')[:10]
    result_list = []
    for greater_record in greater_records:
        result_list.append(greater_record)
    for lower_record in lower_records:
        result_list.append(lower_record)
    random.shuffle(result_list)
    return result_list

def get_practice_players_by_level(player_id, avg_level):
    greater_records = EtheremonDB.UserLadderTab.objects.filter(avg_level__gte=avg_level).filter(~Q(player_id=player_id)).order_by('avg_bp')[:10]
    lower_records = EtheremonDB.UserLadderTab.objects.filter(avg_level__lt=avg_level).filter(~Q(player_id=player_id)).order_by('-avg_bp')[:10]
    result_list = []
    for greater_record in greater_records:
        result_list.append(greater_record)
    for lower_record in lower_records:
        result_list.append(lower_record)
    random.shuffle(result_list)
    return result_list

def add_claim_rank(player_id, rank, point, create_time):
    claim_record = EtheremonDB.ClaimRankLadderTab(player_id=player_id, rank=rank, point=point, status=0, create_time=create_time)
    claim_record.save()
    return claim_record

def is_on_battle(monster_id):
    record = EtheremonDB.UserLadderTab.objects.filter(Q(a0=monster_id) | Q(a1=monster_id) |
                                                    Q(a2=monster_id) | Q(s0=monster_id) | Q(s1=monster_id) | Q(s2=monster_id)).first()
    return record is not None


