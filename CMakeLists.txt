cmake_minimum_required( VERSION 3.2 ) 

project( variant-adapter LANGUAGES CXX )
get_directory_property( is_subproject PARENT_DIRECTORY )
include( CMakeDependentOption REQUIRED )

if ( NOT GIT_EXECUTABLE )
    find_package( Git )
    if ( NOT GIT_FOUND )
        message( FATAL_ERROR "git installation was not found." )
    endif()
endif()

execute_process(
    COMMAND ${GIT_EXECUTABLE} rev-parse --abbrev-ref HEAD
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_BRANCH
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
execute_process(
    COMMAND ${GIT_EXECUTABLE} rev-parse HEAD
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_HASH
    OUTPUT_STRIP_TRAILING_WHITESPACE
) 

message( STATUS "" )
message( STATUS "-----------------------------------------------------------" )
message( STATUS "" )
message( STATUS "variant-adapter" )
message( STATUS "Git current branch: ${GIT_BRANCH}" )
message( STATUS "Git commit hash: ${GIT_HASH}" )
message( STATUS "" )
message( STATUS "-----------------------------------------------------------" )

add_library( variant-adapter INTERFACE )
target_include_directories( variant-adapter INTERFACE . )
target_sources( variant-adapter INTERFACE
"${CMAKE_CURRENT_SOURCE_DIR}/src/include/mpark/config.hpp"
"${CMAKE_CURRENT_SOURCE_DIR}/src/include/mpark/in_place.hpp"
"${CMAKE_CURRENT_SOURCE_DIR}/src/include/mpark/lib.hpp"
"${CMAKE_CURRENT_SOURCE_DIR}/src/include/mpark/variant.hpp"
"${CMAKE_CURRENT_SOURCE_DIR}/variant")

# add_subdirectory(test)
