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




ItemClassConfigGetDataSchema = {
	"type": "object",
	"properties": {
		"id":UInt32Schema,
	},	
	"required": []

}


ItemWipGetDataSchema = {
	"type": "object",
	"properties": {
		"address": {"type": "string"},
	},
	"required": ["address"],
}

EthermonWildGetDataSchema = {
	"type": "object",
	"properties": {
		"address": {"type": "string"},
	},
	"required": ["address"],
}

UserFungibleGetDataSchema = {
	"type": "object",
	"properties": {
		"address": {"type": "string"},
	},
	"required": ["address"],
}
UserFungibleUpdateQtySchema = {
	"type": "object",
	"properties": {
		"meta_id": UInt32Schema,
		"host_id": UInt32Schema,
		"qty": UInt32Schema,
		"dcl_fungible_id": UInt32Schema,
	},
	"required": ['dcl_fungible_id',"qty"],
}

ItemWIPUpdateSchema = {
	"type": "object",
	"properties": {
		"dcl_item_id": UInt32Schema,
		"Mon_ID": UInt32Schema,
	},
	"required": ['dcl_item_id', 'Mon_ID'],
}

MonsterDataGetDataSchema = {
	"type": "object",
	"properties": {
		"id":UInt32Schema,
	},
	"required": ["id"],
}
UserActiveStatusGetDataSchema = {
	"type": "object",
	"properties": {
		"address": {"type": "string"},
		"Mon_ID": {"type": "string"},
	},
	"required": ["address", "Mon_ID"],
}

PurchaseCallbackSchema = {
	"type": "object",
	"properties": {
		"action": {"type": "string"},
		"meta_id": {"type": "string"},
		"host_id": {"type": "string"},
		"plot_unique": {"type": "string"},
		"txn_token": {"type": "string"},
		"eth_from": {"type": "string"},
		"dcl_name": {"type": "string"},
		"sku": {"type": "string"},
		"create_date":Int32Schema,
	},
	"required": ["action", "meta_id", "host_id", "plot_unique", "txn_token", "eth_from", "dcl_name", "sku", "create_date"]
}

DCLUserLoginSchema = {
	"type": "object",
	"properties": {
		"address": {"type": "string"},
		#"a0": Int32Schema,
	},
	"required": ["address"]
}

ConsumeUserFungibleSchema = {
	"type": "object",
	"properties": {
		"dcl_user_fungible": Int32Schema,
	},
	"required": ["dcl_user_fungible"]
}

MonIDSchema = {
	"type": "object",
	"properties": {
		"Mon_ID": Int32Schema,
	},
	"required": ["Mon_ID"]
}


UserFungibleUpdateQtySchema = {
	"type": "object",
	"properties": {
		# "address": {"type": "string"},
		# "ItemClass": {"type": "string"},
		# "ItemVariety": {"type": "string"},
		"qty": UInt32Schema,
		"dcl_fungible_id": UInt32Schema,
	},
	"required": ['dcl_fungible_id',"qty"],
}
