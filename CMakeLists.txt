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

set(CMAKE_CXX_FLAGS "-Wall -std=c++11 -Wl,--no-as-needed")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()

set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -g -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -g")

if(CMAKE_BUILD_BITS EQUAL 32)
  list(APPEND CXX_FLAGS "-m32")
endif()

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

set(BUILD_SHARED_LIBRARIES OFF)
set(CMAKE_FIND_LIBRARY_SUFFIXES ".a;.so") # prefer static library
set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "") # remove -rdynamic
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")
# set(CMAKE_EXE_LINKER_FLAGS "-static")
set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")

link_libraries(pthread)

include(ExternalProject)

################################################################################
# MySQL client library
################################################################################
find_package(MySQL REQUIRED)
if ( MYSQL_FOUND )
  include_directories( ${MYSQL_INCLUDE_DIRS} )
  # target_link_libraries( ranking ${MYSQL_LIBRARIES} )
endif( MYSQL_FOUND )

################################################################################
# zlib
################################################################################
find_package(ZLIB REQUIRED)
if ( ZLIB_FOUND )
  include_directories( ${ZLIB_INCLUDE_DIRS} )
  # target_link_libraries( ranking ${ZLIB_LIBRARIES} )
endif( ZLIB_FOUND )


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
  ExternalProject_Get_Property(googletest binary_dir)

  set(GTEST_INCLUDE_DIRS ${source_dir}/include)

  # Library
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


################################################################################
# gflags - https://github.com/gflags/gflags
################################################################################
set(gflags_RELEASE 2.1.2)
find_package(GFlags)
if (NOT GFLAGS_FOUND)
  message (STATUS " gflags library has not been found.")
  message (STATUS " gflags will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")

  ExternalProject_Add(
    gflags-${gflags_RELEASE}
    PREFIX ${CMAKE_CURRENT_BINARY_DIR}/gflags-${gflags_RELEASE}
    GIT_REPOSITORY https://github.com/gflags/gflags.git
    GIT_TAG v${gflags_RELEASE}
    CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DBUILD_gflags_nothreads_LIB=OFF -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    BUILD_COMMAND make
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    )

  ExternalProject_Get_Property(gflags-${gflags_RELEASE} binary_dir)
  ExternalProject_Get_Property(gflags-${gflags_RELEASE} source_dir)

  set(GFLAGS_INCLUDE_DIRS ${binary_dir}/include CACHE PATH "Local Gflags headers")
  set(GFLAGS_LIBRARY_PATH ${binary_dir}/lib )

  set(GFLAGS_BUILD_DIR ${binary_dir}) # to compile glog

  # import built library as a new one
  set(GFLAGS_LIBRARIES gflags)
  add_library(gflags UNKNOWN IMPORTED)
  set_target_properties(gflags PROPERTIES IMPORTED_LOCATION ${GFLAGS_LIBRARY_PATH}/libgflags.a)
  add_dependencies(gflags gflags-${gflags_RELEASE})

  # file(GLOB GFLAGS_SHARED_LIBRARIES "${binary_dir}/libgflags${CMAKE_SHARED_LIBRARY_SUFFIX}*")
  include_directories(${GFLAGS_INCLUDE_DIRS})
  link_directories(${GFLAGS_LIBRARY_PATH})
endif(NOT GFLAGS_FOUND)

# TODO find autoconf automake 1.14+ for glog build

################################################################################
# glog - https://github.com/google/glog
################################################################################
set(glog_RELEASE 0.3.4)
find_package(GLOG)
if (NOT GLOG_FOUND)
  message (STATUS " glog library has not been found")
  if(NOT GFLAGS_FOUND)
    message(STATUS " or it is likely not linked to gflags.")
  endif(NOT GFLAGS_FOUND)
  message (STATUS " it will be downloaded and built automatically when doing 'make'.")

  set(GLOG_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/glog-${glog_RELEASE})

  # default path
  set(GLOG_SOURCE_DIR ${GLOG_PREFIX}/src/glog-${glog_RELEASE})
  set(GLOG_BINARY_DIR ${GLOG_PREFIX}/src/glog-${glog_RELEASE}-build)

  set(GLOG_CONFIGURE ${GLOG_PREFIX}/configure_with_gflags)
  set(GLOG_CONFIGURE_TMP ${GLOG_PREFIX}/tmp/configure_with_gflags)

  set(GLOG_INSTALL_DIR ${GLOG_PREFIX}/install)

  file(WRITE ${GLOG_CONFIGURE_TMP}
    "#!/bin/sh
export CPPFLAGS=-I${GFLAGS_INCLUDE_DIRS}
export LDFLAGS=-L${GFLAGS_LIBRARY_PATH}
# export LIBS=-lgflags
${GLOG_SOURCE_DIR}/configure --with-gflags=${GFLAGS_BUILD_DIR} --prefix=${GLOG_INSTALL_DIR}
# workaround in centos 6.5
cd ${GLOG_SOURCE_DIR} && automake --add-missing
")

  # add execute permission
  file(COPY ${GLOG_CONFIGURE_TMP}
    DESTINATION ${GLOG_PREFIX}
    FILE_PERMISSIONS
    OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)

  ExternalProject_Add(
    glog-${glog_RELEASE}
    DEPENDS gflags
    PREFIX ${GLOG_PREFIX}
    GIT_REPOSITORY https://github.com/google/glog.git
    GIT_TAG v${glog_RELEASE}
    CONFIGURE_COMMAND ${GLOG_CONFIGURE}
    BUILD_COMMAND make
    INSTALL_DIR ${GLOG_INSTALL_DIR}
    INSTALL_COMMAND make install
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    )

  ExternalProject_Get_Property(glog-${glog_RELEASE} install_dir)
  # ExternalProject_Get_Property(glog-${glog_RELEASE} binary_dir)
  # ExternalProject_Get_Property(glog-${glog_RELEASE} source_dir)

  set(GLOG_INCLUDE_DIRS ${install_dir}/include)
  set(GLOG_LIBRARY_PATH ${install_dir}/lib )

  # WORKAROUND log_severity.h is missing
  # ExternalProject_Add_Step(
  #   glog-${glog_RELEASE} workaround
  #   COMMAND cp ${source_dir}/src/glog/log_severity.h ${GLOG_INCLUDE_DIRS}/glog
  #   DEPENDEES build
  #   )

  # import built library as a new one
  set(GLOG_LIBRARIES glog)
  add_library(glog UNKNOWN IMPORTED)
  set_target_properties(glog PROPERTIES IMPORTED_LOCATION ${GLOG_LIBRARY_PATH}/libglog.a)
  add_dependencies(glog glog-${glog_RELEASE})

  include_directories(${GLOG_INCLUDE_DIRS})
  link_directories(${GLOG_LIBRARY_PATH})

else(NOT GLOG_FOUND )
  add_library(glog-${glog_RELEASE} UNKNOWN IMPORTED)
  set_target_properties(glog-${glog_RELEASE} PROPERTIES IMPORTED_LOCATION "${GLOG_LIBRARIES}")
endif(NOT GLOG_FOUND )

# if(NOT ENABLE_LOG)
#   message(STATUS "Logging is not enabled")
#   add_definitions(-DGOOGLE_STRIP_LOG=1)
# endif(NOT ENABLE_LOG)


################################################################################
# mysqlcppconn - https://dev.mysql.com/downloads/connector/cpp/1.0.html
################################################################################
set(mysqlcppconn_RELEASE 1.1.6)
find_package(MySQLConnectorCpp)
if(NOT MYSQLCONNECTORCPP_FOUND)
  message (STATUS " mysql-connector c++ has not been found.")
  message (STATUS " it will be downloaded and built automatically when doing 'make'.")

  set(MYSQLCPPCONN_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/mysqlcppconn-${mysqlcppconn_RELEASE})

  ExternalProject_Add(
    MySQLConnectorCpp-${mysqlcppconn_RELEASE}
    PREFIX ${MYSQLCPPCONN_PREFIX}
    URL http://cdn.mysql.com/archives/mysql-connector-c++/mysql-connector-c++-${mysqlcppconn_RELEASE}.tar.gz
    # CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR>
    # BUILD_COMMAND make
    INSTALL_DIR ${MYSQLCPPCONN_PREFIX}/install
    INSTALL_COMMAND make install
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON
    )

  # Specify include dir
  ExternalProject_Get_Property(MySQLConnectorCpp-${mysqlcppconn_RELEASE} install_dir)
  ExternalProject_Get_Property(MySQLConnectorCpp-${mysqlcppconn_RELEASE} source_dir)
  # ExternalProject_Get_Property(MySQLConnectorCpp-${mysqlcppconn_RELEASE} binary_dir)

  set(MYSQLCONNECTORCPP_INCLUDE_DIRS ${install_dir}/include)
  set(MYSQLCONNECTORCPP_LIBRARY_PATH ${install_dir}/lib/x86_64-linux-gnu)

  ExternalProject_Add_Step(
    MySQLConnectorCpp-${mysqlcppconn_RELEASE} workaround
    COMMAND
    cp ${source_dir}/driver/mysql_public_iface.h ${MYSQLCONNECTORCPP_INCLUDE_DIRS}
    DEPENDEES install
    )


  set(MYSQLCONNECTORCPP_LIBRARIES mysqlcppconn)
  add_library(mysqlcppconn UNKNOWN IMPORTED)
  set_target_properties(mysqlcppconn PROPERTIES
    IMPORTED_LOCATION ${MYSQLCONNECTORCPP_LIBRARY_PATH}/libmysqlcppconn-static.a)
  add_dependencies(mysqlcppconn MySQLConnectorCpp)

  include_directories(${MYSQLCONNECTORCPP_INCLUDE_DIRS})
  link_directories(${MYSQLCONNECTORCPP_LIBRARY_PATH})

endif(NOT MYSQLCONNECTORCPP_FOUND)


################################################################################
# libmemcached - https://launchpad.net/libmemcached/+download
################################################################################
set(libmemcached_RELEASE 1.0.18)
find_package(Memcached)
if(NOT MEMCACHED_FOUND)
  message (STATUS " libmemcached has not been found.")
  message (STATUS " it will be downloaded and built automatically when doing 'make'.")

  set(LIBMCD_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/memcached-${libmemcached_RELEASE})
  set(LIBMCD_SOURCE_DIR ${LIBMCD_PREFIX}/src/Memcached-${libmemcached_RELEASE})
  set(LIBMCD_BUILD_DIR ${LIBMCD_PREFIX}/src/Memcached-${libmemcached_RELEASE}-build)

  set(LIBMCD_INSTALL_DIR ${LIBMCD_PREFIX}/install)

  set(LIBMCD_CONFIGURE ${LIBMCD_PREFIX}/configure_tmp)

  file(WRITE ${LIBMCD_CONFIGURE}
    "#!/bin/sh
${LIBMCD_SOURCE_DIR}/configure --disable-sasl --prefix=${LIBMCD_INSTALL_DIR}
# workaround in centos 6.5
#cd ${LIBMCD_SOURCE_DIR} && automake --add-missing
# workaround for sasl
cp ${LIBMCD_BUILD_DIR}/libmemcached-1.0/configure.h ${LIBMCD_SOURCE_DIR}/libmemcached-1.0/configure.h
")

  ExternalProject_Add(
    Memcached-${libmemcached_RELEASE}
    PREFIX ${LIBMCD_PREFIX}
    URL https://launchpadlibrarian.net/165454254/libmemcached-${libmemcached_RELEASE}.tar.gz
    # CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    CONFIGURE_COMMAND sh ${LIBMCD_CONFIGURE} --prefix=<INSTALL_DIR>
    BUILD_COMMAND make
    INSTALL_DIR ${LIBMCD_INSTALL_DIR}
    INSTALL_COMMAND make install
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON
    )

  # Specify include dir
  ExternalProject_Get_Property(Memcached-${libmemcached_RELEASE} install_dir)

  set(MEMCACHED_INCLUDE_DIRS ${install_dir}/include)
  set(MEMCACHED_LIBRARY_PATH ${install_dir}/lib)

  set(MEMCACHED_LIBRARIES libmemcached)
  add_library(libmemcached UNKNOWN IMPORTED)
  set_target_properties(libmemcached PROPERTIES
    IMPORTED_LOCATION ${MEMCACHED_LIBRARY_PATH}/libmemcached.a)
  add_dependencies(libmemcached Memcached)

  set(MEMCACHEDUTIL_LIBRARIES libmemcachedutil)
  add_library(libmemcachedutil UNKNOWN IMPORTED)
  set_target_properties(libmemcachedutil PROPERTIES
    IMPORTED_LOCATION ${MEMCACHED_LIBRARY_PATH}/libmemcachedutil.a)
  add_dependencies(libmemcachedutil Memcached)

  include_directories(${MEMCACHED_INCLUDE_DIRS})
  link_directories(${MEMCACHED_LIBRARY_PATH})

endif(NOT MEMCACHED_FOUND)


################################################################################
# pugixml - http://pugixml.org
################################################################################
set(pugixml_RELEASE 1.7)
find_package(PugiXML)
if (NOT PUGIXML_FOUND)
  message (STATUS " pugixml library has not been found.")
  message (STATUS " pugixml will be downloaded and built automatically ")
  message (STATUS " when doing 'make'. ")

  set(PUGIXML_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/pugixml-${pugixml_RELEASE})
  set(PUGIXML_SRC ${PUGIXML_PREFIX}/src/pugixml-${pugixml_RELEASE}/src)
  set(PUGIXML_MAKEFILE ${PUGIXML_PREFIX}/Makefile)
  set(PUGIXML_BUILD ${PUGIXML_PREFIX}/build.sh)

  file(WRITE ${PUGIXML_MAKEFILE}
    "libpugixml.a: pugixml.o
	ar rcs $@ $^")

  file(WRITE ${PUGIXML_BUILD}
    "cp ${PUGIXML_MAKEFILE} ${PUGIXML_SRC} && make -C ${PUGIXML_SRC}")

  ExternalProject_Add(
    pugixml-${pugixml_RELEASE}
    URL http://github.com/zeux/pugixml/releases/download/v${pugixml_RELEASE}/pugixml-${pugixml_RELEASE}.tar.gz
    # CMAKE_ARGS -DBUILD_SHARED_LIBS=ON -DBUILD_STATIC_LIBS=ON -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    PREFIX ${PUGIXML_PREFIX}
    CONFIGURE_COMMAND ""
    CMAKE_COMMAND ""
    BUILD_COMMAND sh ${PUGIXML_BUILD}
    INSTALL_COMMAND ""
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON
    )

  ExternalProject_Get_Property(pugixml-${pugixml_RELEASE} source_dir)

  set(PUGIXML_INCLUDE_DIRS ${source_dir}/src)
  set(PUGIXML_LIBRARY_PATH ${source_dir}/src)

  set(PUGIXML_BUILD_DIR ${binary_dir}) # to compile glog

  # import built library as a new one
  set(PUGIXML_LIBRARIES pugixml)
  add_library(pugixml UNKNOWN IMPORTED)
  set_target_properties(pugixml PROPERTIES IMPORTED_LOCATION ${PUGIXML_LIBRARY_PATH}/libpugixml.a)
  add_dependencies(pugixml pugixml-${pugixml_RELEASE})

  include_directories(${PUGIXML_INCLUDE_DIRS})
  link_directories(${PUGIXML_LIBRARY_PATH})
endif(NOT PUGIXML_FOUND)

add_subdirectory(svr)
add_subdirectory(http)
add_subdirectory(util)
add_subdirectory(ranking)
