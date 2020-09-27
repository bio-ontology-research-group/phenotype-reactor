all: deepwalk

deepwalk: deepwalk.cc
	g++ -Ofast -funroll-loops -I. -Wall -std=c++0x deepwalk.cc -o deepwalk -lboost_thread-mt -lboost_system -lpthread
