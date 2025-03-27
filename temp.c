int main(void) {
    int arr[2] = {1, 2};
    
    // 1. Pointer-to-array
    int(*ptr_to_arr)[2] = &arr;
    
    // 2. Cast to long (like original test)
    long ptr_as_long = (long)ptr_to_arr;
    
    // 3. Cast back to pointer-to-array 
    int(*roundtrip_ptr)[2] = (int(*)[2])ptr_as_long;
    
    // 4. Compare
    return roundtrip_ptr == ptr_to_arr; // MUST return 1
} 