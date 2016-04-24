project(ranking CXX)

########################################################################
# Project setup
########################################################################
if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
  message(WARNING "In-tree build is bad practice. Try 'cd build && cmake ../' ")
endif(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
cmake_minimum_required(VERSION 2.8)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/Modules)
file(RELATIVE_PATH RELATIVE_CMAKE_CALL ${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR})

################################################################################
# Checkout compiler version
################################################################################

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  if(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.7)
    message(STATUS "Your GCC version is too old and does not support some C++11 features required by GNSS-SDR. GCC version must be at least 4.7")
    if(${LINUX_DISTRIBUTION} MATCHES "Ubuntu")
      if(${LINUX_VER} MATCHES "12.04")
        message(STATUS "For instructions on how to upgrade GCC, check http://askubuntu.com/a/271561")
      endif(${LINUX_VER} MATCHES "12.04")
    endif(${LINUX_DISTRIBUTION} MATCHES "Ubuntu")
    message(FATAL_ERROR "Fatal error: GCC >= 4.7 required.")
  endif(CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.7)
endif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")

set(CMAKE_CXX_FLAGS "-Wall -std=c++11")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()

set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -g -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3")

if(CMAKE_BUILD_BITS EQUAL 32)
  list(APPEND CXX_FLAGS "-m32")
endif()

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

set(BUILD_SHARED_LIBRARIES OFF)
set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "") # remove -rdynamic
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")
# set(CMAKE_EXE_LINKER_FLAGS "-static")
# set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")

link_libraries(pthread)

include(ExternalProject)

################################################################################
# Boost - http://www.boost.org
################################################################################
if(UNIX AND EXISTS "/usr/lib64")
  list(APPEND BOOST_LIBRARYDIR "/usr/lib64") # Fedora 64-bit fix
endif(UNIX AND EXISTS "/usr/lib64")
if(GNURADIO_INSTALL_PREFIX)
  if(EXISTS "${GNURADIO_INSTALL_PREFIX}/lib/libboost_thread-mt.so")
    list(APPEND BOOST_LIBRARYDIR "${GNURADIO_INSTALL_PREFIX}/lib")     # Boost installed by PyBOMBS
    list(APPEND BOOST_INCLUDEDIR "${GNURADIO_INSTALL_PREFIX}/include") # Boost installed by PyBOMBS
  endif(EXISTS "${GNURADIO_INSTALL_PREFIX}/lib/libboost_thread-mt.so")
endif(GNURADIO_INSTALL_PREFIX)
set(Boost_ADDITIONAL_VERSIONS
  "1.45.0" "1.45" "1.46.0" "1.46"                 "1.48.0" "1.48" "1.49.0" "1.49"
  "1.50.0" "1.50" "1.51.0" "1.51"                 "1.53.0" "1.53" "1.54.0" "1.54"
  "1.55.0" "1.55" "1.56.0" "1.56" "1.57.0" "1.57" "1.58.0" "1.58" "1.59.0" "1.59"
  "1.60.0" "1.60" "1.61.0" "1.61" "1.62.0" "1.62" "1.63.0" "1.63" "1.64.0" "1.64"
  "1.65.0" "1.65" "1.66.0" "1.66" "1.67.0" "1.67" "1.68.0" "1.68" "1.69.0" "1.69"
  )
set(Boost_USE_MULTITHREAD ON)
# set(Boost_USE_STATIC_LIBS OFF)
set(Boost_USE_STATIC_LIBS ON)
# find_package(Boost COMPONENTS date_time system filesystem thread serialization chrono REQUIRED)
find_package(Boost COMPONENTS system thread  chrono REQUIRED)
if(NOT Boost_FOUND)
  message(FATAL_ERROR "Fatal error: Boost (version >=1.45.0) required.")
endif(NOT Boost_FOUND)

# find_package(Boost REQUIRED)
# include_directories(${Boost_INCLUDE_DIRS})

################################################################################
# Googletest - https://github.com/google/googletest
################################################################################
enable_testing()

set(gtest_RELEASE 1.7.0)
find_package(GTest)
if(NOT GTest_FOUND)
  message (STATUS " Googletest has not been found.")
  message (STATUS " Googletest will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")

  # http://stackoverflow.com/questions/9689183/cmake-googletest
  ExternalProject_Add(
    googletest
    URL http://googletest.googlecode.com/files/gtest-${gtest_RELEASE}.zip
    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/gtest-${gtest_RELEASE}
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/gtest/gtest-${gtest_RELEASE}
    # TIMEOUT 10
    # # Force separate output paths for debug and release builds to allow easy
    # # identification of correct lib in subsequent TARGET_LINK_LIBRARIES commands
    # CMAKE_ARGS -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG:PATH=DebugLibs
    #            -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE:PATH=ReleaseLibs
    #            -Dgtest_force_shared_crt=ON
    # Disable install step
    INSTALL_COMMAND ""
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON)

  # Specify include dir
  ExternalProject_Get_Property(googletest source_dir)
  set(GTEST_INCLUDE_DIRS ${source_dir}/include)

  # Library
  ExternalProject_Get_Property(googletest binary_dir)
  set(GTEST_LIBRARY gtest)
  add_library(${GTEST_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GTEST_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${binary_dir}/libgtest.a)
  add_dependencies(${GTEST_LIBRARY} googletest)
  # Libray gtest_main
  set(GTEST_MAIN_LIBRARY gtest_main)
  add_library(${GTEST_MAIN_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GTEST_MAIN_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${binary_dir}/libgtest_main.a)
  add_dependencies(${GTEST_MAIN_LIBRARY} googletest)

endif(NOT GTest_FOUND)


# enable_testing()
# find_package(GTest REQUIRED)
# include_directories(${GTEST_INCLUDE_DIRS})


################################################################################
# gflags - https://github.com/gflags/gflags
################################################################################
set(LOCAL_GFLAGS false)
set(gflags_RELEASE 2.1.2)
find_package(GFlags)
if (NOT GFlags_FOUND)
  message (STATUS " gflags library has not been found.")
  message (STATUS " gflags will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")

  ExternalProject_Add(
    gflags-${gflags_RELEASE}
    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}
    GIT_REPOSITORY https://github.com/gflags/gflags.git
    GIT_TAG v${gflags_RELEASE}
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/gflags/gflags-${gflags_RELEASE}
    BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}
    CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DBUILD_gflags_nothreads_LIB=OFF -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    BUILD_COMMAND make
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    )

  set(GFlags_INCLUDE_DIRS
    ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/include CACHE PATH "Local Gflags headers"
    )

  add_library(gflags UNKNOWN IMPORTED)
  set_property(TARGET gflags PROPERTY IMPORTED_LOCATION ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gflags.a)
  add_dependencies(gflags gflags-${gflags_RELEASE})
  set(GFlags_LIBS gflags)
  file(GLOB GFlags_SHARED_LIBS "${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gflags${CMAKE_SHARED_LIBRARY_SUFFIX}*")
  set(GFlags_LIBRARY gflags-${gflags_RELEASE})
  set(GFlags_LIBRARY_PATH ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib )
  link_directories(${GFlags_LIBRARY_PATH})
  set(GFlags_lib ${GFlags_LIBS} CACHE FILEPATH "Local Gflags library")
  set(GFlags_LIBRARY_PATH ${GFlags_LIBS})
  set(LOCAL_GFLAGS true CACHE STRING "GFlags downloaded and built automatically" FORCE)
endif(NOT GFlags_FOUND)

################################################################################
# glog - https://github.com/google/glog
################################################################################
find_package(GLOG)
if(GLOG_INCLUDE_DIRS)
  set(GLOG_FOUND ON)
endif(GLOG_INCLUDE_DIRS)
set(glog_RELEASE 0.3.4)
if (NOT GLOG_FOUND OR ${LOCAL_GFLAGS})
  message (STATUS " glog library has not been found")
  if(NOT GFlags_FOUND)
    message(STATUS " or it is likely not linked to gflags.")
  endif(NOT GFlags_FOUND)
  message (STATUS " glog will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")
  if(NOT ${LOCAL_GFLAGS})
    add_library(gflags-${gflags_RELEASE} UNKNOWN IMPORTED)
    set_property(TARGET gflags-${gflags_RELEASE} PROPERTY IMPORTED_LOCATION "${GFlags_LIBS}")
  endif(NOT ${LOCAL_GFLAGS})

  if(${LOCAL_GFLAGS})
    set(TARGET_GFLAGS ${gflags})
    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
      file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        "#!/bin/sh
export CPPFLAGS=-I${GFlags_INCLUDE_DIRS}
export LDFLAGS=-L${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib
export LIBS=${GFlags_SHARED_LIBS}
export CXXFLAGS=\"-stdlib=libc++\"
export CC=clang
export CXX=clang++
${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}/configure")
      file(COPY ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
        FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ
        GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
    else("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
      file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        "#!/bin/sh
export CPPFLAGS=-I${GFlags_INCLUDE_DIRS}
export LDFLAGS=-L${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib
export LIBS=${GFlags_SHARED_LIBS}
${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}/configure")
      file(COPY ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
        FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ
        GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
    endif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")

  else(${LOCAL_GFLAGS})
    set(TARGET_GFLAGS gflags-${gflags_RELEASE})
    if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
      file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        "#!/bin/sh
export CPPFLAGS=-I${GFlags_INCLUDE_DIRS}
export LDFLAGS=-L${GFlags_LIBRARY_DIRS}
export LIBS=\"${GFlags_LIBS} -lc++\"
export CXXFLAGS=\"-stdlib=libc++\"
export CC=clang
export CXX=clang++
${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}/configure")
      file(COPY ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
        FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ
        GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
    else("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
      file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        "#!/bin/sh
export CPPFLAGS=-I${GFlags_INCLUDE_DIRS}
export LDFLAGS=-L${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}/lib
export LIBS=${GFlags_SHARED_LIBS}
${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}/configure")
      file(COPY ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/tmp/configure_with_gflags
        DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
        FILE_PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ
        GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
    endif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  endif(${LOCAL_GFLAGS})

  set(GLOG_CONFIGURE ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/configure_with_gflags)

  ExternalProject_Add(
    glog-${glog_RELEASE}
    DEPENDS ${TARGET_GFLAGS}
    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
    GIT_REPOSITORY https://github.com/google/glog.git
    GIT_TAG v${glog_RELEASE}
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}
    BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}
    CONFIGURE_COMMAND ${GLOG_CONFIGURE} --prefix=<INSTALL_DIR>
    BUILD_COMMAND make
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    )

  # Set up variables
  set(GLOG_INCLUDE_DIRS
    ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/glog/glog-${glog_RELEASE}/src/
    ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/src
    )
  set(GLOG_LIBRARIES
    ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE}/.libs/${CMAKE_FIND_LIBRARY_PREFIXES}glog.a
    )
  set(LOCAL_GLOG true CACHE STRING "Glog downloaded and built automatically" FORCE)
else(NOT GLOG_FOUND OR ${LOCAL_GFLAGS})
  add_library(glog-${glog_RELEASE} UNKNOWN IMPORTED)
  set_property(TARGET glog-${glog_RELEASE} PROPERTY IMPORTED_LOCATION "${GLOG_LIBRARIES}")
endif(NOT GLOG_FOUND OR ${LOCAL_GFLAGS})

if(NOT ENABLE_LOG)
  message(STATUS "Logging is not enabled")
  add_definitions(-DGOOGLE_STRIP_LOG=1)
endif(NOT ENABLE_LOG)


# enable_testing()
# add_subdirectory(thirdparty/gtest-1.6.0)
# include_directories(${gtest_SOURCE_DIR}/include ${gtest_SOURCE_DIR})


################################################################################
# mysqlcppconn - https://dev.mysql.com/downloads/connector/cpp/1.0.html
################################################################################
set(mysqlcppconn_RELEASE 1.1.7)
find_package(MySQLConnectorCpp)
if(NOT MYSQLCONNECTORCPP_FOUND)
  message (STATUS " MYSQL-CONNECTOR-CPP has not been found.")
  message (STATUS " MYSQL-CONNECTOR-CPP will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")

  ExternalProject_Add(
    MySQLConnectorCpp
    URL http://cdn.mysql.com//Downloads/Connector-C++/mysql-connector-c++-${mysqlcppconn_RELEASE}.tar.gz
    SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/mysqlcppconn/mysqlcppconn-${mysqlcppconn_RELEASE}
    BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/mysqlcppconn-${mysqlcppconn_RELEASE}
    CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    BUILD_COMMAND make
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON)

  # Specify include dir
  ExternalProject_Get_Property(MySQLConnectorCpp source_dir)
  set(MYSQLCONNECTORCPP_INCLUDE_DIRS ${source_dir}/include)

  # Library
  ExternalProject_Get_Property(MySQLConnectorCpp binary_dir)
  set(MYSQLCONNECTORCPP_LIBRARY mysqlcppconn)
  add_library(${MYSQLCONNECTORCPP_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${MYSQLCONNECTORCPP_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${binary_dir}/libmysqlcppconn.a)
  add_dependencies(${MYSQLCONNECTORCPP_LIBRARY} MySQLConnectorCpp)

  set(MYSQLCONNECTORCPP_LIBRARIES ${MYSQLCONNECTORCPP_LIBRARY})

endif(NOT MYSQLCONNECTORCPP_FOUND)


add_subdirectory(svr)
add_subdirectory(http)
add_subdirectory(ranking)
