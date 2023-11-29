// #include<iostream>
// using namespace std;

int main() {

    int rows;

    // cout << "Enter number of rows: ";
    // cin >> rows;
    char out;

    for(int i = 1; i <= rows; ++i) {
        for(int j = 1; j <= i; ++j) {
            out = '*\n';
        }
    }
    return 0;
}