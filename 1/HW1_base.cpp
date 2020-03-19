#include<iostream>
#include<pthread.h>
#include<unistd.h>
#include<fstream>
#define MAX 1

using namespace std;

int clk;
int k;
int g;
int G;
int a[MAX];


pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;

class Player{
public:

	int id;
	int m_id;

	int arrive_time;
	int c_play_round;
	int rest_time;
	int total_play_round;
	
	int state;//playing:1,not play:0 
	int round_num;//n-th round
	int rest_t_num;
	int c_round_num;
	int prize;
	int wait;

	int wanttoplay(){
		if(prize!=1 && clk>=arrive_time ){
			if(state==1){
				rest_t_num=0;
				if(c_round_num < c_play_round && g<G && round_num < total_play_round){
					c_round_num++;
					round_num++;
					k--;
					g++;
					a[m_id]=1;

					return 0;
				}
				else {
					/**/
					cout<<clk<<" "<<id<<" "<<"finish playing";
					if(round_num==total_play_round||g>=G){
						g=0;
						cout<<" YES";
						prize=1;
					}
					else cout<<" NO";
					cout<<endl;
					a[m_id]=0;
					m_id=0;
					state=0;
					c_round_num=0;
					rest_t_num ++;
					return 0;
					/**/
				}
			}
			else{
				c_round_num=0;
				if(rest_t_num < rest_time){
					rest_t_num ++;
					return 0;
				}
				else
					return 1;
			}
		}
		return 0;
	};//0cant 1ok
};


/*************/
static void *play_pth(void* temp){

	Player* player = (Player*) temp;
	
	if(k>0){
		pthread_mutex_lock( &mutex1 );
		k--;
		pthread_mutex_unlock( &mutex1 );
		player->round_num++;
		player->c_round_num++;
//		cout<<player->id<<" "<<player->round_num<<endl;
		if(player->state==0){
			for(int i=0;i<MAX;i++)
				if(a[i]==0){ 
					a[i]=1;
					player->m_id=i;
					break;
				}
			cout<<clk<<" "<<player->id<<" "<<"start playing"<<endl;
		}
		player->state=1;
		g++;
		player->wait=1;
	}
	else{
		if(player->wait!=0)
			cout<<clk<<" "<<player->id<<" "<<"wait in line\n";
		player->wait=0;
		player->state=0;
	}
	pthread_exit(NULL);
}
/*************/


int main(int argc,char ** argv)
{
	int player_num;
	int i;
	
	ifstream fin;
	
	fin.open(argv[1],ios::in);
	
	fin>>G>>player_num;

	Player id[player_num+1];
	int o[player_num+1];
	pthread_t t[player_num]; // 宣告 pthread 變數
     // 建立子執行緒

	for( i=1 ; i<player_num+1 ; i++){
		fin>>id[i].arrive_time
		   >>id[i].c_play_round
		   >>id[i].rest_time
		   >>id[i].total_play_round;	
		id[i].id=i;
		id[i].m_id=-1;
		id[i].state=0;
		id[i].round_num=0;
		id[i].prize=0;
		id[i].rest_t_num=id[i].rest_time;
		id[i].c_round_num=0;
		id[i].wait=1;
	}

	clk = 0;

	while(clk < 50){
		//cout<<clk<<"****"<<endl;
		
		k=MAX;
		
		for(i=1;i<player_num+1;i++){
			if(id[i].wanttoplay()==1){
				pthread_create( &t[i-1] , NULL, play_pth , &id[i] );
				//pthread_join(t[i-1], NULL);
				o[i]=1;
			}
		}
		for(i=1;i<player_num+1;i++)
			if(o[i]==1)
				pthread_join(t[i-1], NULL);
		
		if(k==MAX) g=0;
		sleep(0.1);
		clk++;
	}
	return 0;
}
