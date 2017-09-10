#include<stdio.h>
#include<bits/stdc++.h>
#include<iostream>
#include<cstring>
#include<fstream>
#include<sstream>

using namespace std;

int num_blocks;
vector<ifstream* > fPointers;
string output_file;
int memory_size;
int save_buffer = 1024;

class CompareDist {
    public:
        bool operator()(pair<vector<string>, int>& p1, pair<vector<string>, int>& p2) {
            vector<string> a = p1.first;
            vector<string> b = p2.first;
            if(a > b) {
                return true;
            }
            else {
                return false;
            }
        }
};

priority_queue<pair<vector<string>, int>, vector<pair<vector<string>, int> >, CompareDist> myheap;

void mergeFiles() {
    int noSplits = num_blocks;
    int OB = 0.2 * (double)memory_size;
    // cout << "memory_size: " << memory_size << endl;
    // cout << "OB: " << OB << endl;
    int nOB = OB*1024*1024;
    // cout << "nOB: " << nOB << endl;
    int nF = ((double)((memory_size-OB)/noSplits))*1024*1024;
    // cout << "nF: " << nF << endl;

    // Store all file pointers in an array
    for(int i=0; i<noSplits; i++) {
        ifstream *file = new ifstream(("index/file" + to_string(i)).c_str());
        fPointers.push_back(file);
    }

    ifstream *f;
    string line;
    vector<string> record;
    int cnt;

    for(int i=0; i<noSplits; i++) {
        f = fPointers[i];
        cnt = 0;
        cout << "Reading from intermediate file" + to_string(i) << endl;
        while(getline(*f, line)) {
            cnt += line.size();
            vector<string> tokens;
            stringstream ss(line);
            string item;
            int cnt_item = 0;
            while (getline(ss, item, '|')) {
                if(cnt_item == 0) {
                    int i;
                    for(i=0; i<item.size(); i++) {
                        if(item[i] == ':') {
                            break;
                        }
                    }
                    tokens.push_back(item.substr(0, i));
                    tokens.push_back(item.substr(i+1, item.size()));
                }
                else {
                    if(item.size() != 0) {
                        tokens.push_back(item);
                    }
                }
                cnt_item++;
            }
            myheap.push(make_pair(tokens, i));
            if (cnt >= nF-save_buffer) {
                break;
            }
        }
    }

    int cntOB = 0;
    ofstream outFile;
    outFile.open(output_file);
    string str_rec;
    pair<vector<string>, int> ele;
    vector<vector<string> > record_buff;

    while(!myheap.empty()) {
        ele = myheap.top();
        vector<string> tep = ele.first;
        //cout << tep[0] << " " << tep[1] << " " << tep[2] << endl;
        myheap.pop();
        // push record to output buffer
        record_buff.push_back(ele.first);
        int cnt_item = 0;
        if (getline(*fPointers[ele.second], line)) {
            vector<string> tokens;
            stringstream ss(line);
            string item;
            int cnt_item = 0;
            while (getline(ss, item, '|')) {
                if(cnt_item == 0) {
                    int i;
                    for(i=0; i<item.size(); i++) {
                        if(item[i] == ':') {
                            break;
                        }
                    }
                    tokens.push_back(item.substr(0, i));
                    tokens.push_back(item.substr(i+1, item.size()));
                }
                else {
                    if(item.size() != 0) {
                        tokens.push_back(item);
                    }
                }
                cnt_item++;
            }
            myheap.push(make_pair(tokens, ele.second));
        }
        cntOB += line.size();
        if (cntOB >= nOB-save_buffer) {
            // output buffer is full
            // put records to file
            for(int i=0; i<record_buff.size(); i++) {;
                str_rec = record_buff[i][0];
                for(int j=1; j<record_buff[i].size(); j++) {
                    str_rec += " " + record_buff[i][j];
                }
                str_rec += "\n";
                outFile << str_rec;
            }
            // clear Buffer
            cntOB = 0;
            record_buff.erase(record_buff.begin(), record_buff.end());
        }
    }

    if (cntOB < nOB) {
        for(int i=0; i<record_buff.size(); i++) {
            str_rec = record_buff[i][0];
            for(int j=1; j<record_buff[i].size(); j++) {
                str_rec += " " + record_buff[i][j];
            }
            str_rec += "\n";
            outFile << str_rec;
        }
        // clear Buffer
        cntOB = 0;
        record_buff.erase(record_buff.begin(), record_buff.end());
    }

    for(int i=0; i<noSplits; i++) {
        delete fPointers[i];
    }
    fPointers.erase(fPointers.begin(), fPointers.end());
    outFile.close();
}

int main(int argc, char* argv[]) {
    output_file = "finalindex.txt";
    memory_size = 10;

    num_blocks = stoi(argv[1]);

    mergeFiles();

    return 0;
}