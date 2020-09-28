#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <map>
#include <set>
#include <bitset>
#include <pthread.h>
#include <fstream>
#include <climits>
#include <random>
#include <algorithm>
#include <unordered_set>
#include <unordered_map>
#include <boost/threadpool.hpp>
#include <cstring>
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>

#define NUM_NODES 100000//0
#define BUFFERSIZE 512
#define THREADS 32

#define NUMBER_WALKS 100
#define LENGTH_WALKS 20

using namespace std;
using namespace boost::threadpool;


struct Edge {
  unsigned int edge ;
  unsigned int node ;
} ;

unordered_map<unsigned int, vector<Edge>> graph ;

random_device rd;
mt19937 rng(rd());
uniform_int_distribution<int> uni(0,INT_MAX);


ofstream fout;
boost::mutex mtx;

int num_nodes = NUM_NODES;
int threads = THREADS;
int number_walks = NUMBER_WALKS;
int length_walks = LENGTH_WALKS;


void build_graph(string fname) {
  char buffer[BUFFERSIZE];
  graph.reserve(NUM_NODES) ;
  ifstream in(fname);
  cout << "ifstreaming";
  while(in) {
    in.getline(buffer, BUFFERSIZE);
    if(in) {
      Edge e ;
      unsigned int source = atoi(strtok(buffer, " "));
      e.node = atoi(strtok(NULL, " ")) ;
      e.edge = atoi(strtok(NULL, " ")) ;
      graph[source].push_back(e) ;
    }
  }
}

void walk(unsigned int source) {
  vector<vector<unsigned int>> walks(number_walks) ;
  if (graph[source].size()>0) { // if there are outgoing edges at all
    for (int i = 0 ; i < number_walks ; i++) {
      int count = length_walks ;
      int current = source ;
      walks[i].push_back(source) ;
      while (count > 0) {
	if (graph[current].size() > 0 ) { // if there are outgoing edges
	  unsigned int r = uni(rng) % graph[current].size();
	  Edge next = graph[current][r] ;
	  int target = next.node ;
	  int edge = next.edge ;
	  walks[i].push_back(edge) ;
	  walks[i].push_back(target) ;
	  current = target ;
	} else {
	  int edge = INT_MAX ; // null edge
	  current = source ;
	  walks[i].push_back(edge) ;
	  walks[i].push_back(current) ;
	}
	count-- ;
      }
    }
  }
  stringstream ss;
  for(vector<vector<unsigned int>>::iterator it = walks.begin(); it != walks.end(); ++it) {
    for(size_t i = 0; i < (*it).size(); ++i) {
      if(i != 0) {
	ss << " ";
      }
      ss << (*it)[i];
    }
    ss << "\n" ;
  }
  mtx.lock() ;
  fout << ss.str() ;
  fout.flush() ;
  mtx.unlock() ;
}

void generate_corpus() {
  pool tp(threads);
  for ( auto it = graph.begin(); it != graph.end(); ++it ) {
    unsigned int source = it -> first ;
    tp.schedule(boost::bind(&walk, source ) ) ;
  }
  cout << tp.pending() << " tasks pending." << "\n" ;
  tp.wait() ;
}

int main (int argc, char *argv[]) {
  cout << "Building graph from " << argv[1] << "\n";
  build_graph(argv[1]);
  num_nodes = graph.size();
  cout << "Number of nodes in graph: " << num_nodes << "\n" ;
  cout << "Writing walks to " << argv[2] << "\n" ;

  if (argc > 3) {
    number_walks = strtol(argv[3], nullptr, 0);
  }
  if (argc > 4) {
    length_walks = strtol(argv[4], nullptr, 0);
  }
  if (argc > 5) {
    threads = strtol(argv[5], nullptr, 0);
  }

  cout << "Number of walks to " << number_walks << "\n" ;
  cout << "Walk length to " << length_walks << "\n" ;
  cout << "Threads to " << threads << "\n" ;
  fout.open(argv[2]) ;
  generate_corpus() ;
  fout.close() ;
}
