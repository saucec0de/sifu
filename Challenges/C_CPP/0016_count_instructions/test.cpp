/*

 Copyright (c) Siemens AG, 2020
     tiago.gasiba@gmail.com

 SPDX-License-Identifier: MIT

*/
#include <iostream>
#include <ratio>
#include <string>
#include <fstream>
#include <string.h>
#include <iterator>
#include "sort.h"
#include <vector>
#include <ctime>
#include <algorithm>    // std::sort
#include "log.h"
#include "utils.h"
int   timerExpire(void)       { return 8;                                 } // make sure the program exits...
char *timerErrorMessage(void) { return "ERROR: Too long time to process"; }
char *timerTag(void)          { return "NO_TAG";                          }


int random_len = 4;
const char* vector_file = "./vector.txt";

std::vector<int> generate_random_vector(int len){
    int random_integer = rand()%2000 - 1000; 
    std::vector<int> a;
    for(int i = 0; i < len; i++){
        random_integer = rand()%2000 - 1000; 
        a.push_back(random_integer);
    }
    return a;
}

void f(std::vector<int> & a){
        sort(a);
}

void printVector(const std::vector<int> & a){
    char print[100];
    for(int i = 0; i < a.size(); i++){
        char buf[16]; // need a buffer for conversion
        sprintf(buf, "%d", a[i]);
        strncat(print, buf, sizeof(buf));
        if(i < a.size() - 1)
            strncat(print,", ", 2);
    }
    print[0] = ' ';
    logger(print);
}
//Functional test
void test_1(){
    int r = 0;
    int random_len = rand()%10 + 2;
    std::vector<int> v1 = generate_random_vector(random_len);    
    std::vector<int> v2 = v1;
    std::sort(v2.begin(), v2.end());
    std::sort( v1.begin(), v1.end(), std::greater<int>());
    try{
        f(v1);
        if( equal(v1.begin(), v1.end(), v2.begin()) )
            r = 1;
    }
    catch(...){
        //do smth
    }
    testResult(r,"TEST_100","Is it sorting correctly?","","","SORTING");
}
void writeFile (std::vector<int> v) {
    std::ofstream output_file(vector_file,std::fstream::app);
    std::ostream_iterator<int> output_iterator(output_file, " ");
    std::copy(v.begin(), v.end(), output_iterator);
}

std::vector<int> readFile(int start_pos,int len) {
  std::ifstream is(vector_file);
  std::istream_iterator<int> start(is), end;
  std::vector<int> numbers(start, end);
  std::vector<int> v(4);

  std::copy(numbers.begin() + start_pos, numbers.begin() + len, v.begin());
  return v;
}

void check_vector_file(){
    std::ifstream output_file_check;
    output_file_check.open(vector_file,std::fstream::app);
    if(output_file_check.peek() == std::ifstream::traits_type::eof()){
        writeFile(generate_random_vector(random_len));
        writeFile(generate_random_vector(random_len));
        writeFile(generate_random_vector(random_len));
    }
}
int main() {
    srand((unsigned)time(0)); 
    enableLoggingFunction = 1;

    //Functional tests
    test_1();
    
    
    check_vector_file();

    std::vector<int> v1 = readFile(0,random_len);
    std::vector<int> v2 = readFile(random_len, 2*random_len);
    std::vector<int> v3 = readFile(2*random_len, 3*random_len);

    logger("Sort vector v1: \n");
    printVector(v1);
    f(v1);
    logger("Sorted vector v1: ");
    printVector(v1);
    logger("-------------------");

    logger("Sort vector v2: ");
    printVector(v2);
    f(v2);
    logger("Sorted vector v2: ");
    printVector(v2);
    logger("-------------------");

    logger("Sort vector v3: ");
    printVector(v3);
    f(v3);
    logger("Sorted vector v3: ");
    printVector(v3);
    logger("-------------------");


    return 0;
}
