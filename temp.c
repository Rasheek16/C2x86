int main(void) {
    int x;
    int *arr[1] = {&x};
    int *(*array_of_pointers[1])[1] = {&arr};
    return array_of_pointers[0] != (int*(*)[1])arr; 
}