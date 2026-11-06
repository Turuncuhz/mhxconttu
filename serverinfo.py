import app
import localeInfo
from constInfo import TextColor

SERVER_ADI = "Lucifer2"
DISCORD_LINK = "https://discord.gg/Lucifer2"

app.ServerName = None
AUTH = [30001, 30003, 30005]
CH1 = [30007, 30009, 30011, 30013]
CH2 = [30015, 30017, 30019, 30021]
CH3 = [30023, 30025, 30027, 30029]
CH4 = [30031, 30033, 30035, 30037]
CH5 = [30039, 30041, 30043, 30045]
CH6 = [30047, 30049, 30051, 30053]
CH7 = [30055, 30057, 30059, 30061]
CH8 = [30063, 30065, 30067, 30069]
CH9 = [30071, 30073, 30075, 30077]
CH10 = [30079, 30081, 30083, 30085]

def GetChannel(channel):
	return channel[app.GetRandom(0, len(channel) - 1)]

SRV1 = {
	"name":"Lucifer2",
	"host":"45.150.149.254",
	"auth1":GetChannel(AUTH),
	"ch1":GetChannel(CH1),
	"ch2":GetChannel(CH2),
	"ch3":GetChannel(CH3),
	"ch4":GetChannel(CH4),
	"ch5":GetChannel(CH5),
	"ch6":GetChannel(CH6),
	"ch7":GetChannel(CH7),
	"ch8":GetChannel(CH8),
	"ch9":GetChannel(CH9),
	"ch10":GetChannel(CH10),
}
SRV2 = {
	"name":"Lucifer2 Beta",
	"host":"185.128.112.229",
	"auth1":GetChannel(AUTH),
	"ch1":GetChannel(CH1),
}

SRV_DICT = { 1 : SRV1, 2 : SRV2 }

STATE_NONE = localeInfo.CHANNEL_STATUS_OFFLINE

STATE_DICT = {
	0 : localeInfo.CHANNEL_STATUS_OFFLINE,
	1 : localeInfo.CHANNEL_STATUS_RECOMMENDED,
	2 : localeInfo.CHANNEL_STATUS_BUSY,
	3 : localeInfo.CHANNEL_STATUS_FULL,
}

SERVER1_CHANNEL_DICT = {
	0:{"key":10,"name":TextColor("CH-1", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch1"],"udp_port":SRV1["ch1"],"state":STATE_NONE,},
	1:{"key":11,"name":TextColor("CH-2", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch2"],"udp_port":SRV1["ch2"],"state":STATE_NONE,},
	2:{"key":12,"name":TextColor("CH-3", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch3"],"udp_port":SRV1["ch3"],"state":STATE_NONE,},
	3:{"key":13,"name":TextColor("CH-4", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch4"],"udp_port":SRV1["ch4"],"state":STATE_NONE,},
	4:{"key":14,"name":TextColor("CH-5", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch5"],"udp_port":SRV1["ch5"],"state":STATE_NONE,},
	5:{"key":15,"name":TextColor("CH-6", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch6"],"udp_port":SRV1["ch6"],"state":STATE_NONE,},
	6:{"key":16,"name":TextColor("CH-7", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch7"],"udp_port":SRV1["ch7"],"state":STATE_NONE,},
	7:{"key":17,"name":TextColor("CH-8", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch8"],"udp_port":SRV1["ch8"],"state":STATE_NONE,},
	8:{"key":18,"name":TextColor("CH-9", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch9"],"udp_port":SRV1["ch9"],"state":STATE_NONE,},
	9:{"key":19,"name":TextColor("CH-10", "FFffFF"),"ip":SRV1["host"],"tcp_port":SRV1["ch10"],"udp_port":SRV1["ch10"],"state":STATE_NONE,},
}

SERVER2_CHANNEL_DICT = {
	0:{"key":10,"name":TextColor("CH-1", "FFffFF"),"ip":SRV2["host"],"tcp_port":SRV2["ch1"],"udp_port":SRV2["ch1"],"state":STATE_NONE}
}

REGION_NAME_DICT = {0:""}

REGION_AUTH_SERVER_DICT = {
	0:{
		1:{"ip":SRV1["host"],"port":SRV1["auth1"]},
		2:{"ip":SRV2["host"],"port":SRV2["auth1"]},
	}
}

REGION_DICT = {
	0 : {
		1 : { "name" :SRV1["name"], "channel" : SERVER1_CHANNEL_DICT },
		2 : { "name" :SRV2["name"], "channel" : SERVER2_CHANNEL_DICT },
	},
}

MARKADDR_DICT = {
	10 : { "ip" : SRV1["host"], "tcp_port" : SRV1["ch1"], "mark" : "10.tga", "symbol_path" : "10" },
	20 : { "ip" : SRV2["host"], "tcp_port" : SRV2["ch1"], "mark" : "20.tga", "symbol_path" : "20" },
}
