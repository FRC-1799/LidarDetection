HOME_TREE := ../../Downloads/rplidar_sdk-master

MODULE_NAME := $(notdir $(HOME_TREE))

include $(HOME_TREE)/mak_def.inc

CXXSRC += main.cpp
#C_INCLUDES += -I$(HOME_TREE)/../../sdk/include -I$(HOME_TREE)/../../sdk/src

EXTRA_OBJ := 
LD_LIBS += -lstdc++ -lpthread

all: build_app

include $(HOME_TREE)/mak_common.inc

clean: clean_app