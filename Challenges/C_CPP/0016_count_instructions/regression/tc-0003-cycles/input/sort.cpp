
#include <cstdlib>
#include <vector>

void sort(std::vector<int>& list)
{

     for (size_t i = 0; i < list.size(); i++){
        for (size_t j = 0; j < list.size()-1; j++){
            if (list[j]>list[j+1] ){
               std::swap(list[j], list[j+1]);
            }

        }
    }
}

