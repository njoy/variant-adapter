add_executable( variant.test variant.test.cpp )
target_compile_options( variant.test PUBLIC "-std=c++14")
target_link_libraries(variant.test variant-adapter)
