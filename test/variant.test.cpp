#include <string>
#include <variant>

int main(){
  std::experimental::variant< int, std::string> vis;
  vis = 10;
  vis = "foo";
}
