from common.form_validator import extend_form_schema
from etheremon_lib.constants import *

UInt8Schema = {"type": "integer", "minimum": 0, "maximum": TYPE_UINT8_MAX}
UInt16Schema = {"type": "integer", "minimum": 0, "maximum": TYPE_UINT16_MAX}
UInt32Schema = {"type": "integer", "minimum": 0, "maximum": TYPE_UINT32_MAX}
Int32Schema = {"type": "integer", "minimum": TYPE_INT32_MIN, "maximum": TYPE_INT32_MAX}
UInt64Schema = {"type": "integer", "minimum": 0, "maximum": TYPE_UINT64_MAX}
UFloatSchema = {"type": "number", "minimum": 0}
DoubleSchema = {"type": "number"}
StringSchema = {"type": "string"}
BooleanSchema = {"type": "boolean"}

'''
GetTrainerBalanceSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string", "minimum": 42, "maximum": 42}
	},
	"required": ["trainer_address"]
}
'''

# General API
GeneralGetClassMetadataSchema = {
	"type": "object",
	"properties": {
		"class_ids": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt32Schema
		}
	},
	"required": ["class_ids"]
}

# User API
UserSubscribeForm = {
	"type": "object",
	"properties": {
		"email_address": {"type": "string"},
		"type": UInt32Schema
	},
	"required": ["email_address"]
}

UserGetMonsterDexSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"metamask_flag": UInt32Schema
	},
	"required": ["trainer_address"]
}

UserGetSoldMonsterSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

UserGetInfoSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

UserUpdateInfoSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"email": {"type": "string", "minimum": 5, "maximum": 64},
		"username": {"type": "string", "minimum": 6, "maximum": 64},
		"refer_code": {"type": "string"},
	},
	"required": ["trainer_address", "email", "username"]
}

ClaimLadderRankSchema = {
	"type": "object",
	"properties": {
		"player_id": UInt32Schema,
	},
	"required": ["player_id"]
}

UserGetLadderInfoSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

UserSyncDatachema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"site_id": UInt32Schema,
		"token_id": UInt32Schema
	},
	"required": ["trainer_address"]
}

ClaimReferRewardSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"claim_timestamp": UInt32Schema,
		"signature": {"type": "string"},
	},
	"required": ["trainer_address", "signature", "claim_timestamp"]
}

ClaimRewardSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"reward_id": UInt32Schema,
	},
	"required": ["trainer_address", "reward_id"],
}

GetRewardSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

MarkSocialShareSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"facebook": UInt8Schema,
		"twitter": UInt8Schema
	},
	"required": ["trainer_address"]
}

# Monster API
MonsterGetDataSchema = {
	"type": "object",
	"properties": {
		"monster_ids": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": Int32Schema
		}
	},
	"required": ["monster_ids"]
}

# Castle API
CastleGetBattleLogSchema = {
	"type": "object",
	"properties": {
		"battle_ids": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt64Schema
		}
	},
	"required": ["battle_ids"]
}

# Battle API
BattlePracticeBattleSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"castle_ids": {
			"type": "array",
			"minItems": CASTLE_BATCH_SIZE,
			"maxItems": CASTLE_BATCH_SIZE,
			"items": UInt32Schema
		},
		"monster_ids": {
			"type": "array",
			"minItems": CASTLE_ATTACK_TEAM_SIZE,
			"maxItems": CASTLE_ATTACK_TEAM_SIZE,
			"items": UInt32Schema
		}
	},
	"required": ["trainer_address", "castle_ids", "monster_ids"]
}

BattleGetPracticeLogSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

# Ladder
BattleGetCastleSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

BattleAttackCastleSchema = {
	"type": "object",
	"properties": {
		"attacker_player_id": UInt32Schema,
		"defender_player_id": UInt32Schema,
		"player_token": {"type": "string"}
	},
	"required": ["attacker_player_id", "defender_player_id", "player_token"]
}

BattleGetBattleLogSchema = {
	"type": "object",
	"properties": {
		"player_id": UInt32Schema
	},
	"required": ["player_id"]
}

BattleGetPracticePlayersSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"avg_bp":  UInt32Schema,
		"avg_level": UInt32Schema
	},
	"required": ["trainer_address"]
}

BattlePracticeSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"player_tokens": {
			"type": "array",
			"minItems": CASTLE_BATCH_SIZE,
			"maxItems": CASTLE_BATCH_SIZE,
			"items": {"type": "string"}
		},
		"monster_ids": {
			"type": "array",
			"minItems": CASTLE_ATTACK_TEAM_SIZE,
			"maxItems": CASTLE_ATTACK_TEAM_SIZE,
			"items": UInt32Schema
		}
	},
	"required": ["trainer_address", "player_tokens", "monster_ids"]
}

BattleGetPracticeHistorySchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"]
}

# User API
GetWithPagingSchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
		"page_size": UInt32Schema
	},
	"required": ["page_id", "page_size"]
}

# User API
GetMarketHistorySchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
		"page_size": UInt32Schema,
		"class_id": UInt32Schema,
		"sort_by": StringSchema
	},
	"required": ["page_id", "page_size"]
}

# # User API
# GetMarketHistorySchema = {
# 	"type": "object",
# 	"properties": {
# 		"page_id": UInt32Schema,
# 		"page_size": UInt32Schema,
#
# 	},
# 	"required": ["page_id", "page_size"]
# }

NewPlayerCountSchema = {
	"type": "object",
	"properties": {
		"period_in_sec": UInt32Schema
	},
	"required": []
}

# Trading
TradingGetLendingListSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"]
}


# Offchain

EmaBattleGetUserStatsSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"current_block_time": UInt32Schema
	},
	"required": ["trainer_address"]
}

EmaBattleGetRankCastlesSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

EmaBattleSetRankTeamSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"team": {
			"type": "array",
			"minItems": CASTLE_ATTACK_TEAM_SIZE,
			"maxItems": CASTLE_ATTACK_TEAM_SIZE,
			"items": Int32Schema
		}
	}
}

EmaBattleAttackRankCastleSchema = {
	"type": "object",
	"properties": {
		"attacker_player_id": UInt32Schema,
		"defender_player_id": UInt32Schema,
		"attack_count": UInt32Schema
	},
	"required": ["attacker_player_id", "defender_player_id"]
}

EmaBattleGetRankHistorySchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

EmaBattleGetRankBattleSchema = {
	"type": "object",
	"properties": {
		"battle_id": UInt32Schema,
	},
	"required": ["battle_id"]
}


EmaBattleGetPracticeCastlesSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"avg_level": UInt32Schema
	},
	"required": ["trainer_address", "avg_level"]
}

EmaBattleAttackPracticeCastleSchema = {
	"properties": {
		"trainer_address": {"type": "string"},
		"defender_player_id": UInt32Schema,
		"monster_ids": {
			"type": "array",
			"minItems": CASTLE_ATTACK_TEAM_SIZE,
			"maxItems": CASTLE_ATTACK_TEAM_SIZE,
			"items": Int32Schema
		},
		"attack_count": UInt32Schema
	},
	"required": ["trainer_address", "defender_player_id", "monster_ids"]
}

EmaBattleGetPracticeHistorySchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

EmaBattleClaimMonsterExpSchema = {
	"type": "object",
	"properties": {
		"monster_id": UInt32Schema
	},
	"required": ["monster_id"]
}

EmaBattleClaimWinRankSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

EmaBattleClaimTopRankSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

# Adventure API
AdventureGetItemDataSchema = {
	"type": "object",
	"properties": {
		"token_ids": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt64Schema
		}
	},
	"required": ["token_ids"]
}

AdventureGetMySitesSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

AdventureGetMyAdventureItemsSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

AdventureGetMyExploresSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

AdventureGetPendingExploreSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

AdventureGetAdventureStatsSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"}
	},
	"required": ["trainer_address"]
}

AdventureVoteSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"signature": {"type": "string"},
		"vote_timestamp": UInt32Schema,
		"explore_eth": {"type": "number", "minimum": 0.001, "maximum": 1},
		"explore_emont": {"type": "number", "minimum": 1, "maximum": 100},
		"challenge_eth": {"type": "number", "minimum": 0.001, "maximum": 1},
		"challenge_emont": {"type": "number", "minimum": 1, "maximum": 100}
	},
	"required": ["trainer_address", "signature", "vote_timestamp", "explore_eth", "explore_emont", "challenge_eth", "challenge_emont"]
}

AdventureCountItemSchema = {
	"type": "object",
	"properties": {
		"item_classes": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt32Schema
		}
	},
	"required": ["item_classes"]
}


# Quest API
QuestGetPlayerQuestsSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"quest_type": UInt8Schema,
	},
	"required": ["trainer_address", "quest_type"],
}

QuestClaimQuestSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"quest_id": UInt32Schema,
	},
	"required": ["trainer_address", "quest_id"],
}

QuestClaimAllSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

# Auth
AuthGetUserSessionForm = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

SignInForm = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"message": {"type": "string"},
		"signature": {"type": "string"},
	},
	"required": ["trainer_address", "message", "signature"],
}

SignOutForm = {
	"type": "object",
	"properties": {
	},
	"required": [],
}


# Event
LuckyDrawGetInfoForm = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

LuckyDrawSpinForm = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

LunarClaimAdventureForm = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

DexGetSpeciesSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
}


# /api/dex/get_monsters?page_id=1&page_size=28&types=13,4&gen=2&egg=2&forms=2&search=ewq&sort=-name&level=25,71&bp=16,59
DevGetMonsterSchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
		"page_size": {"type": "integer", "minimum": 1, "maximum": 30},
		"class_ids": {
			"type": "array",
			"minItems": 1,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt32Schema
		},
		"types": {
			"type": "array",
			"minItems": 1,
			"maxItems": 30,
			"delimiter": ",",
			"items": UInt32Schema
		},
		"egg": UInt32Schema,
		"gen": Int32Schema,
		"forms": {
			"type": "array",
			"minItems": 1,
			"maxItems": 30,
			"delimiter": ",",
			"items": UInt32Schema
		},
		"sort": {"type": "string"},
		"level": {
			"type": "array",
			"minItems": 1,
			"maxItems": 30,
			"delimiter": ",",
			"items": UInt32Schema
		},
		"bp": {
			"type": "array",
			"minItems": 1,
			"maxItems": 30,
			"delimiter": ",",
			"items": UInt32Schema
		},
		"search": {"type": "string"},
	},
	"required": ["page_id", "page_size"]
}

GetTopRank = {
	"type": "object",
	"properties": {
		"start_time": UInt32Schema,
		"end_time": UInt32Schema,
	},
	"required": ["start_time"]
}


AllEmaBattlesGetDataSchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
	},
	"required": ["page_id"]
}

EmaBattleGetDataSchema = {
	"type": "object",
	"properties": {
		"id":UInt32Schema,
	},
	"required": ["id"],
}

AllPlayersEnergyGetDataSchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
	},
	"required": ["page_id"]
}



PlayerEnergyGetDataSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}



AllPlayersRankGetDataSchema = {
	"type": "object",
	"properties": {
		"page_id": UInt32Schema,
	},
	"required": ["page_id"]
}



PlayerRankGetDataSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}

# Store API
StoreGetClassesSchema = {
	"type": "object",
	"properties": {
		"class_ids": {
			"type": "array",
			"minItems": 0,
			"maxItems": 100,
			"delimiter": ",",
			"items": UInt32Schema
		}
	},
	"required": []
}

RequestAddExpMonSchema = {
	"type": "object",
	"properties": {
		"monster_id": UInt32Schema,
		"exp": UInt32Schema,
	},
	"required": ["exp", "monster_id"],
}



RequestBurnMonSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"monster_id": UInt32Schema,
	},
	"required": ["trainer_address", "monster_id"],
}

ClaimOffchainMonsSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
	},
	"required": ["trainer_address"],
}


TournamentRegisterTeamSchema = {
	"type": "object",
	"properties": {
		"trainer_address": {"type": "string"},
		"tournament_id": Int32Schema,
		"team": {
			"type": "array",
			"minItems": CASTLE_ATTACK_TEAM_SIZE,
			"maxItems": CASTLE_ATTACK_TEAM_SIZE,
			"items": Int32Schema
		}
	},
	"required": ["trainer_address", "tournament_id", "team"]
}

TournamentGetInfoSchema = {
	"type": "object",
	"properties": {
		"tournament_id": Int32Schema,
		"trainer_address": {"type": "string"},
	},
	"required": []
}

DummySchema = {
	"type": "object",
	"properties": {},
	"required": [],
}


