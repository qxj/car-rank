# - Try to find GFlags
#
# The following variables are optionally searched for defaults
# GFlags_ROOT_DIR: Base directory where all GFlags components are found
#
# The following are set after configuration is done:
# GFlags_FOUND
# GFlags_INCLUDE_DIRS
# GFlags_LIBS
# GFlags_LIBRARY_DIRS

# - Try to find GFlags
#
#
# The following are set after configuration is done:
# GFlags_FOUND
# GFlags_INCLUDE_DIRS
# GFlags_LIBS
# GFlags_LIBRARY_DIRS
cmake_minimum_required(VERSION 2.6)

if(APPLE)
     FIND_PATH(GFlags_ROOT_DIR
     libgflags.dylib
     PATHS
     /opt/local/lib
     /usr/local/lib
     )
else(APPLE)
     FIND_PATH(GFlags_ROOT_DIR
     libgflags.so
     HINTS
     /usr/local/lib
     /usr/lib/x86_64-linux-gnu
     /usr/lib/i386-linux-gnu
     /usr/lib/arm-linux-gnueabihf
     /usr/lib/arm-linux-gnueabi
     /usr/lib/aarch64-linux-gnu
     /usr/lib64
     /usr/lib
     )
endif(APPLE)

IF(GFlags_ROOT_DIR)
     # We are testing only a couple of files in the include directories
          FIND_PATH(GFlags_INCLUDE_DIRS
          gflags/gflags.h
          HINTS
          /opt/local/include
          /usr/local/include
          /usr/include
          ${GFlags_ROOT_DIR}/src
          )

     # Find the libraries
     SET(GFlags_LIBRARY_DIRS ${GFlags_ROOT_DIR})

     FIND_LIBRARY(GFlags_lib gflags ${GFlags_LIBRARY_DIRS})

     # set up include and link directory
     include_directories(${GFlags_INCLUDE_DIRS})
     link_directories(${GFlags_LIBRARY_DIRS})
     message(STATUS "gflags library found at ${GFlags_lib}")
     SET(GFlags_LIBS ${GFlags_lib})
     SET(GFlags_FOUND true)
     MARK_AS_ADVANCED(GFlags_INCLUDE_DIRS)
ELSE(GFlags_ROOT_DIR)
     MESSAGE(STATUS "Cannot find gflags")
     SET(GFlags_FOUND false)
ENDIF(GFlags_ROOT_DIR)

